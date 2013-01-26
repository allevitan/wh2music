from django.db import models
import uploadhelper

class Artist(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name

class Album(models.Model):
    name = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist)
    
    def __unicode__(self):
        return "%s by %s" %(self.name, self.artist.name)

class Song(models.Model):
    name = models.CharField(max_length=200)
    song = models.FileField(upload_to=uploadhelper.uploadTo)
    album = models.ForeignKey(Album)
    
    def __unicode__(self):
        return "%s by %s on %s" %(self.name, self.album.artist.name, self.album.name)
