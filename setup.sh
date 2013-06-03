#!/bin/bash
if  ! which mplayer > /dev/null || ! which virtualenv > /dev/null
then
    echo 'dependencies not satisfied... searching for a package manager'
    if which apt-get
    then
	echo 'using apt-get to install mplayer, libevent, and virtualenv'
	apt-get install mplayer python-virtualenv libevent-dev
    elif which brew && which pip
    then
	echo 'using brew to install mplayer abd libevent and pip to install virtualenv'
	brew install mplayer libevent
	pip install virtualenv
    else
	echo 'No acceptible package manager found - install mplayer, virtualenv, and libevent by your own damn self'
    fi
else
    echo 'Dependencies met - continue as planned'
fi

virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python db_create.py
mkdir app/temp app/music
