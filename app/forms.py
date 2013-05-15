from flask.ext.wtf import Form, TextField, FileField
from flask.ext.wtf import Required, ValidationError

MUSIC_FILETYPES = ['mp3']

def validate_music(form, field):
    if field.data.filename.split('.')[-1] not in MUSIC_FILETYPES:
        raise ValidationError('Invalid filetype.')
        
class PostSongForm(Form):
    song = FileField('song', validators = [Required(), validate_music])

class SongDataForm(Form):
    artist = TextField('artist', validators = [Required()])
    album = TextField('album', validators = [Required()])
    song = TextField('song', validators = [Required()])
