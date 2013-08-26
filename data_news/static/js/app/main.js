define([
    'backbone',
    'underscore',
    'jquery',
    'model/model',
    'view/view',
    'bootstrap',
    'pjax'
], function(Backbone, _, $, AppModel, AppView) {
    
    var appView = new AppView();
    var appModel = new AppModel();

    console.log(appView);

});