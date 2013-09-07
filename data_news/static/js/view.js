/* ========================================================================
 * View JS File for DataNews
 * Author: JoeHand
 * ========================================================================
 */
define(['backbone', 'jquery', 'model'], function(Backbone, $, VoteModel) {

    var ItemView = Backbone.View.extend({
        events: {
            "click .up-vote" : "createVote",
            "click .reply"   : "toggleCommentForm"
        },

        createVote: function(e) {
            // Create a vote!
            
            var $targ = $(e.currentTarget);

            if (!currentUser) {
               document.location.href = '/login';
            } else {
                if (!$targ.hasClass('invisible')) {
                    $targ.addClass('invisible')

                    //Create a vote. Some stuff set via model defaults (time, user)
                    var vote = new VoteModel({
                            item_id: this.item_id,
                            user_to_id: this.user_id
                        });
                    vote.save()

                    var $countEl = this.$el.find('.vote-count'),
                        count = $countEl.text();

                    $countEl.text(parseInt(count) + 1)
                }
            }
        },

        toggleCommentForm: function(e) {
            // Fetch the comment form via ajax and show
            // Otherwise shows/hides the form if we have it already

            e.preventDefault()
            var $targ = $(e.currentTarget);

            if ($targ.hasClass('clicked')) {
                $targ.parent().find('form').fadeOut('fast');
                $targ.find('a').text('reply');
            } else if ($targ.hasClass('form-active')) {
                $targ.parent().find('form').fadeIn('fast');
                $targ.find('a').text('hide');
            } else {  
                var form_url = $targ.find('a').attr("href");
                this.getCommentForm(form_url);
            }
            
            $targ.toggleClass('clicked');
        },

        appendCommentForm: function(data) {
            // Add the comment form and change classes/text on link
            var $form = $(data.html).fadeOut();
            this.$el.find('.comment-text').append($form);
            $form.fadeIn('fast');
            this.$el.find('.reply').addClass('form-active');
            this.$el.find('.reply a').text('hide');
        },

        getCommentForm: function(url) {
            //TODO write a real error function, even though errors shouldn't happen - they do
            $.ajax({
                context:this,
                url: url,
                type: 'GET',
                dataType: 'json',
                success: this.appendCommentForm,
                error: function() { console.error('uh oh did not work!'); },
                beforeSend: setHeader
            }, this);

            function setHeader(xhr) {
                // We set this header so Flask knows we aren't human =)
                xhr.setRequestHeader('formJSON', 'True');
            }
        },

        initialize: function() {
            this.item_id = this.options.item_id;
            this.user_id = this.options.user_id;
            this.$el = $(this.el);
            this.render();
        },

        render: function() {
            return this;
        },



    });

    // Our overall **AppView** is the top-level piece of UI.
    var AppView = Backbone.View.extend({

        id: '#main',
        el: $("#main"),

        // Add events for focusing in/out of comment form
        events: {
          "focusin .comment-input":  "toggleInputFocus",
          "focusout .comment-input": "toggleInputFocus"
        },

        toggleInputFocus: function(e) {
            // Add class to show/hide submit button and keep height
            // can't do with pure CSS =(

            var $targ = $(e.currentTarget);
            var $form = $targ.parentsUntil('.comment-form').parent();

            if ($form.hasClass('focus') && $targ.val() == '') {
                $form.removeClass('focus');
            } else {
                $form.addClass('focus');
            }
        },

        initialize: function() {
            console.log('AppView init')

            // Start up child views and some ajax magic
            this.initPjax();
            this.initAllItems();

            // render, i guess?
            this.render();
        },

        render: function() {
            // I am lazy and don't do much...
            return this;
        },

        initPjax: function() {
            // Pjax loads portions of pages via ajax rather than reloading the whole thing
            // So basically we reload anything in the "#main" container and keep the rest
            // Need to update a few things manually like active states.
            // Also need to re-init any child views.

            var self = this;

            //Init the pjax for links
            $(document).pjax('a[data-pjax]', self.id);

            $(document).on('pjax:timeout', function(event) {
                // Prevent default timeout redirection behavior
                console.log('timeout');
                event.preventDefault();
            });

            //Init the pjax for forms
            $(document).on('submit', 'form[data-pjax]', function(event) {
                $.pjax.submit(event, '#main', {'scrollTo':false});
            });

            $(document).on('pjax:beforeSend', function(e, xhr, pj) {
                xhr.setRequestHeader('source_url', document.URL);
            });


            $(document).on('pjax:complete', function(e, xhr, pj) {
                console.log('complete');
                console.log(e, xhr, pj);
            });


            $(document).on('pjax:success', function(e, xhr, pj) {
                console.log('success');
                console.log(e, xhr, pj);
            });


            self.$el.on('pjax:start', function(e, xhr, pj) {
                console.log('pjax start')
                self.toggleLoading();
            });

            self.$el.on('pjax:end', function(e, xhr, pj) {
                console.log('pjax end')
                self.itemViews = []; // Clear old Item views
                self.initAllItems(); // Make new ones!
                self.toggleLoading();

                var $link_parent = $(e.relatedTarget).parent()
                if ($link_parent.hasClass('pjax-active')) {
                    $('.pjax-active.active').removeClass('active');
                    $link_parent.addClass('active');
                } else {
                    $('.pjax-active.active').removeClass('active');
                }

                if (pj.type == 'POST') {
                    self.highlightComment()
                }
            });

            //Send google our new page info
            $(document).on('pjax:complete', function() {
                if (typeof ga != "undefined") {
                    ga('set', 'location', window.location.href);
                    ga('send', 'pageview');
                }
            });
        },

        toggleLoading: function() {
            var $el = $('#main-container');

            if ($el.hasClass('loading')) {
                $el.animate({'opacity': '1'}, 200);
            } else {
                $el.animate({'opacity': '0'}, 200);
            }

            $el.toggleClass('loading');

        },

        initItem: function(el) {
            var data = $(el).data(),
                    item_id = data['id'],
                    user_id = data['user'];

            return itemView = new ItemView({
                                         el : el,
                                         id : $(el).attr('id'),
                                         item_id : item_id,
                                         user_id : user_id
                                        })
        },

        initAllItems: function() {
            // Item view is for a single item on either homepage (post)
            // or comments on a post page
            // Used to attach events to vote, reply, etc.

            var itemViews = [],
                initItem = this.initItem;
            $('.item').each(function(i, el) {
                var itemView = initItem(el);
                itemViews.push(itemView)
            });

            this.itemViews = itemViews;
        }, 

        highlightComment: function() {
            var itemId = window.location.hash;
            //scroll to our item
            if (itemId != ''){
                $("html, body").animate({ scrollTop: $(itemId).offset().top }, 1000);
                //add class to highlight
                $(itemId).addClass('highlight');
                setTimeout(function() {
                    $(itemId).removeClass('highlight');
                }, 4000);
            }
        }
    });

    return AppView;
});