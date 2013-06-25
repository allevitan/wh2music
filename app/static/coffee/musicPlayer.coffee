$(window).resize -> fillScreen()

$(document).ready ()->
    fillScreen()

    #Get the interactivity going
    sortable '.music-bar', '#playlist'
    deletable '.music-bar'
    searchable '#song-search'
    
    $(document).on 'keydown', volumize
    window.socket = io.connect '/updates/'
    
    #Handle all the push communications from the server
    socket.on 'update', (data)-> updatePlaylist data
    socket.on 'current_data', (html)-> updateCurrent html
    socket.on 'search_results', (results)-> refreshResults results
    socket.on 'error', (error)-> alert error
    socket.on 'time', (time)->
        console.log 'server update!'
        updateTime '#time', time
    socket.on 'volume', (data)-> console.log data
    socket.on 'play',  ()-> startTiming '#time'
    socket.on 'pause', stopTiming
    $("#next").click () -> socket.emit 'next'
    startTiming '#time'


#sets up the volume up and down hotkeys
volumize = (keyEvent)->
    if keyEvent.ctrlKey and keyEvent.shiftKey and keyEvent.which==190
        socket.emit 'volume', 'up'
    else if keyEvent.ctrlKey and keyEvent.shiftKey and keyEvent.which==188
        socket.emit 'volume', 'down'

#Start the music playback timer running
startTiming = (timeable)->
    window.playing = true
    $("#pause").off('click').click ()-> socket.emit 'pause'
    window.timing = setInterval ->
        min = parseInt $(timeable).children(' #min').text() * 60
        sec = parseInt $(timeable).children('#sec').text()
        return null if isNaN(min) or isNaN(sec)
        time = min + sec + 1
        updateTime timeable, time
    , 1000

#Stops the music playback timer
stopTiming = ->
    window.playing = false
    $("#pause").off('click').click ->
        socket.emit 'play'
    clearInterval window.timing

#Sets the value in the music timer based on a time in seconds
updateTime = (timeable, time)->
    $(timeable).children('#min').text Math.floor(time/60)
    sec = time % 60
    sec = '0' + sec if sec < 10 
    $(timeable).children('#sec').text sec

#Takes a set of things that should be deletable, and makes it so
deletable = (deletable)->
    $(deletable + ' .del-button').off('mousedown').mousedown (e)->
        socket.emit 'delete', who:$(this).parent().attr 'pk'
        e.stopPropagation()

#Takes the search box and sets it up to work with results.
searchable = (searchable)->
    $('#results').click -> $(searchable).focus()
    $(searchable).click ->
        $('#results').addClass 'open' if $(searchable).attr 'value'
        return false
    $(searchable).on 'keypress', (e)->
        $('#results').addClass 'open'
        query = $(searchable).attr 'value'
        start = this.selectionStart ? query.length
        end = this.selectionEnd ? start
        key = e.which
        query = query[0...start] + query[end..] if start isnt end
        query = query[0...start] + String.fromCharCode(key) + query[start..]
        sendQuery query
    
    $(searchable).on 'keydown', (e)->
        key = e.which
        query = $(searchable).attr('value');
        me = $('#results .selected')
        switch key
            when 13
                sendSelection me if me.length is 1
                return false
            when 38
                next = me.prev()
                while next.hasClass 'break'
                    next = next.prev()
            when 40
                next = me.next()
                while next.hasClass 'break'
                    next = next.next()
        if next? and next.length is 1
            me.removeClass 'selected'
            next.addClass 'selected'
            return false
        return true if key != 8 and key != 46
        if query.length <= 1
            $('#results').removeClass 'open'
            return true
        start = this.selectionStart ? query.length
        end = this.selectionEnd ? start
        if start isnt end
            query = query[0...start] + query[end..] 
        else
            query = query[0...(start-1)] + query[end..] if key is 8
            query = query[0...start] + query[(end+1)..] if key is 46 
        sendQuery query
    

