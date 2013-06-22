#Defines all the forms used on the site

from flask.ext.wtf import Form, TextField, FileField, FieldList, FormField, IntegerField
from flask.ext.wtf import Required, ValidationError
from wtforms.widgets import HiddenInput

class MultiFileField(FileField):
    def process_formdata(self, formdata):
        if formdata:
            self.data = formdata

MUSIC_FILETYPES = ['mp3', 'm4a', 'flac', 'aac', 'ac3']

#These check that the music is of an accepted filetype.
def validate_music(form, field):
    if field.data.filename.split('.')[-1].lower() not in MUSIC_FILETYPES:
        raise ValidationError('Invalid filetype.')

def validate_multi_music(form, multi_field):
    for datum in multi_field.data:
        if datum.filename.split('.')[-1] not in MUSIC_FILETYPES:
            raise ValidationError('One or more songs has an invalid filetype')

#These are for posting the actual song files
class PostSongForm(Form):
    song = FileField('song', validators = [Required(), validate_music]) 

class PostAlbumForm(Form):
    songs = MultiFileField('songs', validators = [Required(), validate_multi_music])

#These are for comfirming the song's metadata
class SongDataForm(Form):
    filename = TextField('filename', validators = [Required()], widget=HiddenInput())
    artist = TextField('artist', validators = [Required()])
    album = TextField('album', validators = [Required()])
    song = TextField('song', validators = [Required()])

class AlbumSongDataForm(Form):
    filename = TextField('filename', validators = [Required()], widget=HiddenInput())
    song = TextField('song', validators = [Required()])
    track = IntegerField('track')
    
class AlbumDataForm(Form):
    artist = TextField('artist', validators = [Required()])
    album = TextField('album', validators = [Required()])
    uploads = FieldList(FormField(AlbumSongDataForm))
