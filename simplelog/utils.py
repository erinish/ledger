import re
import requests as req

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