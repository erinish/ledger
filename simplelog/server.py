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

    def get(self, taskid):
        if taskid not in tasks:
            return jsonify('not found'), 404
        return jsonify(tasks[taskid])

    def delete(self, taskid):
        tasks.pop(taskid)
        return jsonify({taskid: 'deleted successfully'}), 204


api.add_resource(Tasks, '/task')
api.add_resource(Task, '/task/<int:taskid>')

if __name__ == '__main__':
    app.run('0.0.0.0', port=9000, debug=True)