function sendAndReplace(where){
    var data = new FormData($('.post-song')[0]);
    $.ajax({
	type: 'POST',
	url: where,
	data: data,
	complete: function(){},
	success: function(data){
	    console.log(data);
	    $('#uploadbox').html(data);
	},
	cache: false,
	contentType: false,
	processData: false
    });
}
