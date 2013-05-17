from flask.ext.wtf import Form, TextField, FileField, FieldList, FormField
from flask.ext.wtf import Required, ValidationError
from wtforms.widgets import HiddenInput

class MultiFileField(FileField):
    def process_formdata(self, formdata):
        if formdata:
            self.data = formdata

MUSIC_FILETYPES = ['mp3']

def validate_music(form, field):
    if field.data.filename.split('.')[-1] not in MUSIC_FILETYPES:
        raise ValidationError('Invalid filetype.')

def validate_multi_music(form, multi_field):
    for datum in multi_field.data:
        if datum.filename.split('.')[-1] not in MUSIC_FILETYPES:
            raise ValidationError('One or more songs has an invalid filetype')

class PostSongForm(Form):
    song = MultiFileField('song', validators = [Required(), validate_multi_music])

class SongDataForm(Form):
    filename = TextField('filename', validators = [Required()], widget=HiddenInput())
    artist = TextField('artist', validators = [Required()])
    album = TextField('album', validators = [Required()])
    song = TextField('song', validators = [Required()])

class MultiSongDataForm(Form):
    uploads = FieldList(FormField(SongDataForm))
