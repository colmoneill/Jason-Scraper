(function (window, document, $, jQuery) {
    'use strict';
    
    var getTemplate = function (name) {
        return $('#template-' + name)
                    .children()
                    .first()
                    .clone();
    }

    var addImage = function (image) {
        var el = getTemplate('artist-artwork');
        el.find('img').attr('src', image['path']);
        $('#artistImages').append(el);
    }
    
    var getImages = function (artist){
        $('#artistImages').empty();
        jQuery.get(
            '/admin/api/artist/' + artist + '/image,
            {
            dataType: 'json',
            success: function (images) {
                for (var i=0; i<images.length;i++) {
                    addImage(images[i]);
                }
            }
        });
    }
    
    $(window).ready(function () {
        $('select#artist').change(function () {
            getImages($(this).val());
        });
        
        getImages($('select#artist').val());
    });

})(window, document, $, jQuery);