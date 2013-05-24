from app import app, cache
from flask import request, Response, render_template
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from console import console #for shits and giggles
from music import get_playlist, next_song
import music
from models import Song

class UpdateNamespace(BaseNamespace):
    sockets = {}
    
    def recv_connect(self):
        #print "Got a socket connection!"
        self.sockets[id(self)] = self
    
    def disconnect(self, *args, **kwargs):
        #print "A socket disconnected!"
        if id(self) in self.sockets:
            del self.sockets[id(self)]
        super(UpdateNamespace, self).disconnect(*args, **kwargs)

    def on_move(self, data):
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
    
    def on_next(self):
        next_song()
    
    def on_delete(self, data):
        current, playlist = get_playlist()
        playlist.pop(playlist.index(int(data['who'])))
        cache.set('playlist', playlist)
        self.broadcast('update', {'current':current, 'playlist':playlist})
        
    def on_add(self, data):
        current, playlist = get_playlist()
        if int(data['who']) not in playlist + [current]:
            current, playlist = music.append_song_to_playlist(Song.query.filter_by(id=int(data['who'])).first())
            self.broadcast('update', {'current':current, 'playlist':playlist})
        else:
            self.emit('error', 'That song is already on the playlist!')

    def on_current_request(self):
        current, playlist = get_playlist()
        current = Song.query.filter_by(id=current).first()
        sketchy_ctx = app.test_request_context()
        sketchy_ctx.push()
        self.emit('current_data', render_template('current_bar.html', current=current, played=cache.get('played')))
        sketchy_ctx.pop()
    
    def on_song_request(self, pk):
        song = Song.query.filter_by(id=pk).first()
        sketchy_ctx = app.test_request_context()
        sketchy_ctx.push()
        self.emit('song_data', render_template('music_bar.html', song=song))
        sketchy_ctx.pop()

    def on_match(self, data):
        current, playlist = get_playlist()
        playlist.append(current)
        if data['what'] == 'song' or data['what'] == 'all':
            songs = Song.query.filter(Song.title.ilike('%%%s%%' %data['query'])).limit(len(playlist) + 5).all()
            songs = [(song.title, song.artist.name, song.id) for song in songs
                     if song.id not in playlist]
            self.emit('search_results', songs[:5])
    
    #Broadcast to all sockets on this channel
    @classmethod
    def broadcast(self, event, *args):
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

