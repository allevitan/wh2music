function sendAndConfirm(where){
    var data = new FormData($('.post-song')[0]);
    $.ajax({
	type: 'POST',
	url: where,
	data: data,
	complete: function(){},
	success: function(data){
	    $('#playlist').addClass('hide');
	    $('.well').append(data);
	},
	cache: false,
	contentType: false,
	processData: false
    });
}

function sendConfirmData(where){
    var data = new FormData($('.post-song')[0]);
    $.ajax({
	type: 'POST',
	url: where,
	data: data,
	complete: function(){},
	success: function(data){
	    $('#playlist').removeClass('hide');
	    $('#uploadbox').remove();
	},
	cache: false,
	contentType: false,
	processData: false
    });
}    
