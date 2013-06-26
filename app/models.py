from app import db

class dud():
    """A simple object that can pick up any random attributes"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128), index = True, unique = True)
    albums = db.relationship('Album', backref = 'artist')
    songs = db.relationship('Song', backref = 'artist')

    def __repr__(self):
        return '<Artist %r>' %self.name

class Album(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(128), index = True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    songs = db.relationship('Song', backref = 'album')

    def __repr__(self):
        return '<Album %r by %r>' %(self.title, self.artist.name)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(128), index = True)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    extension = db.Column(db.String(5))
    length = db.Column(db.Float)
    plays = db.Column(db.Integer, default=0)
    track = db.Column(db.Integer)
    def __repr__(self):
        return '<Song %r by %r (%d:%d)>' %(self.title, self.artist.name,
                                           int(self.length / 60), 
                                           int(self.length % 60))
