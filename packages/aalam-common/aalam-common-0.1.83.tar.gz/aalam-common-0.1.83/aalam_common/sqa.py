# coding=utf8
import logging
import sqlalchemy
import six
import time
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.query import Query

from aalam_common import exceptions as zexc
from aalam_common.config import cfg
from aalam_common.utils import datetime, date

_ENGINE = {}
__SESSION = {}


def getconnection(url):
    def _getconn():
        u = sqlalchemy.engine.url.make_url(url)
        dialect_cls = u._get_entrypoint().get_dialect_cls(u)
        dargs = {'dbapi': dialect_cls.dbapi()}
        dialect = dialect_cls(**dargs)
        (cargs, cparams) = dialect.create_connect_args(u)
        for i in range(0, 5):
            try:
                return dialect.connect(*cargs, **cparams)
            except Exception as e:
                if i == 4:
                    raise e
                logging.critical(
                    "Connection to db failed, retrying again for %s time, e %s"
                    % (i, e))
                time.sleep(1)
    return _getconn


def init_engine(db_name, dec_base, charset=None, use_pycnctr=None):
    # the following code is just for the SQLITE databases
    # from sqlalchemy.interfaces import PoolListener

    # class ForeignKeysListener(PoolListener):
    #     def connect(self, dbapi_con, con_record):
    #         dbapi_con.execute('pragma foreign_keys=ON')

    sqa_cfg = getattr(cfg.CONF, "sqlalchemy", None)
    if not sqa_cfg:
        return

    url = sqa_cfg.url
    url_ends_with_db_name = url.endswith(db_name)

    kwargs = {"echo": getattr(sqa_cfg, "debug", "false").lower() == 'true'}
    if url.startswith("sqlite://"):
        # kwargs["listeners"] = [ForeignKeysListener()]
        kwargs['poolclass'] = sqlalchemy.pool.StaticPool
        kwargs['connect_args'] = {'check_same_thread': False}
    else:
        if url.startswith("mysql:") and use_pycnctr:
            kwargs['max_overflow'] = 30
            url = url.replace("mysql:", "mysql+%s:" % use_pycnctr)

        if charset:
            url = url + "?charset=%s" % charset

    kwargs["creator"] = getconnection(url)
    kwargs['query_cache_size'] = 0
    logging.debug("DB url %s" % url)
    engine = create_engine(url, pool_recycle=3600, **kwargs)
    if url.startswith("mysql") and not url_ends_with_db_name:
        engine.execute("create database if not exists %s" % db_name)
        engine.execute("use %s" % db_name)
    try:
        dec_base.metadata.create_all(engine)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e
    _ENGINE[db_name] = engine


def _get_engine(db_name):
    global _ENGINE
    if db_name not in _ENGINE:
        logging.error("Database '%s' not found or not inialized" % db_name)
        raise zexc.DatabaseNotFound(db_name)

    return _ENGINE[db_name]


def reset_engine():
    global _ENGINE
    _ENGINE = {}


def init_session(db_name):
    global __SESSION
    engine = _get_engine(db_name)
    __SESSION[db_name] = scoped_session(sessionmaker(bind=engine))
    return __SESSION[db_name]


def Session(db_name):
    if db_name in __SESSION:
        return __SESSION[db_name]
    return init_session(db_name)


def create_user_with_database(engine, user, password, host, db):
    host = host.replace("%", "%%")
    engine.execute("CREATE USER '%s'@'%s' IDENTIFIED BY '%s'" % (
        user, host, password))
    engine.execute("CREATE DATABASE %s" % db)
    engine.execute("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s'" % (
        db, user, host))
    engine.execute("FLUSH PRIVILEGES")


def destroy_user_with_database(engine, user, host, db):
    host = host.replace("%", "%%")
    engine.execute("DROP DATABASE %s" % db)
    engine.execute("DROP USER '%s'@'%s'" % (user, host))


