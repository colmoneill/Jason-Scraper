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


  var navigation = responsiveNav(".nav-collapse", {
    animate: true,                    // Boolean: Use CSS3 transitions, true or false
    transition: 284,                  // Integer: Speed of the transition, in milliseconds
    label: "",                        // String: Label for the navigation toggle
    insert: "after",                  // String: Insert the toggle before or after the navigation
    customToggle: "",       		  // Selector: Specify the ID of a custom toggle
    closeOnNavClick: false,           // Boolean: Close the navigation when one of the links are clicked
    openPos: "relative",              // String: Position of the opened nav, relative or static
    navClass: "nav-collapse",         // String: Default CSS class. If changed, you need to edit the CSS too!
    navActiveClass: "js-nav-active",  // String: Class that is added to <html> element when nav is active
    jsClass: "js",                    // String: 'JS enabled' class which is added to <html> element
    init: function(){},               // Function: Init callback
    open: function(){},               // Function: Open callback
    close: function(){}               // Function: Close callback
  });