#Does all the hard work of communicating with the frontend
#and dealing with it's input.

from app import app, cache, console
from flask import request, Response, render_template
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from music import get_playlist, next_song
import music
from models import Song, Artist, Album

class UpdateNamespace(BaseNamespace):
    """
    The namespace that deals with updates from the app's frontend.
    It keeps a list of connected sockets so it can broadcast updates
    to the playlist.
    Currently the only namespace."""
    sockets = {}
    
    def recv_connect(self):
        """Connect up a new client"""
        #print "Got a socket connection!"
        self.sockets[id(self)] = self
    
    def disconnect(self, *args, **kwargs):
        """Disconnect a client"""
        #print "A socket disconnected!"
        if id(self) in self.sockets:
            del self.sockets[id(self)]
        super(UpdateNamespace, self).disconnect(*args, **kwargs)

    def on_move(self, data):
        """Move a song around in the playlist."""
        current, playlist = get_playlist()
        to = data['to']
        playlist.insert(int(data['to']),
                        playlist.pop(playlist.index(int(data['from']))))
        cache.set('playlist', playlist)
        self.broadcast('update', {'current':current, 'playlist':playlist})
    
    def on_pause(self):
        music.pause()
        self.broadcast('pause')
    
    def on_play(self):
        music.play()
        self.broadcast('play')
    
    def on_volume(self, data):
        print data
        step = (5 if data == 'up' else -5)
        volume = music.change_volume(step)
        self.broadcast('volume', volume)
    
    def on_next(self):
        next_song()
    
    def on_delete(self, data):
        """Deletes a song from the playlist."""
        current, playlist = get_playlist()
        playlist.pop(playlist.index(int(data['who'])))
        cache.set('playlist', playlist)
        self.broadcast('update', {'current':current, 'playlist':playlist})
        
    def on_add(self, data):
        """Adds a new song to the playlist by primary key"""
        current, playlist = get_playlist()
        if int(data['who']) not in playlist + [current]:
            current, playlist = music.append_song_to_playlist(Song.query.filter_by(id=int(data['who'])).first())
            self.broadcast('update', {'current':current, 'playlist':playlist})
        else:
            self.emit('error', 'That song is already on the playlist!')

    def on_current_request(self):
        """
        Returns the html for the current song, ready to plop into
        the music player."""
        current, playlist = get_playlist()
        current = Song.query.filter_by(id=current).first()
        sketchy_ctx = app.test_request_context()
        sketchy_ctx.push()
        self.emit('current_data', render_template('current_bar.html', current=current, played=music.get_time()))
        sketchy_ctx.pop()
    
    def on_song_request(self, pk):
        """Returns the html for a song, ready to go into a playlist"""
        song = Song.query.filter_by(id=pk).first()
        sketchy_ctx = app.test_request_context()
        sketchy_ctx.push()
        self.emit('song_data', render_template('music_bar.html', song=song))
        sketchy_ctx.pop()

    def on_match(self, data):
        """Looks for a match for a given search request."""
        current, playlist = get_playlist()
        playlist.append(current)
        response = {}
        if data['what'] == 'song' or data['what'] == 'all':
            songs = Song.query.filter(Song.title.ilike('%%%s%%' %data['query']))
            exclusion = Song.query.filter(Song.id.in_(playlist))
            songs = songs.except_(exclusion).order_by(Song.plays.desc())\
                .limit(5).all()
            songs = [(song.id, song.title, song.artist.name) for song in songs]
            response['songs'] = songs

        if data['what'] == 'artist' or data['what'] == 'all':
            artists = Artist.query.filter(Artist.name.ilike('%%%s%%' %data['query'])).limit(3).all()
            artists = [(artist.id, artist.name) for artist  in artists]
            response['artists'] = artists

        if data['what'] == 'album' or data['what'] == 'all':
            albums = Album.query.filter(Album.title.ilike('%%%s%%' %data['query'])).limit(3).all()
            albums = [(album.id, album.title, album.artist.name) for album  in albums]
            response['albums'] = albums

        if data['what'] == 'by_artist':
            artist = data.get('artist','').strip(' ')
            songs = Song.query.join(Artist).filter(Artist.name.ilike(artist))\
                        .filter(Song.title.ilike('%%%s%%' %data['query']))
            exclusion = Song.query.filter(Song.id.in_(playlist))
            songs = songs.except_(exclusion).order_by(Song.plays.desc()).all()
            songs = [(song.id, song.title, song.artist.name) for song in songs]
            response['songs'] = songs

            albums = Album.query.join(Artist).filter(Artist.name.ilike(artist))\
                        .filter(Album.title.ilike('%%%s%%' %data['query']))
            albums = [(album.id, album.title, album.artist.name) for album in albums]
            response['albums'] = albums
        

        if data['what'] == 'by_album':
            album = data.get('album','').strip(' ')
            songs = Song.query.join(Album).filter(Album.title.ilike(album))\
                        .filter(Song.title.ilike('%%%s%%' %data['query']))
            exclusion = Song.query.filter(Song.id.in_(playlist))
            songs = songs.except_(exclusion).order_by(Song.track).all()
            songs = [(song.id, song.title, song.artist.name) for song in songs]
            response['songs'] = songs
        self.emit('search_results', response)
    
    #Broadcast to all sockets on this channel
    @classmethod
    def broadcast(self, event, *args):
        """broadcasts an event to everybody who's connected"""
        for ws in self.sockets.values():
            ws.emit(event, *args)

@app.route('/socket.io/<path:rest>')
def push_stream(rest):
    try:
        socketio_manage(request.environ, {'/updates/':UpdateNamespace}, request)
    except:
        app.logger.error("Exception while handling socket.io connection",
                         exc_info=True)
    return Response('')

