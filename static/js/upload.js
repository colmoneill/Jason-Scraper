function uploadField (name, element, form) {
    var acceptedTypes = ['image/png', 'image/jpeg', 'image/gif'];
    
    var images = [];
    
    var $el         = $(element),
        $field      = $el.find('input.filepicker'),
        $aggregator = $el.find('input.aggregator'),
        $button     = $el.find('button'),
        $dropmask   = $el.find('.dropmask'),
        $thumbnails = $el.find('.thumbnail-container');

    var addThumbnail = function (file) {
        var reader = new FileReader(),
        $thumbnail = $('<img class="upload-thumbnail">');

        reader.onload = function (event) {
            $thumbnail.attr('src', event.target.result);
            $thumbnails.append($thumbnail);
        }

        reader.readAsDataURL(file);

        return $thumbnail;
    };

    var handleFiles = function (files) {
        for (var i=0; i < files.length; i++) {
            handleFile(files[i]);
        }
    }

    var handleFile = function (file) {
        if (acceptedTypes.indexOf(file.type) > -1) {
            addThumbnail(file);
            images.push(file);
        }
    };

    $el.on('dragenter', function (e) {
            e.preventDefault();
            $dropmask.show();
        });
    
    $dropmask.on('dragover', function (e) {
            e.preventDefault();
            e.originalEvent.dataTransfer.dropEffect = 'copy';
        })
        .on('dragleave', function () {
            $(this).hide();
        })
        .on('dragend', function () {
            $(this).hide();
        })
        .on('drop', function (e) {
            e.preventDefault();
            e.originalEvent.dataTransfer.dropEffect = 'copy';
            // hide dropmask
            $(this).hide();
            handleFiles(e.originalEvent.dataTransfer.files);
        });

    $field.change(function () {
        handleFiles(this.files);
        $(this).val('');
    });
    
    $button.click(function (e) {
        e.preventDefault();
        $field.click();
    });
    
    $(form).on('submit', function (e) {
        e.preventDefault();
        data = new FormData(this);
        
        for (var i=0;i<images.length;i++) {
            data.append('image', images[i]);
        }
        
        $.ajax({
            type: "POST",
            url: $(form).attr('action'),
            enctype: 'multipart/form-data',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            success: function (image) {
                callback.call(ctx, image);
            },
            dataType: 'json'
        });
    });
}