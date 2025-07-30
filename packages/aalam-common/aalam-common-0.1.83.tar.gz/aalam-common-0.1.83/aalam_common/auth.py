# coding=utf8
from base64 import b64decode
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA, SHA256
from collections import OrderedDict
from datetime import datetime
from ecdsa import VerifyingKey
from ecdsa.util import sigdecode_der
import sys
if sys.version_info[0] == 3:
    import urllib.parse as urllib_parse
else:
    import urllib as urllib_parse

import binascii
import os
import time
import logging
import webob.exc
import aalam_common.wsgi as wsgi
import aalam_common.utils as zutils
from aalam_common.config import cfg


AUTH_COOKIE_NAME = "auth"  # This is the cookie set by central auth server
CUSTOMER_AUTH_COOKIE_NAME = "cauth"
CUSTOMER_AUTH_CURRENT_ID_COOKIE_NAME = "cid"
ANONYMOUS_USERNAME = "Anonymous"
ANONYMOUS_EMAIL = "anonymous"
customer_auth_pubkey = os.path.join(
    os.path.dirname(getattr(cfg.CONF, "pubkey", "/config/keys")),
    "customer_auth.pub.pem")

# a simple key cache to hold the keys so that we don't
# stress the file system
class KeyCache(object):
    def __init__(self, size):
        self._cache_size = size
        self._cache = OrderedDict()

    def get(self, filename):
        if filename not in self._cache:
            with open(filename, "r") as fd:
                self._cache[filename] = fd.read()

        self._cache.move_to_end(filename)
        if len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)
        return self._cache[filename]

    def remove(self, filename):
        if filename in self._cache:
            del self._cache[filename]


key_cache = KeyCache(32)  # a typical key file is 271 bytes


class HTTPAuthenticationFailed(webob.exc.HTTPUnauthorized):
    path = os.path.join(os.path.dirname(__file__), "error-unauthorized.html")
    if os.path.exists(path):
        with open(path, "r") as fd:
            body_template_obj = webob.exc.Template(fd.read())
    def __init__(self, host):
        super(HTTPAuthenticationFailed, self).__init__()
        biz_code = getattr(cfg.CONF, "bizcode", None)
        domain = None
        if not biz_code:
            # could be in other admin servers
            if cfg.CONF.app_provider_code == 'aalam':
                biz_code = 'accounts' if cfg.CONF.app_code == 'central' else cfg.CONF.app_code

        super(HTTPAuthenticationFailed, self).delete_cookie(
            AUTH_COOKIE_NAME, domain=host.replace(biz_code, ""))


