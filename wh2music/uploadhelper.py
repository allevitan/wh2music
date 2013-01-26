import models

def gomArtist(artist):
    try:
        artist = models.Artist.objects.get(name__iexact=artist)
    except:
        artist = models.Artist.objects.create(name=artist)
        artist.save()
    return artist

def gomAlbum(album, artist):
    try:
        album = models.Album.objects.filter(name__iexact=album).get(artist=artist)
    except:
        album = models.Album.objects.create(name=album, artist=artist)
        album.save()
    return album

def makeSong(name, album, music):
    song = models.Song.objects.create(name=name, album=album, song=music)
    song.save()

def exists(song, album, artist):
    numhits = models.Song.objects.filter(name__iexact=song).filter(album__name__iexact=album).filter(album__artist__name__iexact=artist).count()
    if numhits == 0:
        return False
    else: return True

def uploadTo(instance, filename):
    extension = filename.split('.')[-1]
    return "%s/%s/%s.%s" %(instance.album.artist.name,
                           instance.album.name,
                           instance.name,
                           extension)
