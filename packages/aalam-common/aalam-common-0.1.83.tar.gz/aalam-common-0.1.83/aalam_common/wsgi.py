# coding=utf8
import copy
import datetime as dt
from decimal import Decimal
import eventlet
eventlet.monkey_patch()
import eventlet.wsgi
from htmlmin.decorator import htmlmin
import importlib
import json
import os
import os.path
import socket
import sys
import six
import string
# from threading import Timer
import mimetypes
if sys.version_info[0] == 3:
    import urllib.parse as urllib_parse
else:
    import urllib as urllib_parse

import paste.deploy
import grp
import routes
import routes.middleware
import stat
import sqlalchemy
import webob
import webob.dec
import aalam_common as zc
import aalam_common.sqa as zsqa
from aalam_common.debug import logging
import aalam_common.exceptions as zexc
from aalam_common.utils import datetime, date, report_bug
from aalam_common import debug
from aalam_common.config import cfg

WSGI_SOCKET_ROOT = "/tmp"
MIGRATE_LOCK = ".migrate.lock"
CLEANUP_WAIT_PERIOD = 180  # 3 minutes
wsgi_listener = None
app_callbacks = {}


class AALAMRequest(webob.Request):
    def __repr__(self):
        return "AALAMRequest at %x" % id(self)

    def _filterout_system_params(self):
        if '_is_nohook' not in self.environ['webob.adhoc_attrs']:
            _g = self.GET
            _p = self.POST
            self.environ['webob.adhoc_attrs']['_is_nohook'] = False
            if 'nohook' in _g:
               self.environ['webob.adhoc_attrs']['_is_nohook'] = True
            if 'nohook' in _p:
               self.environ['webob.adhoc_attrs']['_is_nohook'] = True
            _g.pop('nohook', None)
            self.params = webob.multidict.NestedMultiDict(_g, _p)

    @property
    def is_nohook(self):
        self._filterout_system_params()
        return self.environ['webob.adhoc_attrs'].get('_is_nohook', False)

    @property
    def params(self):
        if self._params is None:
            self._filterout_system_params()
        return self._params

    @params.setter
    def params(self, value):
        self.environ['webob.adhoc_attrs']['_params'] = value

    def __getattr__(self, name):
        try:
            return super(AALAMRequest, self).__getattr__(name)
        except AttributeError:
            if name == "sqa_session":
                route_args = self.environ['wsgiorg.routing_args'][1]
                database = route_args.get("database", zsqa.get_database_name())
                if not database:
                    logging.error("'database' routing args not present")
                    raise zexc.ExpectedRouteArgs("database")
                self.sqa_session = retval = zsqa.Session(database)
                return retval


def cleanup():
    logging.warn("Cleanup invoked")
    try:
        if zc.CALLBACK_CLEANUP in app_callbacks:
            app_callbacks[zc.CALLBACK_CLEANUP]()
    except Exception:
        pass
    logging.warn("Killing the wsgi server")

    def terminate_now():
        sys.exit(100)

    def terminate_delayed():
        eventlet.sleep(1)
        #Not killing from the thread to honour its response
        wsgi_listener.kill()
        logging.warn("Terminating after a delay of %s seconds"
                     % CLEANUP_WAIT_PERIOD)
        eventlet.sleep(CLEANUP_WAIT_PERIOD)
        logging.warn("Terminator woke up, exiting now")
        terminate_now()

    eventlet.spawn_n(terminate_delayed)
    # Timer(CLEANUP_WAIT_PERIOD, terminate_now, ()).start()


class UnixDomainHttpProtocol3(eventlet.wsgi.HttpProtocol):
    def __init__(self, conn_state, server):
        client_address = conn_state[0]
        if client_address == '':
            client_address = ('<local>', 0)
            conn_state = (client_address, *conn_state[1:])
        # base class is old-style, no super does not work properly
        eventlet.wsgi.HttpProtocol.__init__(self, conn_state,
                                            server)
    def get_environ(self):
        env = super(UnixDomainHttpProtocol3, self).get_environ()
        # without this, any unicode character passed to the url path is
        # throws an error
        env['PATH_INFO'] = urllib_parse.unquote(env['RAW_PATH_INFO'], 'iso-8859-1')
        return env

    def finish(self):
        # we are having this to avoid fd leak when the client
        # cancels their connection before completion
        if not self.wfile.closed:
            try:
                self.wfile.flush()
            except socket.error:
                # A final socket error may have occurred here, such as
                # the local error ECONNABORTED.
                pass
        try:
            self.wfile.close()
        except socket.error:
            pass
        self.rfile.close()
        super(UnixDomainHttpProtocol3, self).finish()


