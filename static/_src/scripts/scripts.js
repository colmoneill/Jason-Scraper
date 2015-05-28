$(document).ready(function() {

	/* FastClick.attach(document.body); */
	$("#sidebar").stick_in_parent(); // Allows the SideBar (Subnav) to keep percentage value and position relative to parent when fixed (Sticky-Kit)
		

	$(document).ready(function () {
		$(document).on("scroll", onScroll);
		$('a[href^="#"]').on('click', function (e) {
			e.preventDefault();
			$(document).off("scroll");
	 
			$('a').each(function () {
				$(this).removeClass('points-to');
			})
			$(this).addClass('points-to');
	 
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
		$('.subnav a').each(function () {
			var currentLink = $(this);
			var refElement = $(currentLink.attr("href"));
			if (refElement.position().top <= scrollPosition && refElement.position().top + refElement.height()  > scrollPosition) {
				$('.subnav ul li a').removeClass("points-to");
				currentLink.addClass("points-to");
			}
			else{
				currentLink.removeClass("points-to");
			}
		});
	}


});
