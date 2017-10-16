#!/usr/bin/env python3
"""
rest server for simplelog
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

app = Flask('simplelog')
api = Api(app)

TASKFIELDS = {'task': fields.String,
              'uri': fields.String,
              'time': fields.Integer,
              'status': fields.String
              } 

if not Path(TASKFILE).is_file():
    with open(TASKFILE, 'w') as f:
        json.dump({}, f)

with open(TASKFILE, 'r') as f:
    TASKDATA = json.load(f)


class Tasks(Resource):
    """Add new TASKDATA and list all"""
    def get(self):
        """handle get request for all tasks"""
        return TASKDATA

    @marshal_with(TASKFIELDS)
    def put(self):
        """handle put request for new tasks"""
        print(request.json)
        stamp = request.json['time']
        msg = request.json['task']
        digest = str(stamp) + msg
        taskid = hashlib.sha256(digest.encode()).hexdigest()
        if taskid not in TASKDATA:
            TASKDATA[taskid] = {}
        else:
            return 401
        for k, v in request.json.items():
            TASKDATA[taskid][k] = v
        TASKDATA[taskid]['uri'] = "/task/{}".format(taskid)
        with open(TASKFILE, 'w') as f:
            json.dump(TASKDATA, f)
        return TASKDATA[taskid], 201



class TaskHandler(Resource):
    """Work with specific TASKDATA"""
    def get(self, taskid):
        """retrieve a specific task"""
        if taskid not in TASKDATA:
            return {taskid: 'not found'}, 404
        return TASKDATA[taskid]

    def delete(self, taskid):
        """delete the specified task"""
        deleted = TASKDATA.pop(taskid)
        with open(TASKFILE, 'w') as f:
            json.dump(TASKDATA, f)
        return deleted

    def put(self, taskid):
        """update the specified task"""
        if taskid not in TASKDATA:
            TASKDATA[taskid] = {}
        for k, v in request.form.items():
            TASKDATA[taskid][k] = v
        with open(TASKFILE, 'w') as f:
            json.dump(TASKDATA, f)
        return TASKDATA[taskid], 201

api.add_resource(Tasks, '/task')
api.add_resource(TaskHandler, '/task/<string:taskid>')


@app.route('/')
def main():
#    tasksbytime = copy.deepcopy(sorted(TASKDATA.items(), key=lambda x: x[1]['time'], reverse=True))
#    for task in tasksbytime:
#        task[1]['time'] = arrow.get(task[1]['time']).to('local').format('MM/DD/YY HH:mm')
    return render_template('index.html')

@app.route('/testing')
def testing():
    return render_template('testing.html')
if __name__ == '__main__':
    app.run('0.0.0.0', port=9000, debug=True)