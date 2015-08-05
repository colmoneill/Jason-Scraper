module.exports = function(grunt) {
  'use strict';

  grunt.initConfig({

    pkg: grunt.file.readJSON('package.json'),

    concat: {
      options: {
        separator: ';\n'
      },
      plugins: {
        src: ['scripts/plugins/**/*.js'],
        dest: '.tmp/plugins.js'
      }
    },

    uglify : {
      main: {
        options: {
          banner: '/*\n' +
          ' * <%= pkg.name %>\n' +
          ' *\n' +
          ' * <%= pkg.version %> <%= grunt.template.today("dd-mm-yyyy") %>\n' +
          ' *\n '+
          ' */\n'
        },
        files: {
          '../js/scripts.min.js' : 'scripts/scripts.js'
        }
      },
      plugins: {
        files: {
          '../js/plugins.min.js' : '.tmp/plugins.js'
        }
      }
    },

    compass: {
      css: {
       options: {
        config: 'config.rb'
      }
    }
  },

  jshint: {
    files: ['scripts/scripts.js'],
    options: {
      jshintrc: '.jshintrc'
    }
  },

  watch: {
    css: {
      files: ['sass/**/*.sass', 'sass/**/*.scss'],
      tasks: ['compass']
    },
    js: {
      files: ['scripts/scripts.js'],
      tasks: ['jshint', 'uglify:main']
    },
    scripts: {
      files: ['scripts/plugins/**/*.js'],
      tasks: ['jshint', 'concat', 'uglify:plugins']
    }
  },

  browserSync: {
    dev: {
      bsFiles: {
        src : [
        '../css/**/*.css',
        '../js/*.js',
        'templates/*.php',
        '../../*.php',
        ],
      },
      options: {
        watchTask: true,
        ghostMode: {
          clicks: false,
          location: false,
          forms: false,
          scroll: false
        },
        logLevel: 'debug',
        online: false,
        proxy: 'localhost',
        open: 'local',
        host: "localhost",
        port: 5000
      },
    },
  },

});

grunt.loadNpmTasks('grunt-contrib-jshint');
grunt.loadNpmTasks('grunt-contrib-concat');
grunt.loadNpmTasks('grunt-contrib-uglify');
grunt.loadNpmTasks('grunt-contrib-watch');
grunt.loadNpmTasks('grunt-contrib-compass');
grunt.loadNpmTasks('grunt-browser-sync');
grunt.loadNpmTasks('grunt-notify');

grunt.registerTask('test', 'jshint');
grunt.registerTask('dev', ['browserSync', 'watch']);
grunt.registerTask('default', ['compass', 'jshint', 'concat', 'uglify']);
grunt.registerTask('grj', ['watch']);

};
