var draggedThumbnail;

function extend (obj, dict) { 
    for (var i=1;i<arguments.length;i++) {
        for (key in arguments[i]) {
            obj[key] = arguments[i][key]; 
        }
    }
}

var Thumbnail = function (input, fieldname) {
    this.fieldname = fieldname;
    
    if (input instanceof File) {
        this.$el = $(this.template());
        this.file = input;
        this.loadFromFile(input);
    } else if (typeof input == 'string') {
        this.$el = $(this.template());
        this.loadFromPath(input);
    } else {
        this.$el = input;
    }
    
    
    var self = this;
    this.$('.action.delete').click(function () { self.delete(); });
    this.$('.action.restore').click(function () { self.restore(); });
    
    this.$el.on('dragstart', function startdrag (e) {
            // register
            self.startdrag(e);
        }).on('drop', function (e) {
            self.ondrop(e);
        }).on('dragover', function (e) {
            self.dragover(e);
        }).on('dragleave', function (e) {
            self.dragleave(e);
        });
}

extend(Thumbnail.prototype, {
    $: function (selector) { return this.$el.find(selector); },
    
    template: function () {
        html = '<div class="upload-thumbnail selectable" draggable="true">'
        + '<span class="glyphicon glyphicon-remove action delete"></span>'
        + '<span class="glyphicon glyphicon-restore action restore"></span>'
        + '<input type="hidden" name="' + this.fieldname + '" value="" />'
        + '<img src="">'
        + '</div>';
        return html;
    },
       
    loadFromFile: function (file) {
        var reader = new FileReader(),
            self = this;
        reader.onload = function (event) {
            self.$('img').attr('src', event.target.result);
        }
        reader.readAsDataURL(file);
    },
    
    loadFromPath: function (path) {
        this.$('img').attr('src', path);
    },
    
    'delete': function () {
        this.$el.addClass('disabled');
        this.$('input').prop('disabled', 'disabled');
        
        if (this.onDelete) this.onDelete();
    },
    
    restore: function () {
        this.$el.removeClass('disabled');
        this.$('input').removeProp('disabled');
        if (this.onRestore) this.onRestore();
    },
    
    ondrop: function (e) {
        e.preventDefault();
        if (this.$el != draggedThumbnail) {
            this.$el.removeClass('drop-suggestion-before drop-suggestion-after');
            var offset = e.originalEvent.clientX - this.$el.offset().left;
            
            if ((offset) > (this.$el.width() / 2)) {
                this.$el.after($(draggedThumbnail).detach());
            } else {
                this.$el.before($(draggedThumbnail).detach());
            }
        }
        draggedThumbnail = null;
    },
    
    startdrag: function (e) {
        e.originalEvent.dataTransfer.setData('text/drag-type', 'thumbnail');
        draggedThumbnail = this.$el;
    },
    
    dragover: function (e) {
        e.preventDefault();
        if (this.$el != draggedThumbnail) {
            var offset = e.originalEvent.clientX - this.$el.offset().left;
            this.$el.removeClass('drop-suggestion-before drop-suggestion-after');
            if ((offset) > (this.$el.width() / 2)) {
                this.$el.addClass('drop-suggestion-after');
            } else {
                this.$el.addClass('drop-suggestion-before');
            }
        }
    },
    
    dragleave: function (e) {
        this.$el.removeClass('drop-suggestion-before drop-suggestion-after');
    },
    
    setUploadIndex: function (i) {
        this.$el.find('input[type=hidden]').val('uploaded:' + i.toString());
    }
});

var SelectableThumbnail = function (input, fieldname) {
    Thumbnail.call(this, input, fieldname);
    
    var self = this;
};

extend(SelectableThumbnail.prototype, Thumbnail.prototype, {
    template: function () {
        html = '<div class="upload-thumbnail selectable">'
        + '<span class="glyphicon glyphicon-remove action delete"></span>'
        + '<span class="glyphicon glyphicon-ok action restore"></span>'
        + '<input type="hidden" name="' + this.fieldname + '" value="" />'
        + '<img src="">'
        + '</div>';
        return html;
    }
});

var UploadField = function (name, $el) {
    this.name            = name;
    this.$el             = $el;
    this.acceptedTypes   = ['image/png', 'image/jpeg', 'image/gif'];
    this.files           = [];
    this.thumbnails      = [];
    
    this.attachElements();
    this.setListeners();
}

