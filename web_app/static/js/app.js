/* Smooth scrolling para anclas */  
$(document).on('click','a.smooth', function(e){
    e.preventDefault();
    var $link = $(this);
    var anchor = $link.attr('href');
    $('html, body').stop().animate({
        scrollTop: $(anchor).offset().top
    }, 1000);
});

/* MixItUp */
$(function() {
    $('#Grid').mixitup();
});


/* Hover Touch */
$(document).ready(function() {
    $('.hover').bind('touchstart', function(e) {
        e.preventDefault();
        $(this).toggleClass('cs-hover');
    });
});