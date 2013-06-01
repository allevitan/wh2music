#!/bin/bash
apt-get install mplayer python-virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python db_create.py
mkdir app/temp app/music
