from mutagen import File

def get_metadata(filename):
    audio = File(filename, easy=True)
    mdata = {}
    mdata['title'] = audio['title'][0]
    mdata['album'] = audio['album'][0]
    mdata['artist'] = audio['artist'][0]
    #we'll use what mutagen thinks the file is, not the original extension
    mdata['extension'] = audio.__module__.split('.')[-1]
    mdata['length'] = audio.info.length
    return mdata
