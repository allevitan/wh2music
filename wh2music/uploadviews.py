from django.shortcuts import render
from forms import songForm
from django.http import HttpResponse, HttpResponseRedirect
import uploadhelper

def upload(request):
    form = songForm()
    if request.method == 'POST':
        form = songForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            if not uploadhelper.exists(data['song'], data['album'], data['artist']):
                artist = uploadhelper.gomArtist(data['artist'])
                album = uploadhelper.gomAlbum(data['album'], artist)
                song = uploadhelper.makeSong(data['song'], album, data['music'])
            return HttpResponseRedirect('/play/')
        else:
            return render(request,'upload/form.html', {'form':form})
    else:
        return render(request,'upload/form.html', {'form':form})
