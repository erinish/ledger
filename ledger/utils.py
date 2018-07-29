import re
import requests as req
import configparser
from pathlib import Path


class ConfigBoss():

    def __init__(self, config_file=None):
        self._config_file = config_file
        self._user_home_conf = Path.home() / '.ledger' / 'ledger.conf'
        self._system_default_conf = Path('/etc/ledger/ledger.conf')
        self._package_default_conf = Path('ledger.conf')
        self._config_files = [self._package_default_conf, self._system_default_conf, self._user_home_conf, self._config_file]

        self.config_data = self._parse_config_file()
    

    def _parse_config_file(self):

        self._parser = configparser.ConfigParser()
        # Not checking if exists because ConfigParser handles this gracefully
        # Standard allowing for hierarchal config overrides
        for item in self._config_files:
            if item:
                self._parser.read(item)
        # Return the parser because ConfigParser object actually contains the config data 
        return self._parser


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
            if key == 'status':
                tests.append(task['status'] == value)
    return all(tests)
