#!venv/bin/python
from optparse import OptionParser

#Do this before importing app for --help and the like
parser = OptionParser()
parser.add_option('-p', '--port', dest='port', default=80, type='int',
                  help="specify a port serve the app on (default is 80)")

(options, args) = parser.parse_args()

from app import app
from flask import Flask, render_template
from werkzeug.serving import run_with_reloader
from gevent import monkey
from socketio.server import SocketIOServer
from socket import error as SocketError

monkey.patch_all()

def run_server():
    try:
        SocketIOServer(('', options.port), app, resource="socket.io").serve_forever()
    except SocketError as e:
        print '\nA socket error occured while starting the server:'
        print e
        print "Perhaps you don't have permission to use the specified port (%d)\n"\
            %options.port
        quit()

run_server()