def query_process(*args, **kwargs):
    num = kwargs.get("num", -1)
    proc_func = kwargs.get('proc_func', lambda i, k, v: v)
    qfunction = args[0] if len(args) > 0 else None

    def _query_process(*args, **kwargs):
        def wrapper(*args, **kwargs):
            func = qfunction if qfunction is not None else function
            res = func(*args, **kwargs)
            if not res:
                return None

            if not isinstance(res, Query):
                raise zexc.NotAQueryObject(res)

            count = 0
            num_cols = len(res.column_descriptions)

            dts = [index for index, value in enumerate(
                res.column_descriptions) if isinstance(
                value['type'], sqlalchemy.DateTime)]
            ret = []

            keys = None
            for r in res:
                convert_dt = lambda index, value: value if index not \
                    in dts else datetime.from_db(value)
                if not keys:
                    keys = list(r.keys())
                values = [
                    proc_func(index, keys[index], convert_dt(index, value)) for (index, value) in enumerate(r)
                ]
                if num_cols is 1:
                    value = values[0]
                else:
                    value = dict(zip(keys, values))

                ret.append(value)

                count += 1
                if num > 0 and count == num:
                    break

            if num is 1:
                if len(ret) is 0:
                    return None

                return ret[0]

            return ret

        if qfunction:
            return wrapper(*args, **kwargs)
        else:
            function = args[0]

        return wrapper
    return _query_process


class QueryResultGrouping(object):
    def __init__(self, ref_column, group_columns):
        self.ref_column = ref_column
        self.group_columns = group_columns
        self.column_groups = {}

    def process(self, query_row):
        ref = self.column_groups.get(query_row[self.ref_column], {})
        ref_empty = ref == {}
        for k, v in query_row.items():
            if k in self.group_columns:
                if not ref_empty and k in ref:
                    if v is not None:
                        ref[k].append(v)
                else:
                    ref[k] = [v] if v is not None else []
            else:
                ref[k] = v

        if ref_empty:
            self.column_groups[query_row[self.ref_column]] = ref

    def group(self):
        ret = []
        for k, v in self.column_groups.items():
            ret.append(v)

        return ret


def query_grouping(group_obj, num=-1):
    def _query_grouping(func):
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            if not res:
                return None

            if not isinstance(res, Query):
                raise zexc.NotAQueryObject(res)

            count = 0

            dts = [index for index, value in enumerate(
                res.column_descriptions) if isinstance(
                value['type'], sqlalchemy.DateTime)]
            ret = []

            for r in res:
                convert_dt = lambda index, value: value if index not \
                    in dts else datetime.from_db(value)
                values = [
                    convert_dt(index, value) for (index, value) in enumerate(r)
                ]

                group_obj.process(dict(zip(r.keys(), values)))
                count += 1
                if num > 0 and count == num:
                    break

            ret = group_obj.group()
            if num is 1:
                if len(ret) is 0:
                    return None

                return ret[0]

            return ret

        return wrapper

    return _query_grouping