class Auth(wsgi.Middleware):
    def __init__(self, app):
        super(Auth, self).__init__(app)

    def __verify_rsa(self, key_file, message, signature):
        pub_key = RSA.importKey(key_cache.get(key_file))
        auth_signer = PKCS1_PSS.new(pub_key)
        enc_msg = message.encode('utf-8')
        h = SHA.new()
        h.update(enc_msg)
        signature = b64decode(signature)

        def h256():
            ret = SHA256.new()
            ret.update(enc_msg)
            return ret

        # first verify is for legacy
        return auth_signer.verify(h, signature) or auth_signer.verify(h256(), signature)

    def _handle_token_auth(self, request):
        token = request.headers.get("X-Auth-Token", None)
        if not token:
            return

        try:
            (message, signature) = token.split(";")
        except ValueError:
            raise webob.exc.HTTPUnauthorized()

        (remote_id, _, exp_time) = message.split("#")

        pub_key_file = os.path.join(
            cfg.CONF.auth.userkeys_path,
            "remote-%s.pub" % remote_id)
        if not os.path.exists(pub_key_file):
            raise webob.exc.HTTPUnauthorized()

        if not self.__verify_rsa(pub_key_file, message, signature):
            return webob.exc.HTTPUnauthorized()

        if exp_time:
            expiry = datetime.fromtimestamp(float(exp_time))
            if expiry < zutils.datetime.utcnow():
                logging.warn(
                    "Got an expired token for app %s" % remote_id)
                raise webob.exc.HTTPUnauthorized()

        request.auth = {
            'email_id': "%s@." % remote_id,
            'remote_id': remote_id
        }
        return True

    def _verify_signature(self, key_file, header_value, request):
        (prefix, signature) = header_value.split(";")
        params = request.params
        path = urllib_parse.unquote(request.path)
        if params:
            params = '&'.join(
                ["=".join([k, v]) for k, v in params.items()])
            url = path + "?" + params
        else:
            url = path
        message = "#".join([prefix, url])
        return self.__verify_rsa(key_file, message, signature), prefix

    def _validate_user_signature(self, path, val, ts, signature, host, retry=False):
        ret = False
        try:
            vk = VerifyingKey.from_pem(key_cache.get(path))
            cookie_val_b = binascii.a2b_base64(signature)
            message = "#".join([val, ts])
            if (vk.verify(cookie_val_b, message.encode('utf-8'),
                          sigdecode=sigdecode_der)):
                ret = True
        except Exception:
            pass

        if not ret and retry:
            key_cache.remove(path)
            st = os.stat(path)
            if (time.time() - st.st_mtime) > (5*60):  # more than 5 minutes
                unq_val = urllib_parse.unquote(val)
                self._fetch_user_keys(unq_val)
                ret = self._validate_user_signature(path, val, ts, signature, host)

        if ret:
            return ret

        raise HTTPAuthenticationFailed(host)

    def _fetch_user_keys(self, val):
        payload = {}
        if '@' in val:
            payload['email_id'] = val
        else:
            payload['mobile'] = val
        resp = zutils.request_local_server(
            "POST", "/aalam/base/central/userkey", params=payload)
        if resp.status_code != 200:
            return False

        return True

    def _handle_cookie_auth(self, request):
        auth_cookie = request.cookies.pop(AUTH_COOKIE_NAME, None)
        cauth_cookie = request.cookies.pop(CUSTOMER_AUTH_COOKIE_NAME, None)
        if auth_cookie:
            val, ts, signature = auth_cookie.split('#', 2)
            unq_val = urllib_parse.unquote(val)
            path = os.path.join(cfg.CONF.auth.userkeys_path,
                                "%s.pub" % unq_val)
            if not os.path.exists(path):
                if not self._fetch_user_keys(unq_val):
                    raise webob.exc.HTTPUnauthorized()

            if self._validate_user_signature(path, val,
                                             ts, signature, request.host, retry=True):

                request.auth = {"email_id": unq_val} if '@' in unq_val \
                    else {'mobile': unq_val}
                request.auth['user'] = True
                return True

        if cauth_cookie:
            (contact_id, random, signature) = cauth_cookie.split("#", 2)
            message = "#".join([contact_id, random])
            if not self.__verify_rsa(customer_auth_pubkey, message, signature):
                return
            else:
                ids = []
                if ":" in contact_id:
                    ids = contact_id.split(":")
                    curr_id = request.cookies.pop(
                        CUSTOMER_AUTH_CURRENT_ID_COOKIE_NAME, None)
                    contact_id = ids[0] if (
                        not curr_id or curr_id not in ids) else curr_id
                request.auth = {'customer_id': contact_id, 'other_ids': ids}
                return True

        return False

    def _handle_internal_auth(self, request):
        internal = request.headers.get("X-Auth-Internal", None)
        if internal:
            (prefix, signature) = internal.split(";")
            p = prefix.split("/")
            pubkey = os.path.join(
                os.path.dirname(cfg.CONF.pubkey),
                "%s_%s.pub" % (p[0], p[1]))
            (ret, prefix) = self._verify_signature(
                pubkey, internal, request)
            if not ret:
                raise webob.exc.HTTPUnauthorized()

            request.auth = {'internal': True,
                            'from': prefix}

            if len(p) > 2:
                val = p[2]
            else:
                val = get_app_email(p[0], p[1])

            if '@' in val:
                request.auth['email_id'] = val
            else:
                request.auth['mobile'] = val

            return True

        return False

    def _handle_external_auth(self, request):
        signature = request.headers.get('X-Auth-Signature', None)
        if signature:
            prefix = signature[:signature.index(';')]
            ret = False
            if prefix == 'CENTRALPORTAL':
                (ret, _) = self._verify_signature(
                    cfg.CONF.auth.central_pubkey, signature, request)
            elif prefix.startswith('APPSPORTAL'):
                (ret, _) = self._verify_signature(
                    cfg.CONF.auth.apps_server_pubkey, signature, request)
            elif prefix.startswith('BILLINGPORTAL'):
                (ret, _) = self._verify_signature(
                    cfg.CONF.auth.billing_pubkey, signature, request)

            if not ret:
                raise webob.exc.HTTPUnauthorized()

            request.auth = {'external': True}
            if "/" in prefix:
                prefix, val = prefix.split("/")
                params = {'fields': 'id'}
                if '@' in val:
                    params['email'] = val
                else:
                    params['mobile'] = val
                resp = zutils.request_local_server(
                    "GET",
                    "/aalam/base/users",
                    params=params)
                if resp.status_code != 200:
                    raise webob.exc.HTTPUnauthorized()
                data = resp.json()
                user_id = data[0] if data else None

                if '@' in val:
                    request.auth['email_id'] = val
                else:
                    request.auth['mobile'] = val

                request.auth['id'] = user_id

            request.auth['from'] = prefix
            return True

        return False

    def _handle_anonymous(self, request):
        # allow anonymous users, role module will manage it
        request.auth = {"email_id": ANONYMOUS_EMAIL}
        return None

    def pre(self, request):
        if self._handle_token_auth(request):
            pass
        elif self._handle_cookie_auth(request):
            pass
        elif self._handle_internal_auth(request):
            pass
        elif self._handle_external_auth(request):
            pass
        else:
            self._handle_anonymous(request)

        return None


