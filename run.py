#!venv/bin/python
from app import app
from flask import Flask, render_template
from werkzeug.serving import run_with_reloader
from gevent import monkey
from socketio.server import SocketIOServer

#app.run(port=8000)

monkey.patch_all()

@run_with_reloader
def run_dev_server():
    port = 8000
    SocketIOServer(('', port), app, resource="socket.io").serve_forever()

run_dev_server()
