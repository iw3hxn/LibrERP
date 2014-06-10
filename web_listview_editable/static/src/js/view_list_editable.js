openerp.web_listview_editable = function (openerp) {
    var KEY_RETURN  = 13,
        KEY_ESCAPE  = 27,
        LEFT_ARROW  = 37,
        UP_ARROW    = 38,
        RIGHT_ARROW = 39,
        DOWN_ARROW  = 40;
    var QWeb = openerp.web.qweb;

    // add getCursorPosition, isCursorAtStart and isCursorAtEnd
    // functions to jQuery
    (function ($, undefined) {
	$.fn.getCursorPosition = function() {
            var el = $(this).get(0);
            var pos = 0;
            if('selectionStart' in el) {
		pos = el.selectionStart;
            } else if('selection' in document) {
		el.focus();
		var sel = document.selection.createRange();
		var selLength = document.selection.createRange().text.length;
		sel.moveStart('character', -el.value.length);
		pos = sel.text.length - selLength;
            }
            return pos;
	};
	$.fn.isCursorAtStart = function () {
	    return ($(this).getCursorPosition() === 0);
	};
	$.fn.isCursorAtEnd = function () {
	    return ($(this).getCursorPosition() === $(this).val().length);
	};
    })(jQuery);

    openerp.web.ListView.List.include(/** @lends openerp.web.ListView.List# */{
	cell_widths: [],
        row_clicked: function (event) {
	    var self = this;
            if (!this.options.editable) {
                return this._super.apply(this, arguments);
            }
	    if (self.cell_widths.length === 0) {
		self.cell_widths = $(event.currentTarget).closest('table.oe-listview-content').find('tr.oe-listview-header-columns').find('th').map(function () { return parseInt($(this).width()); }).get();
	    }
            this.edit_record($(event.currentTarget).data('id'),
			    (($(event.target).prop('tagName').toLowerCase() === 'td') ? $(event.target).prevAll('td').length : null));
        },
        cancel_pending_edition: function () {
            var self = this, cancelled;
            if (!this.edition) {
                return $.when();
            }

            if (this.edition_id) {
                cancelled = this.reload_record(this.records.get(this.edition_id));
            } else {
                cancelled = $.when();
            }
            cancelled.then(function () {
                self.view.unpad_columns();
		if (self.edition_form) {
                    self.edition_form.stop();
                    self.edition_form.$element.remove();
                    delete self.edition_form;
		}
                self.dataset.index = null;
                delete self.edition_id;
                delete self.edition;
            });
            this.pad_table_to(5);
            return cancelled;
        },
        on_row_keyup: function (e) {
            var self = this;
            switch (e.which) {
            case KEY_RETURN:
                $(e.target).blur();
                e.preventDefault();
                //e.stopImmediatePropagation();
                setTimeout(function () {
                    self.save_row().then(function (result) {
                        if (result.created) {
                            self.new_record();
                            return;
                        }

                        var next_record_id,
                            next_record = self.records.at(
                                    self.records.indexOf(result.edited_record) + 1);
                        if (next_record) {
                            next_record_id = next_record.get('id');
                            self.dataset.index = _(self.dataset.ids)
                                    .indexOf(next_record_id);
                        } else {
                            self.dataset.index = 0;
                            next_record_id = self.records.at(0).get('id');
                        }
                        self.edit_record(next_record_id);
                    }, 0);
                });
                break;
            case KEY_ESCAPE:
                this.cancel_edition();
                break;
	    case UP_ARROW:
		if (this.navigate_in_grid(e, 'up')) { e.preventDefault(); }
		break;
	    case DOWN_ARROW:
		if (this.navigate_in_grid(e, 'down')) { e.preventDefault(); }
		break;
	    case LEFT_ARROW:
		if (this.navigate_in_grid(e, 'left')) { e.preventDefault(); }
		break;
	    case RIGHT_ARROW:
		if (this.navigate_in_grid(e, 'right')) { e.preventDefault(); }
		break;
            }
        },
	navigate_in_grid: function(event, direction) {
	    var $target = $(event.target);
	    var $cell = $target.parents('.oe-field-cell').first();
	    var $row = $target.parents('tr.oe_forms').first();
	    var $moveto;

	    switch (direction) {

	    case 'up':
		$moveto = $row.prev();
		if ($moveto.length) {
		    this.edit_record($moveto.data('id'), $cell.prevAll('td').length);
		    return true;
		}
		return false;
	    case 'down':
		$moveto = $row.next();
		if (($moveto.length) && ($moveto.data('id'))) {
		    this.edit_record($moveto.data('id'), $cell.prevAll('td').length);
		    return true;
		}
		return false;
	    case 'left':
		if ($target.isCursorAtStart()) {
		    if ($target.data('move-left')) {
			$moveto = $cell.prev();
			if ($moveto.length) {
			    $target.data('move-left', false);
			    $moveto.find('input').focus();
			    $moveto.find('textarea').focus();
			    return true;
			}
		    } else {
			$target.data('move-left', true);
		    }
		}
		return false;
	    case 'right':
		if ($target.isCursorAtEnd()) {
		    if ($target.data('move-right')) {
			$moveto = $cell.next();
			if ($moveto.length) {
			    $target.data('move-right', false);
			    $moveto.find('input').focus();
			    $moveto.find('textarea').focus();
			    return true;
			}
		    } else {
			$target.data('move-right', true);
		    }
		}
		return false;
	    default: return false;
	    }
	},
        render_row_as_form: function (row, cell_position) {
            var self = this;
            return this.ensure_saved().pipe(function () {
                var record_id = $(row).data('id');
                var $new_row = $('<tr>', {
                        id: _.uniqueId('oe-editable-row-'),
                        'data-id': record_id,
                        'class': (row ? $(row).attr('class') : '') + ' oe_forms',
                        click: function (e) {e.stopPropagation();}
                    })
                    .delegate('button.oe-edit-row-save', 'click', function () {
                        self.save_row();
                    })
                    .delegate('button', 'keyup', function (e) {
                        e.stopImmediatePropagation();
                    })
                    .keyup(function () {
                        return self.on_row_keyup.apply(self, arguments); })
                    .keydown(function (e) { e.stopPropagation(); })
                    .keypress(function (e) {
                        if (e.which === KEY_RETURN) {
                            return false;
                        }
                    });

                if (row) {
                    $new_row.replaceAll(row);
                } else if (self.options.editable) {
                    var $last_child = self.$current.children('tr:last');
                    if (self.records.length) {
                        if (self.options.editable === 'top') {
                            $new_row.insertBefore(
                                self.$current.children('[data-id]:first'));
                        } else {
                            $new_row.insertAfter(
                                self.$current.children('[data-id]:last'));
                        }
                    } else {
                        $new_row.prependTo(self.$current);
                    }
                    if ($last_child.is(':not([data-id])')) {
                        $last_child.remove();
                    }
                }
                self.edition = true;
                self.edition_id = record_id;
                self.dataset.index = _(self.dataset.ids).indexOf(record_id);
                if (self.dataset.index === -1) {
                    self.dataset.index = null;
                }
                self.edition_form = _.extend(new openerp.web.ListEditableFormView(self.view, self.dataset, false), {
                    form_template: 'ListView.row.form',
                    registry: openerp.web.list.form.widgets,
                    $element: $new_row
                });
                // HA HA
                self.edition_form.appendTo();
                // put in $.when just in case  FormView.on_loaded becomes asynchronous
                return $.when(self.edition_form.on_loaded(self.get_form_fields_view())).then(function () {
                    if (self.options.selectable) {
                        $new_row.prepend('<th>');
                    }
                    if (self.options.isClarkGable) {
                        $new_row.prepend('<th>');
                    }
                    // pad in case of groupby
                    _(self.columns).each(function (column) {
                        if (column.meta) {
                            $new_row.prepend('<td>');
                        }
                    });
                    // Add column for the save, if
                    // there is none in the list
                    if (!self.options.deletable) {
                        self.view.pad_columns(
                            1, {except: $new_row});
                    }

                    self.edition_form.do_show();

		    if ((self.cell_widths) && (self.cell_widths.length > 0)) {
			$new_row.find('th:first').css('width',self.cell_widths[0]);
		    	$new_row.find('> td').each(function (i) { $(this).addClass('oe-field-cell')
								      .css('width', self.cell_widths[i+1]);
		    						  $(this).find('input').css('width', self.cell_widths[i+1])
                                                                      .css('min-width', 25);
		    						  $(this).find('textarea').css('width', self.cell_widths[i+1])
                                                                      .css('min-width', 25).css('height', 22);
								});
		    	$new_row.find('td:last').removeClass('oe-field-cell');

		    } else {
                        $new_row.find('> td').addClass('oe-field-cell')
		    	    .find('td:last').removeClass('oe-field-cell').end();
		    }

		    // set the focus to the clicked cell
		    setTimeout(function () {
			var input = $new_row.find('> td:eq(' + cell_position + ') input:eq(0)');
			if (input.length > 0) { input[0].focus(); return; }
			var textarea = $new_row.find('> td:eq(' + cell_position + ') textarea:eq(0)');
			if (textarea.length > 0) { textarea[0].focus(); return; }
		    }, 100);

                });
            });
        },
        edit_record: function (record_id, target_position) {
            this.render_row_as_form(
                this.$current.find('[data-id=' + record_id + ']'),
		target_position);
            $(this).trigger(
                'edit',
                [record_id, this.dataset]);
        },
        new_record: function () {
	    if (this.cell_widths.length === 0) {
		this.cell_widths = this.$current.closest('table.oe-listview-content').find('tr.oe-listview-header-columns').find('th').map(function () { return parseInt($(this).width()); }).get();
	    }
            this.render_row_as_form();
        }
    });
};
