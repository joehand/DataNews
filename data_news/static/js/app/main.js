define([
    'backbone',
    'underscore',
    'jquery',
    'bootstrap',
    'pjax'
], function(Backbone, _, $) {
    $(document).pjax('a[data-pjax]', '#main');

    $('#main')
        .on('pjax:start', function() { 
        })
        .on('pjax:end',   function(e) {
            var $link = $(e.relatedTarget);
            if ($link.parent().hasClass('pjax-active')) {
                var $targ = $link.parent();
                $('.pjax-active.active').removeClass('active');
                $targ.addClass('active');
            } else {
                $('.pjax-active.active').removeClass('active');
            }
            bindComments();
            bindVotes();
        });

    var api_ver = 'v0',
        api_root = '/api/' + api_ver + '/'

    var Vote = Backbone.Model.extend({
        urlRoot :  api_root + 'vote'
    });

    var Votes = Backbone.Collection.extend({
        model : Vote,
        url : api_root + 'vote',
        parse: function(response) {
            return response.objects;
        } 
    });

    var votes = new Votes()

    votes.fetch()

    console.log(votes);

    var bindVotes = function() { 
        $('.up-vote').click(function(e) {
            var $targ = $(e.currentTarget);

            if (!currentUser) {
               document.location.href = '/login';
            } else {
                if (!$targ.hasClass('invisible')) {
                    $targ.addClass('invisible')

                    var data = $('#' + $targ.data('item')).data(),
                        time = new Date(),
                        vote = new Vote({
                            item_id: data['id'],
                            timestamp: time.toISOString(),
                            user_from_id: currentUser,
                            user_to_id: data['user']
                        });
                    var count = $targ.parent().find('.vote-count').text()
                    $targ.parent().find('.vote-count').text(parseInt(count) + 1)
                    vote.save()
                }
            }
        });
    };


    var bindComments = function() {
        $('.comment-input').keyup(function() {
            $('.comment-form').addClass('focus')
        });

        $('.comment-input').focusout(function() {
            if ($('.comment-input').val() == '') {
                $('.comment-form').removeClass('focus')
            }
        });


        $('.reply').click(function(e) {
            console.log('reply clicked');
            e.preventDefault()
            var $targ = $(e.currentTarget);

            var toggleForm = function($el) {
                var form_url = $el.find('a').attr("href");

                if ($el.hasClass('clicked')) {
                    $el.parent().find('form').fadeOut('fast');
                    $el.find('a').text('reply');
                        console.log('clicked');
                } else if ($el.hasClass('form-active')) {
                    $el.parent().find('form').fadeIn('fast');
                    $el.find('a').text('hide');
                        console.log('form-active');
                } else {  
                    $.getJSON(form_url, function(data) {
                        var $form = $(data.html).fadeOut();
                        $el.parent().append($form);
                        $form.fadeIn('fast');
                        $el.addClass('form-active');
                        $el.find('a').text('hide');
                        console.log('for got');
                    });
                    console.log(form_url);
                }

                $el.toggleClass('clicked');
            }

            toggleForm($targ);
        });
    };

    bindComments();
    bindVotes();



});