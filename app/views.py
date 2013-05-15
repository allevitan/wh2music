from app import app, db
from flask import render_template, redirect, url_for, request, send_from_directory
import os
from shutil import move
from werkzeug import secure_filename
from forms import PostSongForm, SongDataForm
from models import Artist, Album, Song
from metadata import get_metadata

@app.route('/')
def home():
    songs = Song.query.all()
    form = PostSongForm()
    return render_template('home.html', form=form, songs=songs)

@app.route('/music/<filename>')
def get_song(filename):
    return send_from_directory(app.config['MUSIC_DIR'], filename)

@app.route('/post_song/', methods=['POST'])
def post_song():
    form = PostSongForm()
    if not form.validate():
        return redirect(url_for('home'))
    song = form.song.data
    filename = os.path.join(app.config['TEMP_DIR'],
                            secure_filename(form.song.data.filename))
    song.save(filename)
    metadata = get_metadata(filename)
    confirm_form = SongDataForm(formdata=None,song=metadata.get('title',''),
                                album = metadata.get('album',''),
                                artist = metadata.get('artist',''))
    return render_template('song_data.html', filename=filename.split('/')[-1], form=confirm_form)

@app.route('/confirm_song/<filename>', methods=['POST'])
def confirm_song(filename):
    form = SongDataForm()
    if form.validate():
        artist = Artist.query.filter_by(name=form.artist.data).first()
        if not artist:
            artist = Artist(name=form.artist.data)
            db.session.add(artist)
        album = Album.query.filter(Album.title==form.album.data,
                                   Album.artist==artist).first()
        if not album:
            album = Album(title=form.album.data, artist=artist)
            db.session.add(album)
        song = Song.query.filter(Song.title==form.song.data,
                                 Song.album==album,
                                 Song.artist==artist).first()
        if not song:
            song = Song(title=form.song.data, artist=artist, album=album)
            db.session.add(song)
        source = os.path.join(app.config['TEMP_DIR'],
                                secure_filename(filename))
        destination = os.path.join(app.config['MUSIC_DIR'],
                                secure_filename(artist.name), 
                                secure_filename(album.title))
        extension = filename.split('.')[-1]
        if not os.path.exists(destination):
            os.makedirs(destination)
        move(source, os.path.join(destination, secure_filename(song.title + extension)))
        db.session.commit()
        
    return redirect(url_for('home'))
