from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.contrib.cache import SimpleCache
from mplayer import Player, CmdPrefix

app = Flask(__name__)
app.config.from_object('config')
cache = SimpleCache()
cache.default_timeout = 86400
player = Player()
metaplayer = Player(args=('-af','volume=-200:1'))
metaplayer.cmd_prefix = CmdPrefix.PAUSING
db = SQLAlchemy(app)
sleeper = None

import views, sockets, models, music, context_processors



