from app import app, cache, player, sleeper
from werkzeug import secure_filename
from os.path import join
from time import time
from models import Song
import sockets
import gevent

def get_path_from_song(song):
    path = join(app.config['MUSIC_DIR'],
                secure_filename(song.artist.name),
                secure_filename(song.album.title),
                secure_filename(song.title + '.' + song.extension))
    return path

def append_song_to_playlist(song):
    global sleeper
    current, playlist = get_playlist()
    if not playlist and not current:
        path = get_path_from_song(song)
        player.loadfile(path)
        current = song.id
        sleeper = start_sleeper(song)
    else:
        playlist = playlist + [song.id]
    cache.set('playlist', playlist)
    cache.set('current', current)
    return current, playlist

def get_playlist():
    current = cache.get('current')
    playlist = cache.get('playlist')
    if playlist == None:
        playlist = []
        cache.set('playlist', playlist)
        #playlist = []
    return current, playlist

def next_song():
    global sleeper
    old_sleeper = sleeper
    current, playlist = get_playlist()
    try:
        current = playlist.pop(0)
        song = Song.query.filter_by(id=current).first()
        path = get_path_from_song(song)
        player.loadfile(path)
        sleeper = start_sleeper(song)
    except:
        current = None;
        player.stop();
    cache.set('current',current)
    cache.set('playlist', playlist)
    sockets.UpdateNamespace.broadcast('update', {'current':current, 'playlist':playlist})
    old_sleeper.kill()


def pause():
    if not player.paused:
        cache.set('last_pause', time())
        player.pause()

def play():
    if player.paused:
        last = cache.get('last_pause')
        if last:
            cache.inc('pause_time', time() - last)
        player.pause()

#gevent timekeeping functions for keeping track of the music

def sleep(sleep, action):
    gevent.sleep(sleep)
    print 'sup'
    action()
                
def keep_time(t):
    while True:
        cache.set('played', player.time_pos)
        gevent.sleep(t)

def start_sleeper(song):
    return gevent.spawn(sleep, song.length, next_song)

timer = gevent.spawn(keep_time, 0.5)

