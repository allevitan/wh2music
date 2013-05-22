from app import app, db, cache
from flask import render_template, redirect, url_for, request, send_from_directory, abort, jsonify
import os
from shutil import move
from werkzeug import secure_filename
from werkzeug.wrappers import Response
from random import random
from time import time, sleep
from forms import PostSongForm, SongDataForm, MultiSongDataForm
from models import Artist, Album, Song, dud
from metadata import get_metadata

def get_playlist():
    current = cache.get('current')
    playlist = cache.get('playlist')
    if playlist == None:
        playlist = [song.id for song in Song.query.all()]
        cache.set('playlist', playlist)
        #playlist = []
    return current, playlist

@app.route('/')
def home():
    current, playlist = get_playlist()
    playlist = [Song.query.filter_by(id=pk).first() for pk in playlist]
    current = Song.query.filter_by(id=current).first()
    form = PostSongForm()
    return render_template('home.html', form=form, current=current,
                           playlist=playlist)

@app.route('/music/<filename>')
def get_song(filename):
    return send_from_directory(app.config['MUSIC_DIR'], filename)

@app.route('/post_song/', methods=['GET','POST'])
def post_song():
    """The frst step in uploading songs, it takes in files posted by
    the user, stores them in a temporary directory, and ask the user
    to confirm that the automatically pulled metadata is correct"""

    files =  request.files.getlist('song')
    #form = PostSongForm(MultiDict([('song',files[0])]))
    form = PostSongForm()
    if not form.validate():
        print 'invalid!'
        abort(403)

    #Create a unique batch directory in the temp folder
    while not 'batch_name' in locals() or \
        os.path.exists(os.path.join(app.config['TEMP_DIR'], batch_name)):
        batch_name = str(int(random() * 10**16))
    os.makedirs(os.path.join(app.config['TEMP_DIR'], batch_name))

    #Generate appropriate form with correct default data, one row per song
    confirm_form = MultiSongDataForm()
    for song in form.song.data:
        filename = secure_filename(song.filename)
        path = os.path.join(app.config['TEMP_DIR'],
                                batch_name, filename)

        song.save(path)
        metadata = get_metadata(path)
        #add the new row, using dud as an object with the wirght attributes
        confirm_form.uploads.append_entry(dud(song=metadata.get('title',''),
                                          album = metadata.get('album',''),
                                          artist = metadata.get('artist',''),
                                          filename = filename))

    return render_template('song_uploader.html', batch_name=batch_name, form=confirm_form, step='check')


@app.route('/confirm_song/<batch_name>', methods=['POST'])
def confirm_song(batch_name):
    """The last step in uploading a song, it takes a form filled with song
    metadata and puts the music in the database"""
    form = MultiSongDataForm(request.form)
    if not form.validate():
        print 'invalid!'
        abort(403)
    for upload in form.uploads.data:
        print upload
        artist = Artist.query.filter_by(name=upload['artist']).first()
        if not artist:
            artist = Artist(name=upload['artist'])
            db.session.add(artist)
        album = Album.query.filter(Album.title==upload['album'],
                                   Album.artist==artist).first()
        if not album:
            album = Album(title=upload['album'], artist=artist)
            db.session.add(album)
        song = Song.query.filter(Song.title==upload['song'],
                                 Song.album==album,
                                 Song.artist==artist).first()
        if not song:
            song = Song(title=upload['song'], artist=artist, album=album)
            db.session.add(song)
        source = os.path.join(app.config['TEMP_DIR'],
                              batch_name, secure_filename(upload['filename']))
        destination = os.path.join(app.config['MUSIC_DIR'],
                               secure_filename(artist.name),
                               secure_filename(album.title))
        extension = upload['filename'].split('.')[-1]
        if not os.path.exists(destination):
            os.makedirs(destination)
        move(source, os.path.join(destination, secure_filename(song.title + '.' + extension)))
        db.session.commit()

    os.rmdir(os.path.join(app.config['TEMP_DIR'],batch_name))

    form = PostSongForm(formdata = None)
    return render_template('song_uploader.html', form=form, uploaded=True)

@app.route('/play/')
def play():
    #p.pause()
    return Response(status=204)

@app.route('/pause/')
def pause():
    #p.pause()
    return Response(status=204)

@app.route('/next/')
def next():
    current, playlist = get_playlist()
    cache.set('current',playlist.pop(0))
    cache.set('playlist', playlist)
    cache.set('latest', time())
    return redirect(url_for('changes'))

@app.route('/update/', methods=['GET','POST'])
def update():
    current, playlist = get_playlist()

    if request.form['type'] == 'update':
        to = request.form['to']
        playlist.insert(int(request.form['to']),
                        playlist.pop(playlist.index(int(request.form['from']))))
        cache.set('playlist', playlist)
    elif request.form['type'] == 'add':
        cache.set('playlist', playlist + [int(request.form['add'])])
    elif request.form['type'] == 'del':
        playlist.pop(playlist.index(int(request.form['del'])))
        cache.set('playlist', playlist)
    else: abort(403);
    cache.set('latest',time())
    return Response(status=204)

@app.route('/last_update/')
def last_update():
    try:
        latest = time() - cache.get('latest')
    except:
        cache.set('latest', time())
        latest = time() - cache.get('latest')
    return jsonify(latest=latest)

@app.route('/playlist/')
def changes():
    current, playlist = get_playlist()
    playlist = [Song.query.filter_by(id=pk).first() for pk in playlist]
    playlist = [song.id for song in playlist]
    return jsonify(current=current, playlist=playlist)

@app.route('/music_bar/<pk>/')
def music_bar(pk):
    Song = Song.query.filter_by(id=pk).first()
    return render_template('music_bar.html', song=song)

@app.route('/current_song/')
def current_song():
    current, playlist = get_playlist()
    current = Song.query.filter_by(id=current).first()
    return render_template('current_bar.html', current=current)