extend(UploadField.prototype, {
    $: function (selector) { return this.$el.find(selector); },
    
    thumbnailPrototype: Thumbnail,
       
    attachElements: function () {
        this.$field          = this.$('input.filepicker');
        this.$button         = this.$('button');
        this.$dropmask       = this.$('.dropmask');
        this.$thumbnails     = this.$('.thumbnail-container');
        this.$deleteThumb    = this.$('.action.delete');
        this.$restoreThumb   = this.$('.action.restore');
    },
       
    setListeners: function () {
        var self = this;
        
        this.$el.on('dragenter', function (e) {
            if (!self.isInternalDrag(e)) {
                e.preventDefault();
                self.$dropmask.show();
            }
        });
        
        this.$dropmask.on('dragover', function (e) {
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
            self.handleFiles(e.originalEvent.dataTransfer.files);
        });
        
        this.$field.change(function () {
            self.handleFiles(this.files);
            $(this).val('');
        });
        
        this.$button.click(function (e) {
            e.preventDefault();
            self.$field.click();
        });
        
        this.$('.upload-thumbnail').each(function () {
            new Thumbnail($(this));
        });
    },
       
    handleFiles: function (files) {
        for (var i=0; i < files.length; i++) {
            this.handleFile(files[i]);
        }
    },
    
    handleFile: function (file) {
        if (this.acceptedTypes.indexOf(file.type) > -1) {
            var thumbnail = this.addThumbnail(file);
            this.files.push(file);
            this.thumbnails.push(thumbnail);
        }
    },
    
    addThumbnail: function (data) {
        var thumbnail = new this.thumbnailPrototype(data, this.name),
            self = this;
       
        thumbnail.onDelete = function() { self.deleteUploadThumbnail(thumbnail); };
        thumbnail.onRestore = function() { self.restoreUploadThumbnail(thumbnail); };

        this.$thumbnails.append(thumbnail.$el);
        
        return thumbnail;
    },
    
    deleteUploadThumbnail: function (thumbnail) {
        if (thumbnail.file && this.files.indexOf(thumbnail.file) > -1) {
            delete this.thumbnails[this.thumbnails.indexOf(thumbnail)];
            delete this.files[this.files.indexOf(thumbnail.file)];
        }
    },
    
    restoreUploadThumbnail: function (thumbnail) {
        if (thumbnail.file && this.files.indexOf(thumbnail.file) < 0) {
            this.thumbnails.push(thumbnail);
            this.files.push(thumbnail.file);
        }
    },
    
    isInternalDrag: function (e) {
        var types = e.originalEvent.dataTransfer.types;
        for (var i=0; i<types.length;i++) {
            if (types[i] == 'text/drag-type') {
                return true;
            }
        }
        return false;
    },
    
    setUploadIndexes: function () {
        for (var i=0;i<this.thumbnails.length;i++) {
            this.thumbnails[i].setUploadIndex(i);
        }
    }
});

var BoundUploadField = function (name, $el) {
    UploadField.call(this, name, $el);
};

extend(BoundUploadField.prototype, UploadField.prototype, {
    thumbnailPrototype: SelectableThumbnail
});

var Form = function ($el) {
    this.$el = $el;
    this.uploadFields = [];
    
    var self = this;
    this.$el.on('submit', function (e) { self.onSubmit(e); });
}

extend(Form.prototype, {
    $: function (selector) {
        return this.$el.find(selector);
    },
    
    addUploadField: function (name) {
        var field = new UploadField(name, this.$('#' + name + '-upload-field'));
        this.uploadFields.push(field);
        return field;
    },
    
    addBoundUploadField: function (name) {
        var field = new BoundUploadField(name, this.$('#' + name + '-upload-field'));
        this.uploadFields.push(field);
        return field;
    },

    markProcessing: function () {
        this.$('#submit-button').addClass('hide');
        this.$('#processing-button').removeClass('hide');
    },

    markDone: function () {
        this.$('#submit-button').removeClass('hide');
        this.$('#processing-button').addClass('hide');
    },
    
    clearErrors: function () {
        this.$('p.text-danger').detach();
        this.$('.has-error').removeClass('has-error');
    },

    showValueErrors: function (errors) {
        var fieldName,
            fieldNames = Object.getOwnPropertyNames(errors);
        
        if (fieldNames.length > 0) {
            for (fieldName in errors) {
                this.showErrorsOnField(fieldName, errors[fieldName]);
            }
            
            this.focusOnField(fieldNames[0]);
        }
    },
    
    showErrorsOnField: function (fieldName, errors) {
        var $field = this.getFieldWrapper(fieldName);
        
        $field.addClass('has-error');
        
        for (var i=0;i<errors.length;i++) {
            var $error = $('<p>')
            .addClass('text-danger')
            .text(errors[i]);
            $field.prepend($error);
        }
        
    },
    
    focusOnField: function (fieldName) {
        this.getFieldWrapper(fieldName).get(0).scrollIntoView(false);
        this.getField(fieldName).focus();
    },
    
    getField: function (fieldName) {
        return this.$('[name="' + fieldName + '"]');
    },
    
    getFieldWrapper: function(fieldName) {
        return this.getField(fieldName).parents('.form-group');
    },    
    
    onSubmit: function (e) {
        e.preventDefault();
        this.clearErrors();        
        this.markProcessing();
        
        for (var i=0;i<this.uploadFields.length;i++){
            this.uploadFields[i].setUploadIndexes();
        }
        
        var formData = new FormData(this.$el.get(0));
        
        for (var i=0;i<this.uploadFields.length;i++) {
            var field = this.uploadFields[i];
            
            for (var f=0;f<field.files.length;f++) {
                formData.append(field.name, field.files[f]);
            }
        }
        
        var self = this;
        
        $.ajax({
            type: "POST",
            url: this.$el.attr('action'),
            enctype: 'multipart/form-data',
            data: formData,
            cache: false,
            contentType: false,
            processData: false,
            success: function (response) { self.onSuccess(); },
            error: function (response) { self.onError(response); },
            dataType: 'json'
        });
    },
    
    onSuccess: function (data) {
        this.markDone();
        
        var redirectExp = /(\/[a-z\-]+\/[a-z\-]+\/)/i,
            newPathMatch = redirectExp.exec(window.location.pathname);

        if (newPathMatch != null) {
            window.location.assign(newPathMatch[0]);
        } else {
            console.warn('Could not find redirect on location', window.location.pathname);
        }
    },
       
    onError: function (response) {
        this.markDone();
        
        if (response.status == 400) {
            this.onValueError(response);
        } else {
            this.showError();
        }
    },
    
    onValueError: function (response) {
        var errors = response.responseJSON || [];
        this.showValueErrors(errors);
    },
    
    showError: function () {
        alert('Unknown error while saving. Try again');
    }
});