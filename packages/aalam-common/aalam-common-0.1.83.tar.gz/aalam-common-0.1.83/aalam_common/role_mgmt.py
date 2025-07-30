# coding=utf8
import logging
import os
import webob
import six
import yaml
import aalam_common.auth as zauth
import aalam_common.exceptions as zexc
from aalam_common.redisdb import redis_conn, baseapp_redisify_name
import aalam_common.utils as zutils
import aalam_common.wsgi as wsgi
from aalam_common.config import cfg


yaml_dict = {}


# Following are permission map rules
# all:
#    Need all permissions to access the url
# any:
#    Need atleast one of permissions to access the url
# deny_anon:
#    Cannot be accessed by anonymous users
# deny_ext:
#    Allowed only from the apps running internally
# deny_exc(provide/app,...):
#    Deny all except the apps in the args


class Permissions(object):
    ALL_APPS = "all_apps"
    ALL_REMOTE = "all_remote"

    def __init__(self, condition=None, permissions=[]):
        self.condition = condition
        self.permissions = permissions
        self._allow_apps = []
        self._deny_anon = False
        self._deny_ext = False
        self._deny_exc = []

    def __call__(self):
        # This is important, otherwise python-routes
        # will put this object as unicode in its route args
        pass

    @staticmethod
    def all(*args):
        return Permissions("all", args)

    @staticmethod
    def any(*args):
        return Permissions("any", args)

    def deny_anon(self):
        self._deny_anon = True
        return self

    def deny_ext(self):
        self._deny_ext = True
        return self

    def deny_exc(self, *args):
        self._deny_exc = args
        return self

    def allow_apps(self, *args):
        self._allow_apps = args
        return self

    def check(self, request):
        if self._deny_anon and zauth.is_anonymous_user(request):
            raise webob.exc.HTTPForbidden()

        if self._deny_ext and request.auth.get("external", None):
            raise webob.exc.HTTPForbidden()

        if self._deny_exc:
            if Permissions.ALL_REMOTE in self._deny_exc and \
                not request.auth.get('remote_id', None):
                raise webob.exc.HTTPForbidden()

            if not request.auth.get("internal", None):
                raise webob.exc.HTTPForbidden()

            if Permissions.ALL_APPS not in self._deny_exc and \
                    request.auth.get("from", None) not in self._deny_exc:
                raise webob.exc.HTTPForbidden()
            else:
                # We don't need the permissions because we are allowed by
                # choice of the app
                return

        if self._allow_apps:
            if Permissions.ALL_APPS in self._allow_apps or \
                    request.auth.get("from", None) in self._allow_apps:
                return

        suser_perms = set(request.user_perms)
        found = False
        for p in self.permissions:
            perm_fq = frame_permission(cfg.CONF.app_provider_code,
                                       cfg.CONF.app_code,
                                       *p.split('/'))
            id = RoleCache.get(perm_fq)
            if id not in suser_perms and self.condition == 'all':
                msg = "You do not have enough permissions"
                raise webob.exc.HTTPForbidden(explanation=msg)
            elif id in suser_perms and self.condition == 'any':
                # atlest one is there, break now
                found = True
                break

        if self.condition == "any" and not found:
            raise webob.exc.HTTPForbidden()


def parse_yaml_dict(permissions_map):
    if not os.path.exists(permissions_map):
        yaml_dict = {}
        return yaml_dict

    with open(permissions_map, "r") as stream:
        yaml_dict = yaml.load(stream)
    return yaml_dict


def get_yaml_dict(permissions_map):
    global yaml_dict
    if yaml_dict:
        return yaml_dict

    yaml_dict = parse_yaml_dict(permissions_map)
    return yaml_dict


def get_permission_groups(permissions_map):
    if not os.path.exists(permissions_map):
        return []

    with open(permissions_map, "r") as stream:
        yaml_dict = yaml.load(stream)

    return [group for group, _ in yaml_dict['permission-groups'].items()]


def frame_permission(provider, app, perm_group, perm):
    return "/".join([provider, app, perm_group, perm])


