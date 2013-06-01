##WH3Music
A simple Flask app designed to be run on a Raspberry Pi. It plays music on the Raspberry Pi itself while users on the website manage the playlist.

###Installation Instructions
```bash
$ git clone https://github.com/allevitan/wh2music.git
$ sudo wh2music/setup.sh
```
setup.sh will install any unmet dependencies and set up the app's music database and directories

```bash
$ wh2music/run.py --help
```

###Dependencies
* mplayer
* virtualenv
* mplayer.py
* Flask, Flask-SQLAlchemy, and Flask-WTF
* gevent and gevent-socketio

Only mplayer and virtualenv will be installed system-wide by the setup script (if not already present). The rest of the dependencies will be installed in a virtual environment in the 'wh2music' directory.

###The app currently includes
* Collaborative playlist management.
* A simple ajax-based song uploading interface.
* A simple music player
* A small built-in music library, including 4'33" by John Cage.

###Future commits will bring
* Less opaque control over the music
* A better upload experience
* Documentation.