#Takes the stuff in the search box, formats a search request, and
# #Sends it to the server.
sendQuery = (query)->
    artist_reg = /artist:[^\|]*/i
    artist_match = artist_reg.exec query
    album_reg = /album:[^\|]*/i
    album_match = album_reg.exec query
    if artist_match && !album_match
        artist = artist_match[0].split(':')[1..].join ':'
        query = query.replace(artist_reg, '').replace /\|\s*/, ''
        socket.emit 'match', {what:'by_artist', query:query, artist:artist}
    if album_match
        album = album_match[0].split(':')[1..].join ':'
        query = query.replace(album_reg, '').replace /\|\s*/, ''
        socket.emit 'match', {what:'by_album', query:query, album:album}
    if not (artist_match or album_match)
        socket.emit 'match', {what:'all', query:query}

#Takes the results pane and makes it selectable with the mouse
selectable = (selectable)->
    selectable.on 'mouseenter', ->
        selectable.removeClass 'selected'
        $(this).addClass 'selected'
    $(document).on 'click', -> $('#results').removeClass 'open'
    selectable.on 'click', (e)->
        me = $('#results .selected')
        sendSelection me if me

# Takes the class of a set of click-and-drag sortable objects,
# and makes it so
sortable = (sortableClass, sortBox)->
    $(sortableClass).off('mousedown').mousedown (e)->
        me = $(this)
        center = me.height() / 2
        curZero = me.offset().top + center
        me.css('z-index', 10).addClass 'selected'
        $(sortBox).bind 'mousemove', (e)->
            #for zepto compatibility (it's got no pageY)
            e.pageY = e.pageY ? e.y + $('body').scrollTop()
            above = me.siblings '[pos="' + (parseInt(me.attr('pos')) - 1) + '"]'
            below = me.siblings '[pos="' + (parseInt(me.attr('pos')) + 1) + '"]'
            if above.length and e.pageY - 1.5*center <= above.offset().top
                curZero = above.offset().top + center
                above.before me
                above.swap(me, 'pos').toggleClass 'greyed'
            else if below.length and e.pageY - 0.5*center >= below.offset().top
                curZero = below.offset().top + center
                below.after me
                below.swap(me, 'pos').toggleClass 'greyed'
            me.css top: e.pageY - curZero + 'px'
        
        $(document).mouseup ->
            me.css({'z-index':1,'top':0}).removeClass 'selected'
            shouldBeGreyed = parseInt(me.attr('pos')) % 2 is 0
            if (not shouldBeGreyed and me.hasClass 'greyed') or
                 shouldBeGreyed and not me.hasClass('greyed')
                me.toggleClass 'greyed'
            $(sortBox).unbind 'mousemove'
            $(document).unbind 'mouseup'
            socket.emit 'move', {from: me.attr('pk'), to: me.attr('pos')}

# Sends a selected item from the results pane to the server
sendSelection = (selection) ->
    if selection.hasClass 'song'
        socket.emit 'add', who: parseInt(selection.attr 'pk')
        $('#results').empty().removeClass 'open'
        $('#song-search').get(0).value = ''
        return true
    else if selection.hasClass 'back'
        $('#results').empty().removeClass 'open'
        $('#song-search').get(0).value = ''
        return false
    else if selection.hasClass 'album'
        searchTerm = 'album: ' + selection.text().split(' by')[0] + ' | ';
    else if selection.hasClass 'artist'
        searchTerm = 'artist: ' + selection.text() + ' | '
    
    prev = $('#song-search').get(0).value.split('|').slice(0,-1).join '|'
    prev += '| ' if prev
    $('#song-search').get(0).value = prev + searchTerm
    sendQuery searchTerm
    return false

# Refreshes the results pane from an object containing songs,
# albums, and artists
refreshResults = (results)->
    select_match = $('#results .selected');
    select_match = [select_match.attr 'pk', select_match.text()]
    box = $('#results').empty()
    if results.songs?.length
        box.append '<li class="break">Songs</li>'
        for song in results.songs
            box.append('<li class="song" pk="' + song[0] + '">' + 
                song[1] + ' <small>by</small> ' +
                song[2] + '</li>')

    if results.artists?.length
        box.append '<li class="break">Artists</li>'
        for artist in results.artists
            box.append('<li class="artist" pk="' + artist[0] + '">' + 
                    artist[1] + '</li>')
    if results.albums?.length
        box.append '<li class="break">Albums</li>'
        for album in results.albums
            box.append('<li class="album" pk="' + album[0] + '">' + 
                    album[1] + ' <small>by</small> ' +
                    album[2] + '</li>')
    box.append '<li class="back">Back to Playlist</li>'
    selected = $('#results').children '[pk="' + select_match[0] + '"]'
    if selected.length
        selected = selected.filter ->
            $(this).text() is select_match[1]
    if not selected.length
        selected = $($('#results').children(':not(.break)').get(0))
    selected.addClass 'selected'
    selectable $('#results').children(':not(.break)')


