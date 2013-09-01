//The build will inline common dependencies into this file.

//For any third party dependencies, like jQuery, place them in the libs folder.

//Configure loading modules from the lib directory,
//except for 'app' ones, which are in a sibling
//directory.
requirejs.config({
    paths: {
        'model'              : 'model', //shortcuts for model/view files
        'view'               : 'view',
        'jquery'             : 'lib/jquery-2.0.3',
        'underscore'         : 'lib/underscore',
        'backbone'           : 'lib/backbone',
        'bootstrap'          : 'lib/bootstrap',
        'pjax'               : 'lib/jquery.pjax'
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