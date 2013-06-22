#This file contains a layer of abstraction on top of mplayer.py that
#lets it work nicely with the playlist stored in the cache.

from app import app, cache, player, metaplayer, db, sleeper
from werkzeug import secure_filename
from os.path import join
from time import time
from models import Song
import sockets
import gevent

def get_metadata(filename_list, orig_filenames=None):
    """
    Gets the metadata from id3 tags in a list of mp3 file paths.
    if orig_filnames (a list of original filenames) is passed,
    it will try to extract a track number and title from them as
    a fallback."""
    mdatas = []
    tags = (('title','Title'),
            ('artist','Artist'),
            ('album','Album'),
            ('track','Track'),
            ('year','Year','date','Date'))
    for i, filename in enumerate(filename_list):
        mdata = {}
        metaplayer.loadfile(filename)
        metadata = metaplayer.metadata
        try: name = orig_filenames[i]
        except: name = metaplayer.filename
        if metadata == None:
            mdata['none'] = True
        else:
            for tag_set in tags:
                for tag in tag_set:
                    if not mdata.get(tag_set[0]):
                        mdata[tag_set[0]] = metadata.get(tag, '')
        guess_track, guess_title = guess_song_title(name)
        if not mdata.get('title',''): mdata['title'] = guess_title
        if not mdata.get('track',''): mdata['track'] = guess_track
        if type(mdata['track']) == type(u'') or \
                type(mdata['track']) == type(''):
            mdata['track'] = mdata['track'].split('/')[0]
        try:
            mdata['track'] = int(mdata['track'])
        except ValueError: pass
        except TypeError: mdata['track'] = ''
        mdata['extension'] = name.split('.')[-1].lower()
        mdata['length'] = metaplayer.length
        mdatas.append(mdata)
    return mdatas

def guess_song_title(filename):
    """ Tries to pull out the title and track number."""
    first_pass = ' '.join(filename.split('.')[:-1]).replace('_',' ')
    try:
        track_num = int(first_pass.split(' ')[0])
        title = ' '.join(first_pass.split(' ')[1:])
    except:
        track_num = None
        title = first_pass
    return track_num, title

def guess_album_and_artist(metadatas):
    """
    Get the most common album and artist from a list of
    possibly incomplete metadata objects."""
    albums, artists = {}, {}
    for metadata in metadatas:
        album = metadata.get('album','')
        artist = metadata.get('artist','')
        albums[album] = albums.get(album, 0) + 1
        artists[artist] = artists.get(artist, 0) + 1
    if albums: album = max(albums)
    else: album = ''
    if artists: artist = max(artists)
    else: artist = ''
    return album, artist

def get_path_from_song(song):
    """Retrieve the stored location of a song from it's database model."""
    path = join(app.config['MUSIC_DIR'],
                secure_filename(song.artist.name),
                secure_filename(song.album.title),
                secure_filename(song.title + '.' + song.extension))
    return path

def append_song_to_playlist(song):
    """Append a song to the playlist and play it if the playlist is empty."""
    global sleeper
    current, playlist = get_playlist()
    if not playlist and not current:
        path = get_path_from_song(song)
        player.loadfile(path)
        song.plays += 1
        current = song.id
        sleeper = start_sleeper(song.length)
    else:
        playlist = playlist + [song.id]
    cache.set('playlist', playlist)
    cache.set('current', current)
    return current, playlist

def get_playlist():
    """Get the primary keys of the songs in the current playlist"""
    current = cache.get('current')
    playlist = cache.get('playlist')
    if playlist == None:
        playlist = []
        cache.set('playlist', playlist)
        #playlist = []
    return current, playlist

def next_song():
    """Start the next song playing and update the playlist."""
    global sleeper
    old_sleeper = sleeper
    current, playlist = get_playlist()
    try:
        current = playlist.pop(0)
        song = Song.query.filter_by(id=current).first()
        song.plays += 1
        path = get_path_from_song(song)
        player.loadfile(path)
        db.session.commit()
        sleeper = start_sleeper(song.length)
    except:
        current = None;
        player.stop();
    cache.set('current',current)
    cache.set('playlist', playlist)
    sockets.UpdateNamespace.broadcast('update', {'current':current, 'playlist':playlist})
    old_sleeper.kill()


def pause():
    """Pause the playlist if playing."""
    if not player.paused:
        sleeper.kill()
        player.pause()

def play():
    """Play the music if currently paused."""
    global sleeper
    if player.paused:
        sleeper = start_sleeper(player.length - player.time_pos)
        player.pause()

def change_volume(step):
    """Change the player's volume by the specified step."""
    cur_volume = player.volume
    if cur_volume == None: return
    volume = cur_volume + step
    if volume > 100: volume = 100
    if volume < 0: volume = 0
    player.volume = volume
    return volume

def get_time():
    """gets mplayer's position in the current song"""
    return player.time_pos

def start_sleeper(length):
    """
    Starts a new greenlet that will wait for the specified time
    and then start the next song. Used for playlist management."""
    return gevent.spawn(sleep, length, next_song)

def sleep(sleep, action):
    """
    Wait the specified time in the current greenlet, then run the
    specified action."""
    gevent.sleep(sleep)
    action()