class UnixDomainHttpProtocol2(eventlet.wsgi.HttpProtocol):
    def __init__(self, request, client_address, server):
        if client_address == '':
            client_address = ('<local>', 0)
        # base class is old-style, no super does not work properly
        eventlet.wsgi.HttpProtocol.__init__(self, request, client_address,
                                            server)
    def get_environ(self):
        env = super(UnixDomainHttpProtocol2, self).get_environ()
        # without this, any unicode character passed to the url path is
        # throws an error
        env['PATH_INFO'] = urllib_parse.unquote(env['RAW_PATH_INFO'], 'iso-8859-1')
        return env


class WSGIServer(object):
    _instance = None

    def _register_app_optgroup(self, app_name):
        return getattr(cfg.CONF, app_name)

    def _write_paste_ini(self, paste_file):
        if not os.path.exists(paste_file) or os.path.getsize(paste_file) == 0:
            middlewares = ["router", "auth", "roles", "statics",
                           "hooks", "system", "sqa_session"]
            paste_conf = {"router": "aalam_common.wsgi:Router.factory",
                          cfg.CONF.app_code: "aalam_common.wsgi:AppFactory",
                          "auth": "aalam_common.auth:Auth.factory",
                          "hooks": "aalam_common.hooks:Hooks.factory",
                          "roles": "aalam_common.role_mgmt:RolesMgmt.factory",
                          "statics":
                          "aalam_common.wsgi:StaticsMiddleware.factory",
                          "sqa_session":
                          "aalam_common.wsgi:SQASession.factory",
                          "system":
                          "aalam_common.system:SystemHandlers.factory"}
            paste = """
[pipeline:main]
pipeline = %(middlewares)s %(app_code)s
""" % {'middlewares': " ".join(middlewares),
                'app_code': cfg.CONF.app_code}

            for m in middlewares:
                factory = paste_conf.get(m)
                filter = """
[filter:%(name)s]
paste.filter_factory = %(factory)s
""" % {"name": m, "factory": factory}
                paste += filter

            paste += """
[app:%(app_code)s]
paste.app_factory = %(factory)s
""" % {"app_code": cfg.CONF.app_code,
                "factory": paste_conf.get(cfg.CONF.app_code)}

            with open(paste_file, 'w') as f:
                f.write(paste)
            os.chown(paste_file, os.geteuid(), os.getegid())
            # Change mode to 0700
            os.chmod(paste_file, stat.S_IRWXU)

    def _load_app_entry(self):
        self.app_entry = None

        if not cfg.CONF.entry_point:
            raise zexc.MissingConfigParameter("entry_point")
        else:
            (module_name, meth_name) = cfg.CONF.entry_point.split(":")
            module = importlib.import_module(module_name)
            self.app_entry = getattr(module, meth_name)

        if not self.app_entry:
            raise ValueError(
                "Entry point(%s) is not valid" % cfg.CONF.entry_point)

        update_lock = os.path.join(
            WSGI_SOCKET_ROOT, cfg.CONF.app_provider_code,
            cfg.CONF.app_code + MIGRATE_LOCK)
        if "MIGRATE_FROM" not in os.environ:
            if os.path.exists(update_lock):
                os.unlink(update_lock)
                self._state = zc.STATE_POST_MIGRATE
                self._sock_name = "_".join(
                    [self._sock_name, "post", "migrate"])
            else:
                self._state = zc.STATE_STARTED
        else:
            self._state = zc.STATE_MIGRATE
            if os.path.exists(update_lock):
                # An upate already happened and post migrate did not run
                sys.exit(-1)

            with open(update_lock, "w") as fd:
                fd.write(str(datetime.utcnow()))

        app_callbacks.update(self.app_entry(self._state))

    def __init__(self, app_name):
        self.server = None
        wsgi_conf = self._register_app_optgroup(app_name)
        self._sock_name = app_name

        if not cfg.CONF.app_provider_code:
            raise zexc.MissingConfigParameter(section='DEFAULT',
                                              param="app_provider_code")

        self._num_threads = 1000
        if not wsgi_conf.paste_ini:
            raise zexc.MissingConfigParameter(section=app_name,
                                              param="paste_ini")

        self._paste_ini = wsgi_conf.paste_ini
        self._write_paste_ini(self._paste_ini)
        self._load_app_entry()

        if self._state != zc.STATE_MIGRATE:
            self._pool = eventlet.GreenPool(size=self._num_threads)
            self._sock = self._setup_sock(wsgi_conf)

        webob.exc.WSGIHTTPException.body_template_obj = string.Template('${explanation}')
        self.logger = logging.getLogger("wsgiapp")
        debug.init_logging(self.logger)
        tmp = logging.getLogger('routes.middleware')
        tmp.setLevel(logging.INFO)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        WSGIServer._instance = None

    def _setup_sock(self, wsgi_conf):
        if getattr(wsgi_conf, "port", None):
            return self._setup_inet_sock(wsgi_conf)

        return self._setup_unix_sock()

    def _setup_inet_sock(self, wsgi_conf):
        return eventlet.listen(
            (getattr(wsgi_conf, "bind_address", "127.0.0.1"),
             int(wsgi_conf.port)))

    def _setup_unix_sock(self):
        _sock_path = "/".join([WSGI_SOCKET_ROOT,
                               cfg.CONF.app_provider_code,
                               self._sock_name + "." + "sock"])
        dir_name = os.path.dirname(_sock_path)
        uid = os.geteuid()

        # check if the directory exists, else create it
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            # change mode to 0750
            os.chmod(dir_name, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
            gid = grp.getgrnam("www-data").gr_gid
            os.chown(dir_name, uid, gid)

        if os.path.exists(_sock_path):
            logging.debug("File " + _sock_path + " exists")
            os.unlink(_sock_path)
        else:
            logging.debug("File " + _sock_path + " does not exist")

        ret = eventlet.listen(_sock_path, family=socket.AF_UNIX)
        gid = grp.getgrnam("www-data").gr_gid
        os.chown(_sock_path, uid, gid)
        os.chmod(_sock_path, stat.S_IRWXU | stat.S_IRWXG)
        return ret

    def run(self):
        if self._state == zc.STATE_MIGRATE:
            if zc.CALLBACK_MIGRATE in app_callbacks:
                try:
                    app_callbacks[zc.CALLBACK_MIGRATE](
                        os.environ['MIGRATE_FROM'])
                except Exception:
                    os.unlink(os.path.join(
                        WSGI_SOCKET_ROOT, cfg.CONF.app_provider_code,
                        cfg.CONF.app_code + MIGRATE_LOCK))
                    sys.exit(-1)
        else:
            self._app = paste.deploy.loadapp("config:" + self._paste_ini)

            global wsgi_listener
            wsgi_listener = eventlet.spawn(
                self._run_server, self._app, self._sock)
            try:
                wsgi_listener.wait()
            except Exception:
                import traceback
                traceback.print_exc()
            logging.warn("WSGI server finished successfully")
            logging.warn("WSGI server pool num open connections %s"
                         % self._pool.running())
            # waitall sometimes never returns
            # self._pool.waitall()
            logging.warn("Server pool waited for pending connections")

    def _run_server(self, app, sock):
        logging.info("Starting the server")
        log = open("/dev/null", "w+")
        from greenlet import GreenletExit

        try:
            eventlet.wsgi.server(
                sock, app, custom_pool=self._pool,
                protocol=UnixDomainHttpProtocol3 if sys.version_info[0] == 3 else UnixDomainHttpProtocol2,
                log_output=False, log=log,
                debug=True)
        except GreenletExit:
            pass


def report_exception(request, e):
    if isinstance(e, webob.exc.HTTPException):
         raise e

    try:
        exc_type, exc_value, exc_tb = sys.exc_info()
        etb = debug.ExceptionTraceback(exc_type, exc_value, exc_tb)
        lines = etb.format_exception()
        eventlet.spawn_n(
            report_bug, 'request', exc_type, exc_value, lines,
            url="%s %s" % (request.method, request.path))
    finally:
        exc_type = exc_value = exc_tb = None
        etb = None
    import traceback
    traceback.print_exc()
    raise webob.exc.HTTPInternalServerError()


class Middleware(object):
    def __init__(self, app):
        self._app = app

    @classmethod
    def factory(cls, global_conf, **local_conf):
        def filter(app):
            return cls(app)

        return filter

    def pre(self, request):
        return None

    def post(self, request, response):
        return response

    @webob.dec.wsgify(RequestClass=AALAMRequest)
    def __call__(self, request):
        result = self.pre(request)
        if result:
            return result

        result = request.get_response(self._app)
        return self.post(request, result)


class Router(object):
    def __init__(self, mapper, app):
        self.mapper = mapper
        if zc.CALLBACK_ROUTES in app_callbacks:
            app_callbacks[zc.CALLBACK_ROUTES](mapper)
        self.route_gen = routes.middleware.RoutesMiddleware(app,
                                                            self.mapper)

    @classmethod
    def factory(cls, global_conf, **local_conf):
        def filter(app):
            return cls(routes.Mapper(), app)

        return filter

    @webob.dec.wsgify(RequestClass=AALAMRequest)
    def __call__(self, request):
        return self.route_gen


class BaseHandler(object):
    def __init__(self, mapper):
        self.mapper = mapper

    @webob.dec.wsgify(RequestClass=AALAMRequest)
    def __call__(self, request):
        hardcoded = request.environ['routes.route'].hardcoded
        route = copy.copy(request.environ['wsgiorg.routing_args'][1])
        try:
            action = route["action"]
        except KeyError:
            logging.warn("No action registered for %s" %
                         request.environ['routes.url'])
            raise webob.exc.HTTPNotImplemented()

        custom_deserializer = route.get("deserializer", None)
        custom_serializer = route.get("serializer", None)
        inp_data_qualifier = route.get('dataset', None)
        for h in hardcoded:
            route.pop(h)

        for k, v in route.items():
            # negating the effect of url path decoding in UnixDomainHttpProtocol
            route[k] = v.encode('iso-8859-1').decode('utf8')

        try:
            return self.respond(action, request, custom_serializer,
                                custom_deserializer, inp_data_qualifier,
                                **route)
        except Exception as e:
            report_exception(request, e)

    def reject_405(self):
        raise webob.exc.HTTPMethodNotAllowed()

    def _json_deserializer(self, request):
        return json.loads(request.text)

    def json_deserializer(self, request):
        return self._json_deserializer(request)

    def _deserializer(self, request, custom_deserializer):
        call = getattr(self, custom_deserializer,
                       None) if custom_deserializer else None
        if call:
            return call(request)

        if not request.content_length:
            return {}

        if request.content_type == "application/json":
            return self._json_deserializer(request)
        else:
            logging.warn("Unable to determine a deserializer for %s"
                         % request.content_type)

        return None

    def _json_default(self, obj):
        if isinstance(obj, dt.datetime):
            return datetime.to_user(obj)
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dt.date):
            return date.to_user(obj)

    def _json_serializer(self, app_data, response):
        primitives = six.integer_types + (str, float, bool)
        if isinstance(app_data, list) or \
           isinstance(app_data, dict):
            body = app_data
        elif isinstance(app_data, primitives):
            body = {"data": app_data}
        elif isinstance(app_data, object):
            to_dict = getattr(app_data, "to_dict", None)
            if to_dict:
                body = to_dict()
            else:
                body = "Unable to serialize %s" % type(app_data)

        response.content_type = "application/json"
        out_data = json.dumps(body, default=self._json_default)
        if six.PY2:
            response.body = out_data
        elif six.PY3:
            response.text = out_data

    def json_serializer(self, app_data, response):
        self._json_serializer(app_data, response)

    def _html_serializer(self, data, response):
        response.content_type = "text/html"

        @htmlmin(remove_comments=True, keep_pre=True,
                 remove_optional_attribute_quotes=False)
        def minify():
            if six.PY2:
                return unicode(data)
            else:
                return data

        response.text = minify()

    def html_serializer(self, app_data, response):
        self._html_serializer(app_data, response)

    def _serializer(self, custom_serializer, app_data, response):
        call = getattr(self, custom_serializer,
                       None) if custom_serializer else None
        if call:
            return call(app_data, response)

        # default behavior
        self._json_serializer(app_data, response)

    def respond(self, action, request, custom_serializer,
                custom_deserializer, inp_data_qualifier, **kwargs):
        req_data = self._deserializer(request, custom_deserializer)
        call = getattr(self, action, None)
        if not call:
            raise webob.exc.HTTPNotImplemented()

        if req_data and isinstance(req_data, dict):
            kwargs.update(req_data)
        try:
            app_ret = call(request, **kwargs)
        except TypeError:
            import traceback
            traceback.print_exc()
            msg = "Input data not proper\n"
            if inp_data_qualifier:
                msg += "Following are valid, (*) are manadatory\n" + \
                    inp_data_qualifier
            raise webob.exc.HTTPBadRequest(explanation=msg)
        except Exception as e:
            logging.error("Application failed for this url")
            report_exception(request, e)

        if isinstance(app_ret, tuple):
            status_code = app_ret[0]
            data = app_ret[1] if len(app_ret) is 2 else None
        else:
            status_code = 200
            data = app_ret

        response = webob.Response()
        response.status_code = status_code
        if data is not None:
            self._serializer(custom_serializer, data, response)

        return response


