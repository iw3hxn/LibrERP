/*##############################################################################*/
//  OpenERP, Open Source Management Solution
//  Copyright (C) 2011 - 2013 Denero Team. (<http://www.deneroteam.com>)
//
//  This program is free software: you can redistribute it and/or modify
//  it under the terms of the GNU Affero General Public License as
//  published by the Free Software Foundation, either version 3 of the
//  License, or (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU Affero General Public License for more details.
//
//  You should have received a copy of the GNU Affero General Public License
//  along with this program.  If not, see <http://www.gnu.org/licenses/>.
//##############################################################################

openerp.web_mask_text = function(openerp) {
openerp.web.form.FieldChar = openerp.web.form.FieldChar.extend({
    start: function() {
        this._super.apply(this,arguments);
        if (this.node.attrs.mask)  {
            var $input = this.$element.find('input');
            $input.mask(this.node.attrs.mask)
        }
    }
    });
};

// vim:et fdc=0 fdl=0:
