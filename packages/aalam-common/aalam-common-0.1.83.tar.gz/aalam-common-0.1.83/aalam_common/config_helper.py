# coding=utf8
import sys
import os
if sys.version_info[0] == 3:
    import configparser as ConfigParser
else:
    import ConfigParser


class ConfigObject(object):
    def __init__(self, _items):
        self._items = _items

    def __getattr__(self, k):
        if k == '_items':
            return self._items
        elif k in self._items:
            return self._items[k]
        else:
            raise AttributeError("Unable to find %s" % k)


class ConfigSectionsObject(object):
    def __init__(self, fpath):
        self._sections = {}
        self._load_config(fpath)

    def _load_config(self, fpath):
        if not os.path.exists(fpath):
            return

        if sys.version_info[0] == 3:
            c = ConfigParser.RawConfigParser(strict=False)
        else:
            c = ConfigParser.ConfigParser()
        c.read(fpath)
        for s in c.sections():
            opts = c.options(s)
            opt_items = {}
            for opt in opts:
                opt_items[opt] = c.get(s, opt)
            self._sections[s] = ConfigObject(opt_items)
        if c.defaults():
            self._sections['DEFAULT'] = c.defaults()

    def __getattr__(self, k):
        if k == "_sections":
            return self._sections

        if k in self._sections:
            return self._sections[k]

        else:
            if 'DEFAULT' in self._sections and k in self._sections['DEFAULT']:
                return self._sections['DEFAULT'][k]
            else:
                raise AttributeError("Unable to find %s" % k)


class Config(object):
    def __init__(self):
        try:
            index = sys.argv.index("--config-file")
            config_file = sys.argv[index+1]
            self.CONF = ConfigSectionsObject(config_file)
            dname = os.path.dirname(config_file)
            for f in os.listdir(dname):
                _f_full = os.path.join(dname, f)
                if f.endswith(".config") and f != config_file and os.path.isfile(_f_full):
                    try:
                        self.CONF._load_config(_f_full)
                    except:
                        pass
        except Exception:
            self.CONF = ConfigSectionsObject("")

    def publicdir(self, pcode, acode):
        return os.path.abspath(os.path.join(
            self.CONF.datadir, "..", "..", ".public", pcode, acode))

    def refresh(self, path):
        self.CONF = ConfigSectionsObject(path)
