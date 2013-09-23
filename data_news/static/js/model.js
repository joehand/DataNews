/* ========================================================================
 * Models JS File for DataNews
 * Author: JoeHand
 * ========================================================================
 */
define(['backbone', 'underscore'], function(Backbone, _) {

    /* Just used to submit votes right now */
    var Vote = Backbone.Model.extend({
        initialize: function(options) {
          this.url = this.collection.url + options.item_id
        }
    });

    var Votes = Backbone.Collection.extend({
        model : Vote,
        url : '/vote/',
        parse: function(response) {
            return response.objects;
        }
    });

    return new Votes;
});