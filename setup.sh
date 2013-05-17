#!/bin/bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python db_create.py
mkdir app/temp app/music