class EvaluateFilters(object):
    def __init__(self, filter_dict, field_dict, not_split_filters=[]):
        self.filter_dict = filter_dict
        self.field_dict = field_dict
        self.not_split_filters = not_split_filters

    def eval(self, fields_present=None, custom_eval=None):
        # custom eval accepts the key, condition and the value as params
        # and is supposed to return a tuple with the evaluated conditions
        ret = ()
        for k, v in self.filter_dict.items():
            index = k.rfind('_')
            try:
                if index is not -1:
                    method = getattr(self, k[index:])
            except AttributeError:
                index = -1

            if index is -1:
                method = getattr(self, "_eq")
                index = None

            try:
                field = self.field_dict[k[:index]]
                if fields_present is not None:
                    fields_present.append(k[:index])
            except KeyError:
                if not custom_eval:
                    logging.warn("Invalid field %s accessed" % k[:index])
                    raise zexc.InvalidFilterField(k[:index])
                else:
                    _r = custom_eval(k[:index], k[index:] if index != None else '_eq', v)
                    if not _r:
                        raise zexc.InvalidFilterField("Custom eval returned null for %s" % k[:index])
                    else:
                        ret += _r
                        continue

            is_str = isinstance(v, six.string_types) or isinstance(v, six.text_type)
            if is_str and '|' in v:
                ored_filters = (k + "=" + v).split("|")
                ored_map = {}
                for f in ored_filters:
                    try:
                        _k, _v = f.split("=")
                    except ValueError:
                       continue
                    ored_map[_k] = _v

                if len(ored_map.keys()) > 1:
                    tmp = []
                    try:
                        val = EvaluateFilters(
                            ored_map, self.field_dict,
                            not_split_filters=self.not_split_filters).eval(tmp, custom_eval=custom_eval)
                        if fields_present:
                            fields_present.extend(tmp)
                        ret += (sqlalchemy.or_(*val),)
                        continue
                    except zexc.InvalidFilterField:
                        pass

            field_type = field.type if type(field.type) != sqlalchemy.sql.sqltypes.NullType else getattr(field, "__fld_type", None)
            if type(field_type) in [sqlalchemy.VARCHAR, sqlalchemy.Enum,
                                    sqlalchemy.Unicode] and \
                    k[:index] not in self.not_split_filters and \
                    ',' in v:
                v = v.split(",")

            if type(field_type) == sqlalchemy.Integer:
                try:
                    v = int(v)
                except ValueError:
                    if ',' in v:
                        v = v.split(',')
                    elif v in self.field_dict:
                        v = self.field_dict[v]
            elif (type(field_type) == sqlalchemy.Float or
                  type(field_type) == sqlalchemy.Numeric or
                  type(field_type) == sqlalchemy.DECIMAL):
                try:
                    v = float(v)
                except ValueError as e:
                    if v in self.field_dict:
                        v = self.field_dict[v]
                    else:
                        raise e
            elif type(field_type) == sqlalchemy.DateTime or \
                    isinstance(field_type, sqlalchemy.types.DATETIME):
                v = datetime.to_db(datetime.from_user(v))
            elif type(field_type) == sqlalchemy.Date:
                v = date.from_user(v)
            elif type(field_type) == sqlalchemy.BOOLEAN:
                v = str(v).lower() in ['1', 'true']

            ret += (method(field, v), )

        return ret

    def __escape_list(self, v):
        _v = []
        for i, n in enumerate(v):
            if not _v or _v[-1][-1] == '\\':
                _v.append(n)
            else:
                _v[-1] += ",%s" % n
        return _v

    def _like(self, f, v):
        if isinstance(v, list):
            _v = self.__escape_list(v)
            if len(_v) == 1:
                v = _v[0]
            else:
                return sqlalchemy.or_(
                    *[f.like(n if n[-1] != '\\' else n[0:-1]) for n in _v])
        return f.like(v)

    def _rlike(self, f, v):
        if isinstance(v, list):
            _v = self.__escape_list(v)
            if len(_v) == 1:
                v = _v[0]
            else:
                return sqlalchemy.or_(
                    *[sqlalchemy.func.regexp_replace(f, '[ .,;\-/]', '').like(re.sub('[ .,;\-/]', '', n) if n[-1] != '\\' else n[0:-1]) for n in _v])
        return sqlalchemy.func.regexp_replace(f, '[ .,;\-/]', '').like(
            re.sub('[ .,;\-/]', '', v))

    def _g(self, f, v):
        return f > v

    def _l(self, f, v):
        return f < v

    def _eq(self, f, v):
        if isinstance(v, list):
            return f.in_(v)
        return f == v

    def _le(self, f, v):
        return f <= v

    def _ge(self, f, v):
        return f >= v

    def _ne(self, f, v):
        if isinstance(v, list):
            return f.not_in(v)
        return f != v

    def _isnull(self, f, v):
        return f.is_(None)

    def _isnotnull(self, f, v):
        return f.isnot(None)


def sqa_enum(*args):
    import sqlalchemy.dialects.mysql
    return sqlalchemy.dialects.mysql.ENUM(*args, strict=True)


def get_database_name():
    return "_".join([cfg.CONF.app_provider_code, cfg.CONF.app_code])
