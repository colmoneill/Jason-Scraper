/*
jQuery("document").ready(function($){
	var pos = $('.nav-container').offset().top;
	var nav = $('.nav-container');
	
	$(window).scroll(function () {
	if ($(this).scrollTop() > pos) {
	nav.addClass("f-nav");
	} else {
	nav.removeClass("f-nav");
	}
	});
});
*/

jQuery("document").ready(function($){
$("#sidebar").stick_in_parent();
});

	$(document).ready(function () {
		$(document).on("scroll", onScroll);
 
		$('a[href^="#"]').on('click', function (e) {
			e.preventDefault();
			$(document).off("scroll");
 
			$('a').each(function () {
				$(this).removeClass('active');
			})
			$(this).addClass('active');
 
			var target = this.hash;
			$target = $(target);
			$('html, body').stop().animate({
				'scrollTop': $target.offset().top
			}, 500, 'swing', function () {
				window.location.hash = target;
				$(document).on("scroll", onScroll);
			});
		});
	});
 
	function onScroll(event){
		var scrollPosition = $(document).scrollTop();
		$('.nav-container a').each(function () {
			var currentLink = $(this);
			var refElement = $(currentLink.attr("href"));
			if (refElement.position().top <= scrollPosition && refElement.position().top + refElement.height()  > scrollPosition) {
				$('.nav-container ul li a').removeClass("active");
				currentLink.addClass("active");
			}
			else{
				currentLink.removeClass("active");
			}
		});
	}