class TestAuth(wsgi.Middleware):
    # This is used just for testing
    def pre(self, request):
        request.auth = {'email_id': 'user@test.test',
                        "internal": True,
                        "from": "aalam/xxxx"}


is_anonymous_user = lambda request: not request.auth or (request.auth.get(
    "email_id", None) == ANONYMOUS_EMAIL) or is_auth_customer(request)


def deny_anonymous_user(request):
    if is_anonymous_user(request):
        raise webob.exc.HTTPForbidden(
            explanation="Forbidden for anonymous users")


def get_auth_user_id(request, deny_anon=True):
    auth = request.auth if hasattr(request, "auth") else None
    if is_anonymous_user(request) and deny_anon:
        raise webob.exc.HTTPForbidden(
            explanation="Forbidden for anonymous users")

    if is_anonymous_user(request):
        return (None, ANONYMOUS_EMAIL)

    id = None
    val = auth['email_id'] if 'email_id' in auth else auth.get('mobile', None)

    if 'id' in auth:
        id = auth['id']

    return (id, val)


def get_auth_user(request, deny_anon=True):
    (_, val) = get_auth_user_id(request, deny_anon=deny_anon)
    return val


def is_auth_internal(request):
    auth = request.auth if hasattr(request, "auth") else None
    if auth:
        if auth.get("internal", False):
            return auth.get("from")

    return False


def is_auth_customer(request):
    auth = request.auth if hasattr(request, "auth") else None
    if auth:
        return auth.get("customer_id", False)

    return False


def is_auth_external(request):
    auth = request.auth if hasattr(request, "auth") else None
    if auth:
        if auth.get("external", False):
            return auth.get("from")

    return False


def is_auth_remote(request):
    auth = request.auth if hasattr(request, 'auth') else None
    if auth and auth.get('remote_id'):
        return auth['remote_id']

    return False


def deny_external_source(request):
    if not is_auth_internal:
        raise webob.exc.HTTPNotFound()


def get_app_email(provider_code, app_code):
    return '_'.join([provider_code, app_code]) + "@%s" % cfg.CONF.hostname


def init_auth():
    pass
