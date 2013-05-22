from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)
app.config.from_object('config')
cache = SimpleCache()
cache.default_timeout = 86400
db = SQLAlchemy(app)

import views, models, context_processors
