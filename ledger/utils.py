import re
import requests as req
import configparser
from configparser import MissingSectionHeaderError
from pathlib import Path
from stain import Stain

stain = Stain()


class ConfigBoss():

    def __init__(self, config_file=None):
        self._config_file = Path(config_file)
        self._user_home_conf = Path.home() / '.ledger' / 'ledger.conf'
        self._system_default_conf = Path('/etc/ledger/ledger.conf')
        self._package_default_conf = Path('ledger.conf')
        self._config_files = [self._package_default_conf, self._system_default_conf, self._user_home_conf, self._config_file]

        self.config_data = self._parse_config_file()

    def _parse_config_file(self):

        self._tmp_config = {}
        self._tmp_config['client'] = {}
        self._tmp_config['server'] = {}
        for item in self._config_files:
            if item.is_file():
                try:
                    # reset parser each time so we can track sources
                    self._parser = configparser.ConfigParser()
                    self._parser.read(item)
                    for section in self._parser.sections():
                        for k, v in self._parser[section].items():
                            self._tmp_config[section][k] = (v, str(item))

                except MissingSectionHeaderError as exc:
                    print(stain.YELLOW + "[Warning]" + stain.RESET + ": {} is an invalid config file. line: {}, {}".format(exc.filename.name, exc.lineno, exc.line))
                except KeyError as exc:
                    print(stain.RED + "[Error]" + stain.RESET + ": {} is an invalid section.".format(exc))

        return self._tmp_config
    
    @staticmethod
    def get_bool(val):
        val = str(val).lower()
        truth = ['yes', 'true', 'on', '1']
        falseness = ['no', 'false', 'off', '0']

        if val in truth:
            return True
        elif val in falseness:
            return False
        else:
            raise ValueError("Expected boolean value, got {}".format(val))


def check_id(api, taskid):
    mytasks = req.get("{}/task".format(api)).json()
    check = []
    for k in mytasks:
        fuzz = re.match(taskid, k)
        if fuzz:
            check.append(k)
    if len(check) > 1:
        print('error: hash matched multiple tasks. provide more characters')
        return None
    elif not check:
        print('error: no tasks match that hash')
        return None
    else:
        return check[0]


def filter_tasks(task, **kwargs):
    tests = []
    if kwargs:
        for key, value in kwargs.items():
            if key == 'days':
                tests.append(int(task['time']) > value)
            if key == 'close_time':
                tests.append(int(task['close_time']) > value)
            if key == 'status':
                tests.append(task['status'] == value)
    return all(tests)
