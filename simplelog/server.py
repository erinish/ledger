"""
server.py
"""
from flask import Flask, response, jsonify
from flask_restful import Resource, Api

app = Flask('simplelog')
api = Api(app)

if __name__ == '__main__':
    app.run('0.0.0.0', port=9000, debug=True)