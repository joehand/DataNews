/* ========================================================================
 * Models JS File for DataNews
 * Author: JoeHand
 * ========================================================================
 */
define(['backbone', 'underscore'], function(Backbone, _) {

    var API_VER = 'v0',
        API_ROOT = '/api/' + API_VER + '/'

    var Vote = Backbone.Model.extend({
        urlRoot :  API_ROOT + 'vote',

        defaults: function() {
            return {
                timestamp: new Date().toISOString()
            };
        },

        initialize: function() {
          if (!this.get("timestamp")) {
            this.set({"timestamp": this.defaults().timestamp});
          }

          if (!this.get('user_from_id') && currentUser) {
            this.set({'user_from_id': currentUser});
          }
        }
    });

    var Votes = Backbone.Collection.extend({
        model : Vote,
        url : API_ROOT + 'vote',
        parse: function(response) {
            return response.objects;
        }
    });

    return Vote;
});