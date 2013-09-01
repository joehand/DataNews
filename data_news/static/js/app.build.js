({
    out: "../js/app.min.js",
    name: 'app',
    optimize: "uglify",
    paths: {
        'model'              : 'model', //shortcuts for model/view files
        'view'               : 'view',
        'jquery'             : 'lib/jquery-2.0.3',
        'underscore'         : 'lib/underscore',
        'backbone'           : 'lib/backbone',
        'bootstrap'          : 'lib/bootstrap',
        'pjax'               : 'lib/jquery.pjax',
    },
    shim: {
        backbone: {
            deps: ['jquery', 'underscore'],
            exports: 'Backbone'
        },
        underscore: {
            exports: '_'
        },
        bootstrap: {
            deps: ['jquery']
        },
        pjax: {
            deps: ['jquery']
        }
    }
})