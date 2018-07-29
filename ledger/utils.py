import re
import requests as req
import configparser
from pathlib import Path


class ConfigBoss():

    def __init__(self, config_file=None):
        self._config_file = config_file
        self.user_home_conf = Path.home() / '.ledger' / 'ledger.conf'
        self.system_default_conf = Path('/etc/ledger/ledger.conf')
        self.package_default_conf = Path('ledger.conf')

        self.config_files = [self.config_file, self.user_home_conf, self.system_default_conf, self.package_default_conf]

        # Not checking if exists because ConfigParser handles this gracefully
        for item in self.config_files:
            self.config_data = self._parse_config_file()
    

    def _parse_config_file(self):

        self._parser = configparser.ConfigParser()
        self._parser.read(self._config_file)
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
