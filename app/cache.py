from app import app, cache
from models import Song

def get_playlist():
    current = cache.get('current')
    playlist = cache.get('playlist')
    if playlist == None:
        playlist = [song.id for song in Song.query.all()]
        cache.set('playlist', playlist)
        #playlist = []
    return current, playlist

def next_song():
    current, playlist = get_playlist()
    try:
        current = playlist.pop(0)
    except:
        current = None;
    cache.set('current',current)
    cache.set('playlist', playlist)
    return current, playlist
