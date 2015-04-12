/*
 * Lazy Res - jQuery plugin for lazy loading responsive images
 *
 * Copyright (c) 2014 Tentwelve
 *
 * Licensed under the MIT license:
 *   http://www.opensource.org/licenses/mit-license.php
 *
 * Version:  0.3.0
 *
 * BASED ON THE LAZYLOAD PLUGIN
 * Lazy Load - jQuery plugin for lazy loading images
 *
 * Copyright (c) 2007-2013 Mika Tuupola
 *
 * Licensed under the MIT license:
 *   http://www.opensource.org/licenses/mit-license.php
 *
 * Project home:
 *   http://www.appelsiini.net/projects/lazyload
 *
 * Version:  1.9.3
 *
 */

(function($, window, document, undefined) {
    var $window = $(window);

    $.fn.lazyres = function(options) {

        var elements = this, $container,
        dpr = (typeof window.devicePixelRatio !== 'undefined')?window.devicePixelRatio:1,
        settings = {
            threshold       : 0,
            failure_limit   : 0,
            event           : 'scroll',
            effect          : 'show',
            container       : window,
            data_attribute  : 'lazy-url',
            step            : 64,
            skip_invisible  : true,
            refresh          : null,
            load            : null,
            placeholder     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC'
        };

        function update() {
            var counter = 0;
            elements.each(function() {
                var $this = $(this);
                if (settings.skip_invisible && !$this.is(':visible')) {
                    return;
                }
                if ($.abovethetop(this, settings) ||
                    $.leftofbegin(this, settings)) {
                        /* Nothing. */
                } else if (!$.belowthefold(this, settings) &&
                    !$.rightoffold(this, settings)) {
                        $this.trigger('refresh');
                        /* if we found an image we’ll load, reset the counter */
                        counter = 0;
                } else {
                    if (++counter > settings.failure_limit) {
                        return false;
                    }
                }
            });
        }

        if(options) {
            $.extend(settings, options);
        }

        /* Cache container as jQuery as object. */
        $container = (settings.container === undefined ||
                      settings.container === window) ? $window : $(settings.container);

        /* Fire one scroll event per scroll. Not one scroll event per image. */
        if (0 === settings.event.indexOf('scroll')) {
            $container.on(settings.event, $.debounce(150, function() {
                return update();
            }));
        }

        this.each(function() {
            var self = this,
            $self = $(self),
            original = $self.data(settings.data_attribute),
            step = $self.data('lazy-step')||settings.step,
            wi,
            he;

            self.loaded = false;
            self.dataW = $self.data('lazy-default_width')/dpr || false;
            self.dataH = $self.data('lazy-default_height')/dpr || false;

            /* When refresh is triggered load original image. */
            $self.on('refresh', function() {

                    var elements_left;

                    if (settings.refresh) {
                        elements_left = elements.length;
                        settings.refresh.call(self, elements_left, settings);
                    }

                    wi = $self.innerWidth();
                    he = $self.innerHeight();

                    var mod = false;

                    if (self.dataW && (wi > self.dataW)) {
                        mod = Math.ceil(wi / step);
                        self.dataW = mod*step;
                        he = Math.round(he * ( self.dataW / wi ));
                        wi = self.dataW;
                    } else if (self.dataH && (he > self.dataH)) {
                        mod = Math.ceil(he / step);
                        self.dataH = mod*step;
                        wi = Math.round(wi * ( self.dataH / he ));
                        he = self.dataH;
                    }

                    if(mod) {

                        var treated = original+'?lazy=1';
                        if(self.dataW) { treated += '&w='+(self.dataW*dpr); }
                        if(self.dataH) { treated += '&h='+(self.dataH*dpr); }

                    $('<img />').on('load', function() {
                        if ($self.is('img')) {
                            //$self.hide();
                            $self.attr('src', treated);
                            //$self[settings.effect](settings.effect_speed);
                        } else {
                            $self.css('background-image', 'url("' + treated + '")');
                        }

                    }).attr('src', treated);

                    self.loaded = true;

                    if (settings.load) {
                        elements_left = elements.length;
                        settings.load.call(self, elements_left, settings);
                    }
                    }
            });

            /* When wanted event is triggered load original image */
            /* by triggering refresh.                              */
            if (0 !== settings.event.indexOf('scroll')) {
                $self.on(settings.event, $.debounce(150, function() {
                    if (!self.loaded) {
                        $self.trigger('refresh');
                    }
                }));
            }
        });

        /* Check if something refreshes when window is resized. */
        $window.on('resize', $.debounce(150, function() {
            update();
        }));

        /* With IOS5 force loading images when navigating with back button. */
        /* Non optimal workaround. */
        if ((/(?:iphone|ipod|ipad).*os 5/gi).test(navigator.appVersion)) {
            $window.on('pageshow', function(event) {
                if (event.originalEvent && event.originalEvent.persisted) {
                    elements.each(function() {
                        $(this).trigger('refresh');
                    });
                }
            });
        }

        /* Force initial check if images should refresh. */
            update();

        return this;
    };

    /* Convenience methods in jQuery namespace.           */
    /* Use as  $.belowthefold(element, {threshold : 100, container : window}) */

    $.belowthefold = function(element, settings) {
        var fold;

        if (settings.container === undefined || settings.container === window) {
            fold = (window.innerHeight ? window.innerHeight : $window.height()) + $window.scrollTop();
        } else {
            fold = $(settings.container).offset().top + $(settings.container).height();
        }

        return fold <= $(element).offset().top - settings.threshold;
    };

    $.rightoffold = function(element, settings) {
        var fold;

        if (settings.container === undefined || settings.container === window) {
            fold = $window.width() + $window.scrollLeft();
        } else {
            fold = $(settings.container).offset().left + $(settings.container).width();
        }

        return fold <= $(element).offset().left - settings.threshold;
    };

    $.abovethetop = function(element, settings) {
        var fold;

        if (settings.container === undefined || settings.container === window) {
            fold = $window.scrollTop();
        } else {
            fold = $(settings.container).offset().top;
        }

        return fold >= $(element).offset().top + settings.threshold  + $(element).height();
    };

    $.leftofbegin = function(element, settings) {
        var fold;

        if (settings.container === undefined || settings.container === window) {
            fold = $window.scrollLeft();
        } else {
            fold = $(settings.container).offset().left;
        }

        return fold >= $(element).offset().left + settings.threshold + $(element).width();
    };

    $.inviewport = function(element, settings) {
         return !$.rightoffold(element, settings) && !$.leftofbegin(element, settings) &&
                !$.belowthefold(element, settings) && !$.abovethetop(element, settings);
     };

    /* Custom selectors for your convenience.   */
    /* Use as $('img:below-the-fold').something() or */
    /* $('img').filter(':below-the-fold').something() which is faster */

    $.extend($.expr[':'], {
        'below-the-fold' : function(a) { return $.belowthefold(a, {threshold : 0}); },
        'above-the-top'  : function(a) { return !$.belowthefold(a, {threshold : 0}); },
        'right-of-screen': function(a) { return $.rightoffold(a, {threshold : 0}); },
        'left-of-screen' : function(a) { return !$.rightoffold(a, {threshold : 0}); },
        'in-viewport'    : function(a) { return $.inviewport(a, {threshold : 0}); },
        /* Maintain BC for couple of versions. */
        'above-the-fold' : function(a) { return !$.belowthefold(a, {threshold : 0}); },
        'right-of-fold'  : function(a) { return $.rightoffold(a, {threshold : 0}); },
        'left-of-fold'   : function(a) { return !$.rightoffold(a, {threshold : 0}); }
    });

})(jQuery, window, document);
