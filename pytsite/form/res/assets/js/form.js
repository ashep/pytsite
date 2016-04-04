pytsite.form = {
    Form: function (em) {
        var self = this;
        self.em = em;
        self.id = em.attr('id');
        self.cid = em.data('cid');
        self.getWidgetsEp = em.data('getWidgetsEp');
        self.validationEp = em.data('validationEp');
        self.reloadOnForward = em.data('reloadOnForward') == 'True';
        self.submitEp = em.attr('submitEp');
        self.totalSteps = em.data('steps');
        self.loadedSteps = [];
        self.currentStep = 0;
        self.isCurrentStepValidated = true;
        self.readyToSubmit = false;
        self.areas = {};
        self.title = self.em.find('.form-title');
        self.messages = self.em.find('.form-messages');
        self.widgets = {};

        // Initialize areas
        em.find('.form-area').each(function () {
            self.areas[$(this).data('formArea')] = $(this);
        });

        // Form submit handler
        self.em.submit(function (event) {
            if (!self.readyToSubmit) {
                event.preventDefault();
                self.forward();
            }
        });

        self.serialize = function (skipTags) {
            function getEmValue(em) {
                if (em.tagName == 'INPUT' && em.type == 'checkbox')
                    return em.checked;
                else
                    return em.value;
            }

            var r = {};

            self.em.find('[name]').each(function () {
                if (skipTags instanceof Array && this.tagName in skipTags)
                    return;

                if (!(this.name in r)) {
                    if (this.name.indexOf('[]') > 0)
                        r[this.name] = [getEmValue(this)];
                    else
                        r[this.name] = getEmValue(this);
                }
                else {
                    if (r[this.name] instanceof Array)
                        r[this.name].push(getEmValue(this));
                    else
                        r[this.name] = getEmValue(this);
                }
            });

            for (var k in r) {
                if (r[k] instanceof Array && r[k].length == 1)
                    r[k] = r[k][0];
            }

            return r;
        };

        // Do an AJAX request
        self._request = function (method, ep) {
            var data = self.serialize();

            // Add form's data-attributes
            var emDataAttrs = self.em.data();
            for (var k in emDataAttrs) {
                if ($.inArray(k, ['getWidgetsEp', 'validationEp', 'reloadOnForward', 'steps']) < 0)
                    data['__form_data_' + k] = emDataAttrs[k];
            }

            // Merge data from location query
            $.extend(data, pytsite.browser.getLocation(true).query);

            // Calculate form location string
            var q = pytsite.browser.getLocation().query;
            $.extend(q, self.serialize(['TEXTAREA']));
            q['__form_data_step'] = self.currentStep;
            var formLocation = location.origin + location.pathname + '?' + pytsite.browser.encodeQuery(q);

            data['__form_data_step'] = self.currentStep;
            data['__form_data_location'] = formLocation;

            return pytsite.ajax.request(method, ep, data)
                .fail(function (resp) {
                    if ('responseJSON' in resp && 'error' in resp.responseJSON)
                        self.addMessage(resp.responseJSON.error, 'danger');
                    else
                        self.addMessage(resp.statusText, 'danger');
                });
        };

        // Get form's title
        self.setTitle = function (title) {
            self.title.html('<h4>' + title + '</h4>');
        };

        // Clear form's messages
        self.clearMessages = function () {
            self.messages.html('');
        };

        // Add a message to the form
        self.addMessage = function (msg, type) {
            if (!type)
                type = 'info';

            self.messages.append('<div class="alert alert-' + type + '" role="alert">' + msg + '</div>')
        };

        // Add a widget to the form
        self.addWidget = function (widgetData) {
            // Initialize widget
            var widget = new pytsite.widget.Widget(widgetData);

            if (widget.uid in self.widgets) {
                if (widget.replaces == widget.uid)
                    self.removeWidget(widget.uid);
                else
                    throw "Widget '" + widget.uid + "' already exists.";
            }

            // Append widget to the form
            widget.hide();
            self.areas[widget.formArea].append(widget.em);
            self.widgets[widget.uid] = widget;
        };

        // Remove widget from the form
        self.removeWidget = function (uid) {
            if (!(uid in self.widgets))
                return;

            self.widgets[uid].em.remove();
            delete self.widgets[uid];
        };

        // Load widgets for the current step
        self.loadWidgets = function (showAfterLoad) {
            var progress = self.areas['body'].find('.progress');

            // Show progress bar
            progress.find('.progress-bar').css('width', '0');
            progress.removeClass('hidden');

            return self._request('POST', self.getWidgetsEp)
                .done(function (resp) {

                    var totalWidgets = resp.length;

                    for (var i = 0; i < totalWidgets; i++) {
                        // Increase progress bar value
                        var percents = (100 / totalWidgets) * (i + 1);
                        progress.find('.progress-bar').css('width', percents + '%');

                        // Append widget
                        self.addWidget(resp[i]);
                    }

                    // Hide progress bar
                    progress.addClass('hidden');

                    // Fill widgets with data from location string
                    self.fill(pytsite.browser.getLocation().query);

                    // Show loaded widgets
                    if (showAfterLoad == true)
                        self.showWidgets();
                });
        };

        // Fill form with data
        self.fill = function (data) {
            for (k in data)
                self.em.find('[name="' + k + '"]').val(data[k]);

            return self;
        };

        // Do form validation
        self.validate = function () {
            var deffer = $.Deferred();

            deffer.done(function () {
                self.isCurrentStepValidated = true;
            });

            if (self.currentStep > 0) {
                // Reset widgets state
                for (var uid in self.widgets)
                    self.widgets[uid].clearState().clearMessages();

                self._request('POST', self.validationEp).done(function (resp) {
                    if (resp.status) {
                        deffer.resolve();
                    }
                    else {
                        // Add error messages for widgets
                        for (var uid in resp.messages) {
                            if (uid in self.widgets) {
                                var widget = self.widgets[uid];
                                widget.setState('error');

                                for (var i = 0; i < resp.messages[uid].length; i++) {
                                    widget.addMessage(resp.messages[uid]);
                                }
                            }
                        }

                        $("html, body").animate({ scrollTop: self.em.find('.has-error').first().offset().top + 'px' });
                        deffer.reject();
                    }
                });
            }
            else {
                deffer.resolve();
            }

            return deffer;
        };

        // Show widgets for the step
        self.showWidgets = function (step) {
            if (step == undefined)
                step = self.currentStep;

            for (var uid in self.widgets) {
                if (self.widgets[uid].formStep == step)
                    self.widgets[uid].show();
            }

            return self;
        };

        // Hide widgets for the step
        self.hideWidgets = function (step) {
            if (step == undefined)
                step = self.currentStep;

            for (var uid in self.widgets) {
                if (self.widgets[uid].formStep == step)
                    self.widgets[uid].hide();
            }

            return self;
        };

        // Remove widgets for the step
        self.removeWidgets = function (step) {
            for (var uid in self.widgets) {
                if (self.widgets[uid].formStep == step)
                    self.removeWidget(uid);
            }
        };

        // Move to the next step
        self.forward = function () {
            var deffer = $.Deferred();

            // Validating the form for the current step
            self.validate()
                .done(function () {
                    // It is not a last step, so just load (if necessary) and show widgets for the next step
                    if (self.currentStep < self.totalSteps) {
                        // Hide widgets for the current step
                        self.hideWidgets();

                        // Step change
                        ++self.currentStep;

                        // Load widgets via AJAX request, if necessary
                        if ($.inArray(self.currentStep, self.loadedSteps) < 0 || self.reloadOnForward) {
                            // First, remove all existing widgets for the current step
                            self.removeWidgets(self.currentStep);

                            // Load widgets for the current step
                            self.loadWidgets()
                                .done(function () {
                                    if ($.inArray(self.currentStep, self.loadedSteps) < 0)
                                        self.loadedSteps.push(self.currentStep);

                                    // Attach click handler to the 'Backward' button
                                    self.em.find('.form-action-backward').click(self.backward);

                                    // Show widgets
                                    self.isCurrentStepValidated = false;
                                    self.showWidgets();
                                    $(self).trigger('pytsite.form.forward');
                                    deffer.resolve();
                                });
                        }
                        // Just show widgets, if they already loaded
                        else {
                            // Show widgets
                            self.isCurrentStepValidated = false;
                            self.showWidgets();
                            $(self).trigger('pytsite.form.forward');
                            deffer.resolve();
                        }
                    }
                    // It is a last step, just allowing submit the form
                    else {
                        self.readyToSubmit = true;
                        self.em.submit();
                    }
                })
                .fail(function () {
                    deffer.reject();
                });

            return deffer;
        };

        // Move to the previous step
        self.backward = function () {
            self.hideWidgets(self.currentStep);
            --self.currentStep;
            self.showWidgets(self.currentStep)
        };
    }
};


$(function () {
    // Initialize all forms on the page after page loading
    $('.pytsite-form').each(function () {
        // Initialize form
        var form = new pytsite.form.Form($(this));

        // If requested to walk to particular step automatically
        var q = pytsite.browser.getLocation().query;
        var walkToStep = '__form_data_step' in q ? parseInt(q['__form_data_step']) : 1;
        $(form).on('pytsite.form.forward', function () {
            if (form.currentStep < walkToStep)
                form.forward();
        });

        // Do the first step
        form.forward();
    });
});
