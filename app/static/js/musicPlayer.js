$.fn.swap = function(selection, attr){
    temp = selection.attr(attr);
    selection.attr(attr,$(this).attr(attr));
    return $(this).attr(attr,temp);
}

$.fn.toggleClass = function(cls){
    if ($(this).hasClass(cls)){
	return $(this).removeClass(cls);
    } else {
	return $(this).addClass(cls);
    }
}

$(document).ready(function(){
    sortify('.music-bar', '#playlist');
});

function sortify(sortableClass, sortBox){
    $(sortableClass).mousedown(function(e){
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
	});
    });
}