def AppFactory(global_config, **local_conf):
    @webob.dec.wsgify(RequestClass=AALAMRequest)
    def _app(request):
        # when defining a route, 'handler' should be of type BaseHandler
        # action should be a method if handler is none or str
        route = request.environ['wsgiorg.routing_args'][1]
        if not route:
            raise webob.exc.HTTPNotFound()

        try:
            handler = route["handler"]
        except KeyError:
            logging.error("handler not present in routes")
            return webob.exc.HTTPNotImplemented()

        return handler

    return _app


class SQASession(Middleware):
    def pre(self, request):
        return None

    def post(self, request, response):
        sqa_session_inited = request.environ['webob.adhoc_attrs']. \
            get('sqa_session') is not None
        sqa_sessions_inited = request.environ['webob.adhoc_attrs']. \
            get('sqa_sessions') is not None
        if response.status_code in range(400, 599):
            # though we override webob.Request to initialize sqa_session
            # it ultimately stores that in environ variable like below.
            if sqa_session_inited:
                request.sqa_session.rollback()
                logging.debug("Removing the sqa_session")
                request.sqa_session.remove()
            if sqa_sessions_inited:
                for session in request.sqa_sessoins:
                    session.rollback()
                    session.remove()

        elif response.status_code in range(200, 399):
            if sqa_session_inited:
                try:
                    request.sqa_session.commit()
                except sqlalchemy.exc.IntegrityError:
                    request.sqa_session.rollback()
                    raise webob.exc.HTTPConflict()
                finally:
                    request.sqa_session.remove()

            if sqa_sessions_inited:
                try:
                    for session in request.sqa_sessoins:
                        if session.dirty or session.deleted:
                            msg = "sqa_sessions are not auto flushed"
                            logging.error(msg)
                            raise zexc.SQASessionsNotFlushed()

                finally:
                    for session in request.sqa_sessoins:
                        session.remove()

        return response


