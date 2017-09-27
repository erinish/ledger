#!/usr/bin/env python3
"""
server.py
"""
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

app = Flask('simplelog')
api = Api(app)

testdata = {'test': 'salright'}


class Test(Resource):

    def get(self):
        return jsonify(testdata)

api.add_resource(Test, '/')

if __name__ == '__main__':
    app.run('0.0.0.0', port=9000, debug=True)