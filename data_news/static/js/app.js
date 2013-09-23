requirejs.config({
    paths: {
        'model'              : 'model', //shortcuts for model/view files
        'view'               : 'view',
        'jquery'             : 'libs/jquery-2.0.3',
        'underscore'         : 'libs/underscore',
        'backbone'           : 'libs/backbone',
        'bootstrap'          : 'libs/bootstrap',
        'pjax'               : 'libs/jquery.pjax',
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
});

// Load the main app module to start the app
requirejs(["main"]);