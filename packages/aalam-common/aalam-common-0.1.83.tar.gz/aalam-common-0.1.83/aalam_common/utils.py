# coding=utf8
import datetime as dt
import dateutil.parser
import dateutil.tz
import json
import base64
import logging
import sys
import os
if sys.version_info[0] == 3:
    import urllib.parse as urllib_parse
else:
    import urllib as urllib_parse
import requests
import requests_unixsocket
requests_unixsocket.monkeypatch()
import pystache
import six

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA, SHA256

from aalam_common.redisdb import redis_conn, baseapp_redisify_name
from aalam_common.config import cfg


# globals mostly used to cache frequently needed redis keys
_globals = {}
def get_common_rkey(rkey, redis_op='get'):
    if not rkey.startswith("__common__"):
        rkey = baseapp_redisify_name(rkey)
    if rkey not in _globals:
        _globals[rkey] = getattr(redis_conn, redis_op)(rkey)
    return _globals[rkey]


def _get_signature(message, privkey):
    # we will deprecate this in future
    key = RSA.importKey(open(privkey).read())
    h = SHA.new()
    h.update(message)
    signer = PKCS1_PSS.new(key)
    return base64.b64encode(signer.sign(h)).decode('utf-8')


def _get_signature_v2(message, privkey):
    key = RSA.importKey(open(privkey).read())
    h = SHA256.new()
    h.update(message)
    signer = PKCS1_PSS.new(key)
    return base64.b64encode(signer.sign(h)).decode('utf-8')


def _sign_and_send(prefix, header_key, method, hostname, url,
                   scheme="http", **kwargs):
    if scheme == "http+unix":
        ses = requests_unixsocket.Session()
        req = getattr(ses, method.lower())
        hostname = hostname.replace("/", "%2F")
    else:
        req = getattr(requests, method.lower())

    _url = url
    params = kwargs.pop('params', None)
    message = prefix + "#" + url
    if params:
        out_dict = {}
        for k, v in params.items():
            if v is None:
                continue
            if six.PY2:
                if isinstance(v, unicode):
                    v = v.encode('utf-8')
                elif isinstance(v, str):
                    v.decode('utf-8')
            out_dict[k] = v
        params = out_dict
        enc_params = urllib_parse.urlencode(params)
        _url = url + "?" + enc_params
        upd_params = {k: v for k, v in params.items() if k != 'nohook'}
        if upd_params:
            message = message + "?" + "&".join(
                ["%s=%s" % (k, v) for k, v in upd_params.items()])
    message = message.encode('utf-8')

    uri = "%(scheme)s://%(hostname)s%(url)s" % {
        "hostname": hostname,
        "url": _url,
        "scheme": scheme
    }
    # add auth header
    signature = _get_signature(message, cfg.CONF.privkey)
    x_auth_signature = prefix + ";" + signature

    new_dict = {}
    if 'headers' in kwargs:
        h = kwargs['headers']
    else:
        new_dict['headers'] = {}
        h = new_dict['headers']

    h[header_key] = x_auth_signature

    json_content = kwargs.pop("json", None)
    if json_content is not None:
        kwargs.pop("data", None)
        new_dict["data"] = json.dumps(json_content)
        h['Content-Type'] = "application/json"
    kwargs.update(new_dict)

    return req(uri, **kwargs)


def request_central_server(method, url, **kwargs):
    return _sign_and_send(cfg.CONF.bizcode,
                          'X-Auth-Signature',
                          method,
                          cfg.CONF.central_server,
                          url, **kwargs)


def request_apps_server(method, url, **kwargs):
    return _sign_and_send(cfg.CONF.bizcode,
                          'X-Auth-Signature',
                          method,
                          cfg.CONF.apps_server,
                          url, **kwargs)


def request_local_server(method, url, **kwargs):
    if "user" in kwargs:
        prefix = os.path.join(
            cfg.CONF.app_provider_code, cfg.CONF.app_code, kwargs.pop('user'))
    else:
        prefix = os.path.join(cfg.CONF.app_provider_code, cfg.CONF.app_code)
    return _sign_and_send(
        prefix,
        'X-Auth-Internal',
        method,
        "127.0.0.1",
        url, **kwargs)


def report_bug(bug_stage, exc_type, value, exc_lines, **kwargs):
    if isinstance(exc_lines, list):
        exc_lines = "\r\n".join(exc_lines)
    data = {
        'type': str(exc_type),
        'value': str(value),
        'logs': exc_lines,
        'stage': bug_stage,
    }
    data.update(kwargs)
    request_local_server(
        "PUT", "/aalam/base/bugs",
        json=data)


def deserialize_json_response(resp):
    if resp.status_code < 200 or resp.status_code > 299:
        return None

    if 'content-type' not in resp.headers or \
       "application/json" not in resp.headers['content-type']:
        return None

    return resp.json()


def mandatory_dataset(param):
    return "(*)" + param


class DateTimeRFC7231(object):
    pattern = "%a, %d %b %Y %H:%M:%S %Z"

    @staticmethod
    def encode(timestamp):
        return timestamp.strftime(DateTimeRFC7231.pattern)

    @staticmethod
    def decode(string):
        return dt.datetime.strptime(string, DateTimeRFC7231.pattern)


