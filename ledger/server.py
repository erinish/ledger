#!/usr/bin/env python3
"""
rest server for Ledger
"""
import os
import json
import copy
import hashlib
import arrow
from pathlib import Path
from flask import Flask, request, render_template
from flask_restful import Resource, Api, fields, marshal_with

MYDIR = os.path.dirname(os.path.abspath(__file__))
TASKFILE = os.path.join(MYDIR, 'data', 'tasks.json')


def logit(msg):
    logfile = "/tmp/wtf"
    with open(logfile, 'a') as f:
        f.write(str(msg))


app = Flask('ledger')
api = Api(app)


TASKFIELDS = {'task': fields.String,
              'uri': fields.String,
              'time': fields.Integer,
              'status': fields.String
              }

if not Path(TASKFILE).is_file():
    with open(TASKFILE, 'w') as f:
        json.dump({}, f)


def get_task_data():
    with open(TASKFILE, 'r') as f:
        return json.load(f)
    return False


class Tasks(Resource):
    """Add new taskdata and list all"""
    def get(self):
        """handle get request for all tasks"""
        taskdata = get_task_data()
        return taskdata

    @marshal_with(TASKFIELDS)
    def put(self):
        """handle put request for new tasks"""
        print(request.json)
        stamp = request.json['time']
        msg = request.json['task']
        digest = str(stamp) + msg
        taskid = hashlib.sha256(digest.encode()).hexdigest()
        taskdata = get_task_data()
        if taskid not in taskdata:
            taskdata[taskid] = {}
        else:
            return 401
        for k, v in request.json.items():
            taskdata[taskid][k] = v
        taskdata[taskid]['uri'] = "/task/{}".format(taskid)
        with open(TASKFILE, 'w') as f:
            json.dump(taskdata, f)
        return taskdata[taskid], 201


class TaskHandler(Resource):
    """Work with specific taskdata"""
    def get(self, taskid):
        """retrieve a specific task"""
        taskdata = get_task_data()
        if taskid not in taskdata:
            return {taskid: 'not found'}, 404
        return taskdata[taskid]

    def delete(self, taskid):
        """delete the specified task"""
        taskdata = get_task_data()
        deleted = taskdata.pop(taskid)
        with open(TASKFILE, 'w') as f:
            json.dump(taskdata, f)
        return deleted

    def put(self, taskid):
        """update the specified task"""
        taskdata = get_task_data()
        if taskid not in taskdata:
            taskdata[taskid] = {}
        for k, v in request.json.items():
            taskdata[taskid][k] = v
        with open(TASKFILE, 'w') as f:
            json.dump(taskdata, f)
        return taskdata[taskid], 201

api.add_resource(Tasks, '/task')
api.add_resource(TaskHandler, '/task/<string:taskid>')


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/testing')
def testing():
    return render_template('testing.html')


@app.errorhandler(404)
def page_not_found(error):
    return 'This route does not exist {}'.format(request.url), 404
if __name__ == '__main__':
    app.run('0.0.0.0', port=9000, debug=True)