#Updates the playlist from an up-to-date copy from the server
updatePlaylist = (data)->

    #Check if necessary and the send a request for a new current_bar
    current_pk = $('#current').attr('pk')
    socket.emit 'current_request' if parseInt(current_pk) isnt data.current
    
    getLocalPlaylist = ->
        selection = $('#playlist').children('.music-bar')
        pks = []
        selection.each -> pks.push(parseInt($(this).attr('pk')))
        return pks

    remote = data.playlist
    local = getLocalPlaylist()

    [finalSort, currentSort] = [[],[]]
    finalSort[pk] = i for pk, i in remote
    currentSort[pk] = i for pk, i in local

    [movements, deletions, additions] = [[],[],[]]
    deletions.push pk for pk in local when not finalSort[pk]?
    additions[pk] = i for pk, i in remote when not currentSort[pk]?
    movements[pk] = i for pk, i in remote when local[i] isnt pk and not additions[pk]?

    moveBars movements, deletions, additions, finalSort

# Updates the currently playing song with a snippet of html
updateCurrent =(html)->
    $('#time').remove()
    $('#current').animate {opacity:0},
        duration: 250,
        complete: ->
            $(this).replaceWith html 
            $('#current').css(opacity:0).animate {opacity:1}, 250

# Does the hard work of animating the moving playlist bars
moveBars = (movements, deletions, additions, finalSort)->
    time = 400
    parent = $ '#playlist'
    plist = $('#playlist').children '.music-bar'
    donified = 0
    required = 0
    for whereTo, pk in movements when whereTo?
        ++required
        bar = plist.filter '[pk="' + pk +  '"]'
        target = plist.filter('[pos="' + whereTo + '"]').offset().top - bar.offset().top;
        if whereTo%2 is 0
            bar.animate
                top: target
                backgroundColor: '#F0F0F0'
            ,
                duration:time
                complete: -> ++donified
        else
            bar.animate
                top: target
                backgroundColor: '#FFFFFF'
            ,
                duration:time
                complete: -> ++donified

    for pk in deletions
        ++required
        bar = plist.filter '[pk="' + pk + '"]'
        bar.animate
            opacity:0
        ,
            duration: 500
            complete: -> ++donified

    for whereTo, pk in additions when whereTo?
        ++required
        socket.once 'song_data', (html)->
            bar = $(html).appendTo parent
            if whereTo%2 is 0
                bar.addClass 'greyed'
            bar.css(opacity:0).animate
                opacity:1
            ,
                duration:500
                complete: -> ++donified
        socket.emit 'song_request', pk
    
    settle_once_done = ->
        if donified < required then setTimeout(settle_once_done, 50)
        else settle()

    settle = ->
        plist.filter('[pk="' + pk + '"]').remove() for pk in deletions

        #refresh selector
        plist = $('#playlist').children '.music-bar'
        #Using the zepto sortElements function, takes a comparator
        plist.sortElements (a,b)->
            if finalSort[parseInt($(a).attr('pk'))] > finalSort[parseInt($(b).attr('pk'))] then 1 else -1
        

        plist.css('top',0).attr 'pos', ->finalSort[parseInt($(this).attr 'pk')]
        plist.each ->
            if parseInt($(this).attr('pos'))%2 is 0
                $(this).addClass 'greyed'
            else $(this).removeClass 'greyed'
            $(this).attr 'style',''
        sortable '.music-bar', '#playlist'
        deletable '.music-bar'

    settle_once_done()


#Stretches the playlist area to fill the screen.
fillScreen = ->
    main = $ '#main'
    main.height $(window).height() - main.offset().top - $('#uploadbox').height() - 32
