#!/usr/bin/env python3
"""
rest server for simplelog
"""
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

app = Flask('simplelog')
api = Api(app)

tasks = {1: 'salright'}


class Tasks(Resource):

    def get(self):
        return jsonify(tasks)

class Task(Resource):

    def taskid_exists(f):
        def wrapper(*args, **kwargs):
            if args[0] not in tasks:
                return jsonify({args[0]: 'not found'}), 404
        return wrapper

    @taskid_exists
    def get(self, taskid):
        return jsonify(tasks[taskid])

    @taskid_exists
    def delete(self, taskid):
        tasks.pop(taskid)
        return jsonify({taskid: 'deleted successfully'}), 204


api.add_resource(Tasks, '/task')
api.add_resource(Task, '/task/<int:taskid>')

if __name__ == '__main__':
    app.run('0.0.0.0', port=9000, debug=True)