class StaticsMiddleware(Middleware):
    def __init__(self, app):
        super(StaticsMiddleware, self).__init__(app)

    def _send_response(self, resource, fname, request, response):
        if os.path.isdir(fname) and os.path.exists(
                os.path.join(fname, "index.html")):
            fname = os.path.join(fname, "index.html")

        if not os.path.exists(fname):
            # Application should be handling this
            return None

        fname_gz = None
        if fname.endswith(".js") or fname.endswith(".html") or \
                fname.endswith(".css"):
            if os.path.exists(fname + ".gz"):
                fname_gz = fname + ".gz"
                response.content_encoding = "gzip"

        response.last_modified = os.path.getmtime(
            fname if not fname_gz else fname_gz)
        response.cache_control = "no-cache"
        if not request.if_modified_since or \
                response.last_modified > request.if_modified_since or request.range:
            if not os.path.exists(fname):
                return

            mime, enc = mimetypes.guess_type(fname)
            mime = mime or "application/octet-stream"
            response.content_type = mime
            if request.range:
                st_info = os.stat(fname)
                r_start, r_end = request.range.range_for_length(st_info.st_size)
                response.status_code = 206
                with open(fname, "rb") as fd:
                    fd.seek(r_start)
                    response.body = fd.read(
                        r_end - r_start)
                    response.content_range = webob.byterange.ContentRange(
                        r_start, r_end,
                        st_info.st_size)
            else:
                response.status_code = 200
                with open(fname if not fname_gz else fname_gz, "rb") as fd:
                    response.body = fd.read()
        else:
            response.status_code = 304

        return response

    def pre(self, request):
        if request.path.find(cfg.CONF.statics_url_root) == 0:
            # This is a statics content
            resource = request.path[len(cfg.CONF.statics_url_root) + 1:]
            if resource == "" or resource == "/":
                resource = "index.html"

            fname = os.path.join(cfg.CONF.statics_dir, resource)
            response = webob.Response()
            return self._send_response(resource, fname, request, response)

    def post(self, request, response):
        if not request.static_file:
            return response

        fname = request.static_file['path']
        resource = request.static_file['resource']
        return self._send_response(resource, fname, request, response)
