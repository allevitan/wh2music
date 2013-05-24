from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.contrib.cache import SimpleCache
from mplayer import Player

app = Flask(__name__)
app.config.from_object('config')
cache = SimpleCache()
cache.default_timeout = 86400
player = Player()
db = SQLAlchemy(app)
sleeper = None

import views, sockets, models, music, context_processors