class datetime(object):
    UTC = dateutil.tz.gettz('UTC')
    DATE_PATTERN = None
    USER_ZONE = None

    @staticmethod
    def userzone():
        if not datetime.USER_ZONE:
            try:
                datetime.USER_ZONE = dateutil.tz.gettz(
                    Settings.get("timezone", "aalam", "base"))
            except:
                datetime.USER_ZONE = datetime.UTC
        return datetime.USER_ZONE

    def validator(func):
        def _wrapper(dtime):
            datetime.get_default_pattern()
            # if isinstance(dtime, str) or isinstance(dtime, unicode):
            if isinstance(dtime, six.string_types) or \
                    isinstance(dtime, six.text_type):
                day_first = datetime.DATE_PATTERN.index('%d') < \
                    datetime.DATE_PATTERN.index('%m')
                dtime = dateutil.parser.parse(dtime, dayfirst=day_first)
            elif not isinstance(dtime, dt.datetime):
                raise ValueError("Input should either be string or datetime")
            elif dtime.tzinfo is None:
                raise ValueError("Datetime object cannot be naive")

            return func(dtime)

        return _wrapper

    @staticmethod
    def utcnow():
        return dt.datetime.utcnow().replace(tzinfo=datetime.UTC)

    @staticmethod
    @validator
    def to_db(dtime):
        if dtime.tzname() != 'UTC':
            dtime = dtime.astimezone(datetime.UTC)

        return dtime.replace(tzinfo=None)

    @staticmethod
    def from_db(dtime):
        return dtime.replace(tzinfo=datetime.UTC) if dtime else None

    @staticmethod
    def get_default_pattern():
        if datetime.DATE_PATTERN is None:
            try:
                setting = Settings.get("date_format", "aalam", "base")
                datetime.DATE_PATTERN = setting.replace(
                    "YYYY", "%Y").replace(
                    "MM", "%m").replace(
                    "DD", "%d")
            except Exception:
                datetime.DATE_PATTERN = "%d-%m-%Y"

        return datetime.DATE_PATTERN

    @staticmethod
    @validator
    def to_user(dtime, pattern=None):
        if dtime.tzinfo != datetime.userzone():
            dtime = dtime.astimezone(datetime.userzone())

        if not pattern:
            pattern = datetime.get_default_pattern() + "T%H:%M:%S"
        return dtime.strftime(pattern)

    @staticmethod
    @validator
    def from_user(dtime):
        # parsing would have been done by the validator
        return dtime.replace(tzinfo=datetime.userzone())


class date(dt.date):
    DATE_PATTERN = None

    @staticmethod
    def _user_format():
        if date.DATE_PATTERN is None:
            try:
                setting = Settings.get("date_format", "aalam", "base")
                date.DATE_PATTERN = setting.replace(
                    "YYYY", "%Y").replace(
                    "MM", "%m").replace(
                    "DD", "%d")
            except Exception:
                date.DATE_PATTERN = "%d-%m-%Y"

        return date.DATE_PATTERN

    @staticmethod
    def from_user(ddate):
        # if isinstance(ddate, str) or isinstance(ddate, unicode):
        if isinstance(ddate, six.string_types) or \
                isinstance(ddate, six.text_type):
            return dt.datetime.strptime(ddate, date._user_format()).date()
        return ddate

    @staticmethod
    def to_user(ddate):
        return ddate.strftime(date._user_format())


class AppCache(object):
    @staticmethod
    def get(app_class=None, provider=None, app=None, detail=False):
        key_name = baseapp_redisify_name(
            "app-%s" %
            (app_class if app_class else "/".join([provider, app])))

        try:
            obj = get_common_rkey(key_name, "hgetall")
            obj = obj.copy()
            if detail:
                obj['id'] = int(obj['id'])
                return obj
            else:
                return int(obj['id'])
        except Exception:
            return None


def generate_RSA(bits=1024):
    new_key = RSA.generate(bits)
    public_key = new_key.publickey().exportKey("PEM")
    private_key = new_key.exportKey("PEM")
    return private_key, public_key


class mustachify(object):
    def __init__(self, template_path, **options):
        self._path = template_path
        self._options = options
        if "partial_files" in options:
            if 'partials' not in self._options:
                self._options['partials'] = {}

            files = self._options.pop('partial_files')
            for (k, v) in files.items():
                with open(v) as fd:
                    self._options['partials'][k] = fd.read()

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            return pystache.Renderer(**self._options).render_path(
                self._path, ret)

        return wrapper


class Settings(object):
    @classmethod
    def get(cls, key, provider, app):
        rkey = baseapp_redisify_name('setting-%s/%s/%s' % (provider, app, key))
        value = get_common_rkey(rkey, "get")
        if not value:
            resp = request_local_server(
                "GET",
                "/aalam/base/setting/%s/%s/%s" % (provider, app, key))
            if resp.status_code != 200:
                logging.error("Unable to find setting %s/%s/%s" % (
                    provider, app, key))
                return None

            data = resp.json()
            value = data['value']

            _globals[rkey] = value
        return value


class Alerts(object):
    @staticmethod
    def put(from_, receiver, fe_url, content, index=None,
            be_url=None, private_data=None, persist=True):
        body = {
            "from": from_,
            "app": "/".join([cfg.CONF.app_provider_code, cfg.CONF.app_code]),
            "receiver": receiver,
            "frontend_url": fe_url,
            "content": content,
            "persist": persist
        }
        if index is not None:
            body['index'] = index
        if be_url is not None:
            body['backend_url'] = be_url
        if private_data is not None:
            body['private_data'] = private_data

        resp = request_local_server(
            "PUT", "/aalam/base/message", json={"message": body})
        if resp.status_code != 200:
            return False

        return True