def break_permission(permission):
    try:
        (provider, app, perm_group, perm) = permission.split("/")
        return (provider, app, perm_group, perm)
    except ValueError:
        raise zexc.InvalidPermissionFormat()


class RoleCache(object):
    _cache = {}

    @staticmethod
    def get(permission):
        (provider, app, grp, perm) = break_permission(permission)
        value = RoleCache._cache.get(permission, None)
        if value:
            return value

        logging.info("Caching permissions of group %s" % grp)
        # the cache needs to be updated
        resp = zutils.request_local_server(
            "GET", "/aalam/base/permissions/%s/%s/%s" % (provider, app, grp))
        if resp.status_code == 404:
            logging.error("Unable to find permission group")
            return None

        if resp.status_code != 200:
            logging.error("Unable to get permissions for group %s, because %s"
                          % (grp, resp.text))
            raise zexc.UnableToUpdateRoleCache(grp, resp.status_code,
                                               resp.text)

        data = resp.json()
        ret_value = None
        for perm_obj in data:
            fq_permission = frame_permission(
                provider, app, grp, perm_obj['name'])
            RoleCache._cache[fq_permission] = perm_obj['id']
            if fq_permission == permission:
                ret_value = perm_obj['id']

        return ret_value


def is_user_admin(inp):
    if inp is None:
        return False

    is_str = isinstance(inp, six.string_types) or \
        isinstance(inp, six.text_type)
    if is_str:
        user_val = inp
    elif isinstance(inp, wsgi.AALAMRequest):
        (_, user_val) = zauth.get_auth_user_id(inp, deny_anon=False)

    return user_val in zutils.get_common_rkey('adminusers', 'smembers')


class RolesMgmt(wsgi.Middleware):
    def __init__(self, app):
        self.ydict = get_yaml_dict(cfg.CONF.permissions_map)
        super(RolesMgmt, self).__init__(app)

    def pre(self, request):
        (_, user_val) = zauth.get_auth_user_id(request, deny_anon=False)
        if user_val and is_user_admin(user_val) or not user_val:
            return
        from_internal = zauth.is_auth_internal(request)
        if from_internal and from_internal == "aalam/base":
            # permit all base requests
            return

        route = request.environ['wsgiorg.routing_args'][1]
        url_perms = route.get('permissions', None)

        user_perms = []
        if user_val:
            rkey = baseapp_redisify_name("permissions-%s" % user_val)
            user_perms = zutils.get_common_rkey(rkey, 'smembers')
            if not user_perms:
                logging.info("Permissions for %s is not cached yet" % user_val)
                resp = zutils.request_local_server(
                    "POST",
                    "/aalam/base/permissions/cache/%s"
                    % user_val)
                if resp.status_code not in [200, 404]:
                    logging.error("Unable to cache the user information")
                    raise webob.exc.HTTPInternalServerError()
                user_perms = zutils.get_common_rkey(rkey, 'smembers')

        user_perms = [int(x) for x in user_perms]
        if not user_perms and not from_internal:
            # This should be a valid user account but has not permissions
            # configured in this account
            request.auth = {}
        request.user_perms = user_perms

        if url_perms is None:
            # permission not configured for this method
            return None

        url_perms.check(request)


def get_id_from_rolecache(permission):
    import webob
    try:
        perm_id = RoleCache.get(permission)
        if perm_id is None:
            msg = "Permission(%s) not found" % permission
            raise webob.exc.HTTPNotFound(explanation=msg)
    except zexc.UnableToUpdateRoleCache:
        raise webob.exc.HTTPInternalServerError()
    except zexc.InvalidPermissionFormat:
        msg = "Permission(%s) is not formatted properly" % permission
        raise webob.exc.HTTPBadRequest(explanation=msg)

    return perm_id


def get_id(grp, name):
    permission = frame_permission(
        cfg.CONF.app_provider_code, cfg.CONF.app_code, grp, name)
    return get_id_from_rolecache(permission)


def is_client_authorized(request, grp, name):
    if request.user_perms:
        return get_id(grp, name) in request.user_perms
    else:
        return False
