from mutagen import File

def get_metadata(filename):
    audio = File(filename, easy=True)
    mdata = {}
    mdata['title'] = audio['title'][0]
    mdata['album'] = audio['album'][0]
    mdata['artist'] = audio['artist'][0]
    return mdata
