#!/usr/bin/env python3
"""
rest server for simplelog
"""
import os
import json
import hashlib
from pathlib import Path
from flask import Flask, request
from flask_restful import Resource, Api

MYDIR = os.path.dirname(os.path.abspath(__file__))
TASKFILE = os.path.join(MYDIR, 'data', 'tasks.json')

app = Flask('simplelog')
api = Api(app)

if not Path(TASKFILE).is_file():
    with open(TASKFILE, 'w') as f:
        json.dump({}, f)

with open(TASKFILE, 'r') as f:
    tasks = json.load(f)


class Tasks(Resource):

    def get(self):
        return tasks

    
    def put(self):
        stamp = request.form['time']
        msg = request.form['task']
        digest = str(stamp) + msg
        taskid = hashlib.sha256(digest.encode()).hexdigest()
        if taskid not in tasks:
            tasks[taskid] = {}
        else:
            return 401
        for k, v in request.form.items():
            tasks[taskid][k] = v
        tasks[taskid]['uri'] = "/task/{}".format(taskid)
        with open(TASKFILE, 'w') as f:
            json.dump(tasks, f)
        return tasks[taskid], 201



class TaskHandler(Resource):

    def get(self, taskid):
        if taskid not in tasks:
            return {taskid: 'not found'}, 404
        return tasks[taskid]

    def delete(self, taskid):
        deleted = tasks.pop(taskid)
        with open(TASKFILE, 'w') as f:
            json.dump(tasks, f)
        return deleted

    def put(self, taskid):
        if taskid not in tasks:
            tasks[taskid] = {}
        for k, v in request.form.items():
            tasks[taskid][k] = v
        with open(TASKFILE, 'w') as f:
            json.dump(tasks, f)
        return tasks[taskid], 201

api.add_resource(Tasks, '/task')
api.add_resource(TaskHandler, '/task/<string:taskid>')

if __name__ == '__main__':
    app.run('0.0.0.0', port=9000, debug=True)