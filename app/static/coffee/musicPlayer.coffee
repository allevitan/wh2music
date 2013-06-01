`
$(window).resize(fillScreen);

$(document).ready(function(){
    sortable('.music-bar', '#playlist');
    deletable('.music-bar');
    searchable('#song-search');
    fillScreen();
    $(document).on('keydown', volumize);
    window.socket = io.connect('/updates/');
    socket.on('update', function(data) {
	updatePlaylist(data);
    });
    socket.on('current_data', function(html) {
	updateCurrent(html);
    });
    socket.on('search_results', function(results) {
	refreshResults(results);
    });
    socket.on('error', function(error) {
	alert(error);
    });
    socket.on('time', function(time) {
	console.log('server update!');
	updateTime('#time', time);
    });
    socket.on('play', function(){
	startTiming('#time');
    });
    socket.on('pause', function(){
	stopTiming();
    });
    socket.on('volume', function(data){
	console.log(data);
    });
    $("#next").click(function(){
	socket.emit('next');
    });
    startTiming('#time');
});

function volumize(keyEvent){
    if (keyEvent.which==190 && keyEvent.ctrlKey && keyEvent.shiftKey){
	socket.emit('volume', 'up');
    } else if (keyEvent.which==188 && keyEvent.ctrlKey && keyEvent.shiftKey){
	socket.emit('volume', 'down');
    } else {return true;}
    return false;
}

function startTiming(timeable){
    window.playing = true;
    $("#pause").off('click').click(function(){
	socket.emit('pause');
    });
    window.timing = setInterval(function(){
	var min = parseInt($(timeable).children(' #min').text()) * 60;
	var sec = parseInt($(timeable).children('#sec').text());
	if (isNaN(min) || isNaN(sec))
	    return
	var time = min + sec + 1;
	updateTime(timeable, time);
    }, 1000);
}

function stopTiming(){
    window.playing = false;
    $("#pause").off('click').click(function(){
	socket.emit('play');
    });
    clearInterval(window.timing);
}

function updateTime(timeable, time){
    $(timeable).children('#min').text(Math.floor(time/60));
    sec = time % 60;
    sec = sec < 10 ? '0' + sec : sec ;
    $(timeable).children('#sec').text(sec);
}

function deletable(deletable){
    $(deletable + ' .del-button').off('mousedown').mousedown(function(e){
	socket.emit('delete', {who:$(this).parent().attr('pk')});
	e.stopPropagation();
    });
}

function searchable(searchable){
    $('#results').click(function(){$(searchable).focus();});
    $(searchable).click(function(){
	if ($(searchable).attr('value')){
	    $('#results').addClass('open');
	}
	return false;});
    $(searchable).on('keypress', function(e){
	$('#results').addClass('open')
	query = $(searchable).attr('value');
	var start = this.selectionStart || query.length;
	var end = this.selectionEnd || start;
	var key = e.which;
	if (start != end){
	    query = query.slice(0,start)
		+ query.slice(end);
	}
	query = query.slice(0,start)
	    + String.fromCharCode(key)
	    + query.slice(start);
	sendQuery(query);
    });
    $(searchable).on('keydown', function(e){
	var key = e.which;
	var query = $(searchable).attr('value');
	if (key == 13){
	    var me = $('#results .selected');
	    if (me)
		sendSelection(me);
	    return false;
	}
	if (key == 38){
	    var me = $('#results .selected');
	    var next = me.prev();
	    while (next.hasClass('break')){
		var next = next.prev();
	    }
	}
	if (key == 40){
	    var me = $('#results .selected');
	    var next = me.next();
	    while (next.hasClass('break')){
		var next = next.next();
	    }
	}
	if (next && next.length == 1){
	    me.removeClass('selected');
	    next.addClass('selected');
	    return false;
	}
	if (key != 8 && key != 46)
	    return true;
	if (query.length <= 1){
	    $('#results').removeClass('open')
	    return true
	}
	var start = this.selectionStart || query.length;
	var end = this.selectionEnd || start;
	if (start != end){
	    query = query.slice(0,start)
		+ query.slice(end);
	} else {
	    if (key == 8){
		query = query.slice(0,start - 1)
		    + query.slice(end);
	    } else if (key == 46){ 
		query = query.slice(0,start)
		    + query.slice(end + 1);
	    }
	}
	sendQuery(query);
    });
}

function sendQuery(query){
    var artist_reg = /artist:[^\|]*/i
    var artist_match = artist_reg.exec(query)
    var album_reg = /album:[^\|]*/i
    var album_match = album_reg.exec(query)
    if (artist_match && !album_match){
	var artist = artist_match[0].split(':').slice(1).join(':')
	var query = query.replace(artist_reg, '').replace(/\|\s*/,'')
	socket.emit('match', {what:'by_artist', query:query, artist:artist});
    }
    if (album_match){
	var album = album_match[0].split(':').slice(1).join(':')
	var query = query.replace(album_reg, '').replace(/\|\s*/,'')
	socket.emit('match', {what:'by_album', query:query, album:album});
    }
    if (!(artist_match || album_match)) {
	socket.emit('match', {what:'all', query:query});
    }
}

function selectable(selectable){
    selectable.on('mouseenter', function(){
	selectable.removeClass('selected');
	$(this).addClass('selected');
    });
    $(document).on('click', function(){
	$('#results').removeClass('open')
    });
    selectable.on('click', function(e){
	var me = $('#results .selected');
	if (me){
	    return sendSelection(me);
	}  
    });
}

function sortable(sortableClass, sortBox){
    $(sortableClass).off('mousedown').mousedown(function(e){
	var me = $(this);
	var center = me.height() / 2;
	var curZero = me.offset().top + center
	me.css('z-index', 10).addClass('selected');
	$(sortBox).bind('mousemove', function(e){
	    //zepto compatibility (no pageY)
	    e.pageY = e.pageY || e.y + $('body').scrollTop();
	    above = me.siblings('[pos="' + (parseInt(me.attr('pos')) - 1) + '"]');
	    below = me.siblings('[pos="' + (parseInt(me.attr('pos')) + 1) + '"]');
	    if (above.length && e.pageY - 1.5 * center <= above.offset().top){
		curZero = above.offset().top + center;
		above.before(me);
		above.swap(me, 'pos').toggleClass('greyed');
	    } else if (below.length && e.pageY - 0.5 * center >= below.offset().top){
		curZero = below.offset().top + center;
		below.after(me);
		below.swap(me, 'pos').toggleClass('greyed');
	    }
	    me.css({top: e.pageY - curZero + 'px'});
	    
	});
	$(document).mouseup(function(){
	    me.css({'z-index':1,'top':0}).removeClass('selected');
	    shouldBeGreyed = me.attr('pos') == 0 ? true : me.siblings('[pos="' + parseInt(me.attr('pos'))%2 + '"]').hasClass('greyed');
	    if (me.hasClass('greyed') ? !shouldBeGreyed : shouldBeGreyed){
		me.toggleClass('greyed');
	    }
	    $(sortBox).unbind('mousemove');
	    $(document).unbind('mouseup');
	    socket.emit('move', {from:me.attr('pk'), to:me.attr('pos')})
	});
    });
}

function sendSelection(selection){
    if (selection.hasClass('song')){
	socket.emit('add',{who:parseInt(selection.attr('pk'))});
	$('#results').empty().removeClass('open');
	$('#song-search').get(0).value = '';
	return true;
    } else if (selection.hasClass('back')){
	$('#results').empty().removeClass('open');
	$('#song-search').get(0).value = '';
	return false;
    } else if (selection.hasClass('album')){
	searchTerm = 'album: ' + selection.text().split(' by')[0] + ' | ';
    } else if (selection.hasClass('artist')){
	searchTerm = 'artist: ' + selection.text() + ' | '
    }
    prev = $('#song-search').get(0).value.split('|').slice(0,-1).join('|');
    if (prev){prev += '| ';}
    $('#song-search').get(0).value = prev + searchTerm;
    sendQuery(searchTerm);
    return false;
}

function refreshResults(results){
    var select_match = $('#results .selected');
    var select_match = [select_match.attr('pk'), select_match.text()];
    var box = $('#results').empty();
    if (results.songs && results.songs.length)
	box.append('<li class="break">Songs</li>');
    for (i in results.songs){
	box.append('<li class="song" pk="' + results.songs[i][0] + '">' + 
		   results.songs[i][1] + ' <small>by</small> ' +
		   results.songs[i][2] + '</li>');
    }
    if (results.artists && results.artists.length)
	box.append('<li class="break">Artists</li>');
    for (i in results.artists){
	box.append('<li class="artist" pk="' + results.artists[i][0] + '">' + 
		   results.artists[i][1] + '</li>');
    }
    if (results.albums && results.albums.length)
	box.append('<li class="break">Albums</li>');
    for (i in results.albums){
	box.append('<li class="album" pk="' + results.albums[i][0] + '">' + 
		   results.albums[i][1] + ' <small>by</small> ' +
		   results.albums[i][2] + '</li>');
    }
    box.append('<li class="back">Back to Playlist</li>')
    selected = $('#results').children('[pk="' + select_match[0] + '"]')
    if (selected.length){
	selected = selected.filter(function(){
	    return $(this).text() == select_match[1];
	});
    }
    if (!selected.length){
	selected = $($('#results').children(':not(.break)').get(0));
    }
    selected.addClass('selected');
    selectable($('#results').children(':not(.break)'));
}

function updatePlaylist(data){
    if ((data.current || $('#current').attr('pk')) &&
	parseInt($('#current').attr('pk')) != data.current){
	socket.emit('current_request');
    }
    
    function getLocalPlaylist(){
	selection = $('#playlist').children('.music-bar')
	pks = []
	selection.each(function(){
	    pks.push(parseInt($(this).attr('pk')))
	});
	return pks
    }

    //then with the playlist
    var remote = data.playlist
    var finalSort = []
    for (i=0; i<data.playlist.length; i++){
	finalSort[data.playlist[i]] = i
    }
    var local = getLocalPlaylist();
    var currentSort = [];
    for (i=0; i<local.length; i++){
	currentSort[data.playlist[i]] = i
    }
    var movements = [];
    var deletions = [];
    var additions = [];
    for (i in local){
	if (typeof finalSort[local[i]] == 'undefined')
	    deletions.push(local[i])
    }
    for (i in remote){
	if (typeof currentSort[remote[i]] == 'undefined')
	    additions[remote[i]] = parseInt(i)
    }
    //if local length < remote length, still valid
    //if remote length < local length, still valid
    for (i=0; i<remote.length; i++){
	if (local[i] != remote[i] && 
	    (typeof additions[remote[i]] == 'undefined')){
	    movements[remote[i]] = i;
	}
    }
    moveBars(movements, deletions, additions, finalSort);
}

function updateCurrent(html){
    $('#time').remove();
    $('#current').animate({opacity:0}, {
	duration: 250,
	complete: function(){
	    $(this).replaceWith(html)
	    $('#current').css({opacity:0})
		.animate({opacity:1},250);
	}
    });
}

function moveBars(movements, deletions, additions, finalSort){
    var time = 400;
    parent = $('#playlist');
    plist = $('#playlist').children('.music-bar');
    var donified = 0;
    var required = 0;
    for (i in movements){
	++required;
	bar = plist.filter('[pk="' + i + '"]');
	target = plist.filter('[pos="' + movements[i] + '"]')
	    .offset().top - bar.offset().top;
	if (movements[i]%2 == 0){
	    bar.animate({top: target, backgroundColor: '#F0F0F0'},
			{duration:time, complete: function(){
			    ++donified;
			}});
	} else {
	    bar.animate({top: target, backgroundColor: '#FFFFFF'},
			{duration:time, complete: function(){
			    ++donified;
			}});
	}
    }
    for (i in deletions){
	++required;
	bar = plist.filter('[pk="' + deletions[i] + '"]');
	bar.animate({opacity:0},{
	    duration: 500, complete: function(){
		++donified;
	    }});
    }
    for (i in additions){
	++required;
	socket.once('song_data', function(html){
	    bar = $(html).appendTo(parent);
	    if (additions[i]%2 == 0)
		bar.addClass('greyed');
	    bar.css({opacity:0}).animate(
		{opacity:1},
		{duration:500, complete: function(){
		    ++donified;
		}});
	});
	socket.emit('song_request', i);
    }
    
    function settle_once_done(){
	if (donified < required){
	    setTimeout(settle_once_done, 50);
	    return;
	}
	settle();
    }

    function settle(){
	for (i in deletions){
	    plist.filter('[pk="' + deletions[i] + '"]').remove()
	}
	//refresh selector
	plist = $('#playlist').children('.music-bar');
	plist.sortElements(function(a,b){
	    return finalSort[parseInt($(a).attr('pk'))] > 
		finalSort[parseInt($(b).attr('pk'))] ? 1 : -1
	});
	plist.css('top',0).attr('pos',function(){
	    return finalSort[parseInt($(this).attr('pk'))]
	});
	plist.each(function(){
	    if (parseInt($(this).attr('pos')%2) === 0){
		$(this).addClass('greyed');
	    }else{
		$(this).removeClass('greyed');
	    }
	    $(this).attr('style','');
	});
	sortable('.music-bar', '#playlist');
	deletable('.music-bar');
    }
    settle_once_done();
}


function fillScreen(){
    main = $('#main');
    main.height($(window).height() - main.offset().top - $('#uploadbox').height() - 32)
}
`