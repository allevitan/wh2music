window.sendAndConfirm = (url)->
    data = new FormData $('.post-song')[0]
    initializeSlider()
    $.ajax
        type: 'POST'
        url: url
        data: data
        xhr: () ->
            progressXhr = $.ajaxSettings.xhr()
            if progressXhr.upload
                progressXhr.upload.addEventListener('progress', (e)->
                    updateProgress (e.loaded / e.total * 100)
                )
            return progressXhr
        error: (xhr, type, e) -> console.log(e)
        success: (data)->
            $('#upload').remove()
            $('#uploads').removeClass('hide')
            $('#playlist').addClass('hide')
            $('.well').append(data)
        cache: false
        contentType: false
        processData: false

initializeSlider = () ->
    $('#uploads').addClass('hide').after('<div id="upload"><div id="slider"></div></div>')

updateProgress = (complete) ->
    if complete == 100
        $('#upload').append('<p>Processing...</p>')
        $('#upload > #slider').css('width', complete + '%')

window.sendConfirmData = (url) ->
    data = new FormData $('.post-song')[0]
    $.ajax
        type: 'POST'
        url: url
        data: data
        success: (data)->
            $('#playlist').removeClass('hide');
            $('#uploadbox').remove();
        cache: false
        contentType: false
        processData: false