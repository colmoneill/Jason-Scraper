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
	
	$('#collapse-bttn').click(function() {
		$('#exhib-list').toggleClass('list-open');
		$(this).toggleClass('list-open');
	});
	
 
	function onScroll(event){
		var scrollPosition = $(document).scrollTop();
		$('.subnav a.go-to-anchor').each(function () {
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
	
	//
	
	$( function()
	{
			// OVERLAY

			overlayOn = function()
			{
				$( '<div id="imagelightbox-overlay"></div>' ).appendTo( 'body' );
				$( '<div id="slider-text-box"></div>' ).appendTo( 'body' );

			},
			overlayOff = function()
			{
				$( '#imagelightbox-overlay' ).remove();
				$( '#slider-text-box' ).remove();
			},


			// CLOSE BUTTON

			closeButtonOn = function( instance )
			{
				$( '<div id="imagelightbox-close">close x</div>' ).appendTo( 'body' ).on( 'click touchend', function(){ $( this ).remove(); instance.quitImageLightbox(); return false; });
			},
			closeButtonOff = function()
			{
				$( '#imagelightbox-close' ).remove();
			},


			// CAPTION

			captionOn = function()
			{
				var source_image_location = 'a[href="' + $( '#imagelightbox' ).attr( 'src' ) + '"] div';
				var artwork_group_name = $( source_image_location ).attr( 'data-groupexhibitionname' ); 
				var artwork_gorup_artist= $( source_image_location ).attr( 'data-groupexhibtionartist' );
				var artwork_artist = $( source_image_location ).attr( 'data-exhibitionartistname' );
				var artwork_year = $( source_image_location ).attr( 'data-artworkyear' );
				var artwork_medium = $( source_image_location ).attr( 'data-artworkmedium' ); 
				var artwork_dimensions = $( source_image_location ).attr( 'data-artworkdimensions' ); 
				var installation_group = $( source_image_location ).attr( 'data-installation-group' ); 
				var installation_solo = $( source_image_location ).attr( 'data-installation-solo' ); 
				
				var artwork_data = [artwork_group_name, artwork_gorup_artist, artwork_artist, artwork_year, artwork_medium, artwork_dimensions, installation_group, installation_solo];
				 
				$( '<div id="imagelightbox-caption"></div>' ).appendTo( '#slider-text-box' );
				
				for (i = 0; i < artwork_data.length; i++) { 
					if(artwork_data[i] !='' && typeof artwork_data[i] != 'undefined'){
						$( '<p>'+ artwork_data[i] +'</p>').appendTo( '#imagelightbox-caption');
					}
				}
				
			},
			captionOff = function()
			{
				$( '#imagelightbox-caption' ).remove();
			},


			// NAVIGATION

			navigationOn = function( instance, selector )
			{
				var images = $( selector );
				if( images.length )
				{
					var nav = $( '<div id="imagelightbox-nav"></div>' );
					for( var i = 0; i < images.length; i++ )
						nav.append( '<button type="button"></button>' );

					nav.appendTo( 'body' );
					nav.on( 'click touchend', function(){ return false; });

					var navItems = nav.find( 'button' );
					navItems.on( 'click touchend', function()
					{
						var $this = $( this );
						if( images.eq( $this.index() ).attr( 'href' ) != $( '#imagelightbox' ).attr( 'src' ) )
							instance.switchImageLightbox( $this.index() );

						navItems.removeClass( 'active' );
						navItems.eq( $this.index() ).addClass( 'active' );

						return false;
					})
					.on( 'touchend', function(){ return false; });
				}
			},
			navigationUpdate = function( selector )
			{
				var items = $( '#imagelightbox-nav button' );
				items.removeClass( 'active' );
				items.eq( $( selector ).filter( '[href="' + $( '#imagelightbox' ).attr( 'src' ) + '"]' ).index( selector ) ).addClass( 'active' );
			},
			navigationOff = function()
			{
				$( '#imagelightbox-nav' ).remove();
			},


			// ARROWS

			arrowsOn = function( instance, selector )
			{
				var $arrows = $( '<div class="imagelightbox-arrow imagelightbox-arrow-left"><p>&#139; previous</p></div><div class="imagelightbox-arrow imagelightbox-arrow-right"><p>next &#155;</p></div>' );

				$arrows.appendTo( 'body' );
				
				getArrowsHeight = function() {
					$arrows.css({'height':($("#slider-text-box").height()+'px')});
				};
				
				$(window).resize(function() {
					getArrowsHeight();
				});

				$arrows.on( 'click touchend', function( e )
				{
					e.preventDefault();

					var $this	= $( this ),
						$target	= $( selector + '[href="' + $( '#imagelightbox' ).attr( 'src' ) + '"]' ),
						index	= $target.index( selector );

					if( $this.hasClass( 'imagelightbox-arrow-left' ) )
					{
						index = index - 1;
						if( !$( selector ).eq( index ).length )
							index = $( selector ).length;
					}
					else
					{
						index = index + 1;
						if( !$( selector ).eq( index ).length )
							index = 0;
					}

					instance.switchImageLightbox( index );
					return false;
				});
			},
			arrowsOff = function()
			{
				$( '.imagelightbox-arrow' ).remove();
			};
});
	
	$( function()
    	{
    	
    	var selectorF = '.image-block a';
		var instanceF = $( selectorF ).imageLightbox({
	        	selector:       'id="imagelightbox"',   // string;
				allowedTypes:   'png|jpg|jpeg|gif',     // string;
			    animationSpeed: 250,                    // integer;
			    preloadNext:    true,                   // bool;            silently preload the next image
			    enableKeyboard: true,                   // bool;            enable keyboard shortcuts (arrows Left/Right and Esc)
			    quitOnEnd:      false,                  // bool;            quit after viewing the last image
			    quitOnImgClick: false,                  // bool;            quit when the viewed image is clicked
			    quitOnDocClick: true,                   // bool;            quit when anything but the viewed image is clicked
			    onStart:		function() { overlayOn(); closeButtonOn( instanceF ); arrowsOn( instanceF, selectorF ); },
				onEnd:			function() { overlayOff(); captionOff(); closeButtonOff(); arrowsOff(); },
				onLoadStart: 	function() { captionOff(); },
				onLoadEnd:	 	function() { captionOn(); $( '.imagelightbox-arrow' ).css( 'display', 'block' ); getArrowsHeight() }

        	});
		});


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