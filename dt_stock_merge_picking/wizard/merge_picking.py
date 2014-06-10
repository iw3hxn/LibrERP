# -*- encoding: utf-8 -*-
##############################################################################
#
#    Merge Picking up to v5 of OpenERP was written by Axelor, www.axelor.com
#    Copyright (C) 2010-2011 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff (complete rewrite)
#    Copyright (C) 2013 Didotech srl (<http://www.didotech.com>).
#    (Various adjustments, PEP8 compliance)
#
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from tools.translate import _


class stock_picking_merge_wizard(osv.osv_memory):
    _name = "stock.picking.merge.wizard"
    _description = "Merge Stock Pickings"
    
    def _get_default_target(self, cr, uid, context):
        return context.get('active_id', None)
    
    _columns = {
        "target_picking_id": fields.many2one("stock.picking", "Target Picking"),
        "picking_ids": fields.many2many("stock.picking", "wizard_stock_move_picking_merge_chosen", "merge_id", "picking_id"),

        "target_picking_id_state": fields.related("target_picking_id", "state", type="char", string="Target Picking State"),
        "target_picking_id_type": fields.related("target_picking_id", "type", type="char", string="Target Picking Type"),
        "target_picking_id_invoice_state": fields.related("target_picking_id", "invoice_state", type="char", string="Target Picking Invoice State"),

        # basic stock.picking relations are related here, they are used for the many2many field domain
        # all non-basic relations are checked after being choosen, in do_check
        "target_picking_id_stock_journal_id": fields.related("target_picking_id", "stock_journal_id", type="many2one", relation='stock.journal', string="Target Picking Journal ID"),
        "target_picking_id_location_id": fields.related("target_picking_id", "location_id", type="many2one", relation='stock.location', string="Target Picking Location"),
        "target_picking_id_location_dest_id": fields.related("target_picking_id", "location_dest_id", type="many2one", relation='stock.location', string="Target Picking Destination Location"),
        "target_picking_id_address_id": fields.related("target_picking_id", "address_id", type="many2one", relation='res.partner.address', string="Target Picking Adress"),
        "target_picking_id_company_id": fields.related("target_picking_id", "company_id", type="many2one", relation='res.company', string="Target Picking Company"),
        
        "commit_merge": fields.boolean("Commit merge"),
    }
    
    _defaults = {
        "target_picking_id": lambda self, cr, uid, context: self._get_default_target(cr, uid, context)
    }

    # dictionary of
    #   fieldname: function handling that fieldname, will not be raised as incompatibility error
    #   def specialhandler(cr, uid, fieldname, merge, target, target_changes, context=None)
    # this function is to be superseeded by subsidiary modules
    def get_specialhandlers(self):
        return {
            'origin': 'ok',
            'sale_id': 'ok'
        }

    def return_view(self, cr, uid, name, res_id):
        view_ids = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'dt_stock_merge_picking', name)
        view_id = view_ids and view_ids[1] or False
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking.merge.wizard',
            'views': [(view_id, 'form')],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': res_id,
        }
    
    def is_compatible_many2one(self, cr, uid, target, merge, context=None):
        fields_pool = self.pool.get("ir.model.fields")
        fields_search = fields_pool.search(cr, uid, [('ttype', '=', 'many2one'), ('model', '=', 'stock.picking'), ('relation', '<>', self._name)])
        failedfields = []
        for field in fields_pool.browse(cr, uid, fields_search, context):
            # don't handle specialhandlers fields as incompatible
            if field.name in self.get_specialhandlers().keys():
                continue
            
            # compare fields
            # This check is required for "dirty" databases, that still has fields
            # that are not used anymore
            if hasattr(target, field.name):
                related_target_id = getattr(target, field.name)
                related_merge_id = getattr(merge, field.name)
                if not related_target_id.id == related_merge_id.id:
                    failedfields.append(field)
        
        return {'result': (len(failedfields) == 0), 'fields': failedfields}
    
    def do_target(self, cr, uid, ids, context=None):
        # look if we got compatible views
        picking_obj = self.pool.get('stock.picking')
        
        found = False
        found_incompatible = False
        incompatible_notes = _('Near misses:')

        for session in self.browse(cr, uid, ids):
            # search if there are any compatible merges at all
            
            if context.get('active_ids', False) and len(context['active_ids']) > 1:
                merge_ids = context['active_ids']
                merge_ids.remove(context['active_id'])
            else:
                merge_ids = picking_obj.search(cr, uid, [('id', '<>', session.target_picking_id.id),
                                                         ('partner_id', '=', session.target_picking_id.partner_id.id),
                                                         ('state', '=', session.target_picking_id.state),
                                                         ('type', '=', session.target_picking_id.type),
                                                         ('invoice_state', '=', session.target_picking_id.invoice_state),
                                                         ])
            
            # ensure that many2one relations are compatible
            for merge in picking_obj.browse(cr, uid, merge_ids):
                is_compatible = self.is_compatible_many2one(cr, uid, session.target_picking_id, merge, context)
                if is_compatible['result']:
                    found = True
                else:
                    found_incompatible = True
                    for f in is_compatible['fields']:
                        desc = self.get_fieldname_translation(cr, uid, f, context)
                        incompatible_notes += "\n" + _('%s: %s (%s) differs.') % (str(merge.name), desc, f.name)
                    
        self.write(cr, uid, ids, {'picking_ids': [(6, 0, merge_ids)]})
        
        if not found:
            if found_incompatible:
                raise osv.except_osv(_('Note'), _('There are no compatible pickings to be merged.') + "\n" + incompatible_notes)
            else:
                raise osv.except_osv(_('Note'), _('There are no compatible pickings to be merged.'))
            
        return self.return_view(cr, uid, 'merge_picking_form_target', ids[0])
    
    # todo remove if http://www.openerp.com/forum/topic24128.html is solved
    def get_fieldname_translation(self, cr, uid, field, context=None):
        if ((context) and (context['lang'])):
            name = str(field.model) + "," + str(field.name)
            trans_pool = self.pool.get('ir.translation')
            trans_search = trans_pool.search(cr, uid, [('lang', '=', context['lang']), ('name', '=', name), ('type', '=', 'field')])
            for trans in trans_pool.browse(cr, uid, trans_search):
                return trans.value
        # nothing found? return untranslated
        return field.field_description
    
    def is_view(self, browse):
        # _auto=False is used to overload __init__ with a "create or replace view" if you don't need a table
        # so: return TRUE if _auto exists and is False, otherwise return False
        if (browse):
            if (hasattr(browse, "_auto")):
                if (not getattr(browse, "_auto")):
                    return True
        return False
            # ((getattr(browse, "_auto") or True)==False)
           
    def is_translateable(self, browse):
        # following a hint of Vo Minh Thu in https://bugs.launchpad.net/openobject-server/+bug/780584
        # it is still possible for a non-custom field to see if it is translatable by inspecting the _columns attribute of the model.
        if (browse):
            cols = getattr(browse, "_columns") or False
            remotefield = cols[self.remote_note] or False
            return (remotefield.translate)
        return False
    
    def do_check(self, cr, uid, ids, context=None):
        # check if pickings are compatible again with the attributes
        # depending on additional modules!
        # I could not bring those to the domain, as there are no optional module dependencies in OpenERP for XML

        for session in self.browse(cr, uid, ids):
            target = session.target_picking_id
            for merge in session.picking_ids:
                # look for incompatible moves
                for move in merge.move_lines:
                    if (move.state == 'done'):
                        raise osv.except_osv(_('Warning'),
                                             _('The following picking can not be merged due to moves in state done:') + " " + str(merge.name))
                        return self.return_view(cr, uid, 'merge_picking_form_target', ids[0])
                    
                # test all many2one fields for compability,as we can't link to different targets from one merged object!
                # yes, we still need this, if we come from a link on stock.picking views, we don't have the first check!
                is_compatible = self.is_compatible_many2one(cr, uid, target, merge, context)
                if (not is_compatible['result']):
                    ex = _('The picking %s can not be merged due to different references:') % (str(merge.name))
                    for f in is_compatible['fields']:
                        desc = self.get_fieldname_translation(cr, uid, f, context)
                        ex += "\n" + desc + " (" + f.name + ")"
                    raise osv.except_osv(_('Warning'), ex)
                    return self.return_view(cr, uid, 'merge_picking_form_target', ids[0])
         
        return self.return_view(cr, uid, 'merge_picking_form_checked', ids[0])
    
    def do_merge(self, cr, uid, ids, context=None):
        # bail out if checkbox not set
        for session in self.browse(cr, uid, ids):
            if not session.commit_merge:
                raise osv.except_osv(_('Unchecked'), _('You did not check the Commit Merge checkbox.'))
                return self.return_view(cr, uid, 'merge_picking_form_checked', ids[0])
            
        # merge
        picking_obj = self.pool.get("stock.picking")
        fields_pool = self.pool.get("ir.model.fields")
    
        for session in self.browse(cr, uid, ids):
            target = session.target_picking_id
            
            target_changes = {"date_done": target.date_done}

            # prepare notes, esp. if not existing
            if (target.note):
                target_changes['note'] = target.note + "\n"
            else:
                target_changes['note'] = ""

            if (target.merge_notes):
                target_changes['merge_notes'] = target.merge_notes + ";\n"
            else:
                target_changes['merge_notes'] = ""
            target_changes['merge_notes'] += "This is a merge target."
            
            for merge in session.picking_ids:
                # fetch notes

                linenote = " Merged " + str(merge.name)
                if (merge.origin != target.origin):
                    linenote += ", had Origin " + str(merge.origin)
                
                if (merge.date != target.date):
                    linenote += ", from " + str(merge.date)

                if (merge.note):
                    linenote += ", Notes: " + str(merge.note)

                target_changes['merge_notes'] += linenote + ";\n"

                if (merge.note):
                    target_changes['note'] += str(merge.note) + "\n"

                # handle changeable values

                # if any one merge has partial delivery, deliver the whole picking as partial (direct)
                if (merge.move_type == 'direct'):
                    target_changes['move_type'] = 'direct'
                
                # date_done = MAX(date_done)
                if (target_changes['date_done'] < merge.date_done):
                    target_changes['date_done'] = merge.date_done
                
                # if any one merge is NOT auto_picking, then the target is not.
                # should never occur, as auto_picking would set it to done instantly, which can't be merged
                if (not (merge.auto_picking)):
                    target_changes['auto_picking'] = False
                
                # search for all outgoing related fields.
                # we handle only ougoing many2one (incoming one2many may not exist for that) here
                # this IS neccessary, but only to catch specialhandler-handled fields.
                # must be done before the next search, because refs might have been destroyed later
                #fields_search = fields_pool.search(cr, uid, [('model','=','stock.picking'),('ttype','=','many2one')])
                                
                # go through these fields
                #for field in fields_pool.browse(cr, uid, fields_search):
                #
                #    if field.name in self.get_specialhandlers().keys():
                #        # use special handler
                #        specialhandler_name = self.get_specialhandlers().get(field.name)
                #        specialhandler = getattr(self, specialhandler_name)
                #        target_changes = specialhandler(cr, uid, field.name, merge, target, target_changes)
                
                # search for all incoming related fields.
                # we don't need to handle one2many here: would be backlinked versions of many2one anyway.
                fields_search = fields_pool.search(cr, uid, [('relation', '=', 'stock.picking'), ('model', '<>', self._name),
                                                             '|', ('ttype', '=', 'many2one'), ('ttype', '=', 'many2many')])
                
                ## go through these fields
                #for field in fields_pool.browse(cr, uid, fields_search):
                #    if field.name in self.get_specialhandlers().keys():
                #        # use special handler
                #        specialhandler_name = self.get_specialhandlers().get(field.name)
                #        specialhandler = getattr(self, specialhandler_name)
                #        target_changes = specialhandler(cr, uid, field.name, merge, target, target_changes)
                        
                ## update all relations to the old picking to look for the new one
                ## includes stock.move lines merge

                # go through these fields and change things, using field_search from before (many2one | many2many)
                for field in fields_pool.browse(cr, uid, fields_search):
                    if not field.name in self.get_specialhandlers().keys():
                        # find the model they're in
                        model_obj = self.pool.get(field.model)

                        # this can happen if you deinstalled modules by deleting their code, so they left something behind in the definition.
                        if (not model_obj):
                            continue

                        # do not handle relations to views
                        if self.is_view(model_obj):
                            continue
                        
                        # handle many2one: simply replace the id
                        if field.ttype == 'many2one':
                            # find all entries that are old
                            model_ids = model_obj.search(cr, uid, [(field.name, '=', merge.id)])
                            
                            if field.name == 'picking_id' and field.model == 'stock.move':
                                if merge.sale_id:
                                    no_origin_ids = model_obj.search(cr, uid, [(field.name, '=', merge.id), '|', ('origin_document', '=', False), ('origin_document', '=', '')])
                                    model_obj.write(cr, uid, no_origin_ids, {'origin_document': "sale.order, {0}".format(merge.sale_id.id)})
                            
                            # and update them in one go
                            model_obj.write(cr, uid, model_ids, {field.name: target.id})
    
                        # handle many2many:
                        if field.ttype == 'many2many':
                            # find all entries that are old (don't know how yet, so I'll have to take 'em all
                            model_search = model_obj.search(cr, uid, [])  # (field.name,'=',merge.id)
                            # and update them in one go
                            model_obj.write(cr, uid, model_search, {field.name: [(3, merge.id), (4, target.id)]})
                        
                # updated everything, so now I can get rid of the object
                picking_obj.unlink(cr, uid, [merge.id])
            
            # /for merge
            picking_obj.write(cr, uid, [target.id], target_changes)
                
        return self.return_view(cr, uid, 'merge_picking_form_done', ids[0])
