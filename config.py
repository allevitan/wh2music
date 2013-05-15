import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'fwe656gUY56Fu079'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')


#File Stuff
TEMP_DIR = os.path.abspath('app/temp/')
MUSIC_DIR = os.path.abspath('app/music/')
