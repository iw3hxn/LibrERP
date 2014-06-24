# -*- coding: utf-8 -*-

from osv import fields, osv
from tools.translate import _
import time

# Dummy to be used by stock picking, so many2one exists when one2many is established
class stock_picking_group_blanco(osv.osv):
    _name = "stock.picking.group"
stock_picking_group_blanco()


class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = _name

    _columns = {
        "picking_group_id": fields.many2one("stock.picking.group", string="Picking Group"),
    }
    
    def action_group(self, cr, uid, ids, context=None):
        # nothing to process
        if len(context['active_ids']) == 0:
            return {}
        
        # checks
        for item in self.browse(cr, uid, context['active_ids'], context):            
            if (item.picking_group_id):
                raise osv.except_osv(_('Grouping failed.'), _('You cannot re-group %s. Remove existing grouping first.') % (item.name))
        
        picking_ids = [x for x in context['active_ids']] #copy list
        # without loss of generality, we choose the last (pop()) one to compare all others to
        wlog_id = picking_ids.pop()
        wlog_item = self.browse(cr, uid, wlog_id, context)

        # iterate through others        
        for item in self.browse(cr, uid, picking_ids, context):
            
            # check for type    
            if (wlog_item.type != item.type):
                raise osv.except_osv(_('Grouping failed.'), _('%s (%s) and %s (%s) have different types.') 
                                                            % (wlog_item.name, wlog_item.type, item.name, item.type))
                
            # check for address
            wlog_address = wlog_item.address_id and wlog_item.address_id.id or None
            item_address = item.address_id and item.address_id.id or None

            if (wlog_address == None and item_address != None):
                raise osv.except_osv(_('Grouping failed.'), _('%s has a target address, %s has not.') % ( item.name, wlog_item.name))
            elif (wlog_address != None and item_address == None):
                raise osv.except_osv(_('Grouping failed.'), _('%s has a target address, %s has not.') % ( wlog_item.name, item.name))
            elif (wlog_address != item_address):
                raise osv.except_osv(_('Grouping failed.'), _('%s and %s have different target addresses.') % (wlog_item.name, item.name))

            # check for company    
            if (wlog_item.company_id.id != item.company_id.id):
                raise osv.except_osv(_('Grouping failed.'), _('%s (%s) and %s (%s) belong to different companies.') 
                                                            % (wlog_item.name, wlog_item.company_id.name, item.name, item.company_id.name))

        # create grouping
        group_obj = self.pool.get("stock.picking.group")
        
        # create empty group
        new_group = group_obj.create(cr,uid,{})
        
        # and use for the requested pickings
        self.write(cr, uid, context['active_ids'], {'picking_group_id': new_group}, context=context)

        # and update fields
        group_obj.update_stored(cr, uid, [new_group], context=context)

        # opening picking group window
        data_pool = self.pool.get('ir.model.data')
        view_result = data_pool.get_object_reference(cr, uid, 'stock_picking_group', 'picking_group_form')
        view_id = view_result and view_result[1] or False
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'stock.picking.group',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': new_group,
                'context': context,
        }
    
        
    # handle back orders - the old order is the rest, not the just processed items
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        print "do_partial in stock_picking_group: start"
        # before
        before = {}
        for picking in self.browse(cr, uid, ids, context=context):
            group = picking.picking_group_id and picking.picking_group_id.id or None
            backorder = picking.backorder_id and picking.backorder_id.id or None
            before[picking.id] = { 'backorder': backorder, 'group': group }
        
        # process partial 
        result = super(stock_picking, self).do_partial(cr, uid, ids, partial_datas, context)

        # after
        for picking in self.browse(cr, uid, ids, context=context):
            group = picking.picking_group_id and picking.picking_group_id.id or None
            backorder = picking.backorder_id and picking.backorder_id.id or None
            
            if (before[picking.id]['backorder'] != backorder):
                # was changed, so switch backorders[picking.id] and backorder_id on before[group]

                # add new, processed picking (set as "backorder of" on the current picking) to the group
                print "writing ",{'picking_group_id': before[picking.id]['group']},"to",backorder
                self.write(cr, uid, [backorder], {'picking_group_id': before[picking.id]['group']}, context)

                print "writing ",{'picking_group_id': False},"to",picking.id
                # remove the current, unprocessed picking from the group
                self.write(cr, uid, [picking.id], {'picking_group_id': False}, context)
        
        # switch if neccessary
        print "do_partial in stock_picking_group: end"
        return result

    
stock_picking()


class stock_picking_group(osv.osv):
    _name = "stock.picking.group"
    _inherit = _name
             
    def _get_naming(self, pickingtype):
        # TODO replace with live sequence prefix (codes "Picking IN", "Picking INT", "Picking OUT")
        naming = {'internal': 'INT/', 'out': 'OUT/', 'in': 'IN/'}
        return naming[pickingtype]
                                    
    # get list of picking names (for display, easier reference.)                   
    # will be stored, to be searchable
    def _get_list(self, cr, uid, ids, field_name=None, arg=None, context=None):
        res = {}
        for session in self.browse(cr, uid, ids):
            r = []
            for pick in session.picking_ids:
                r.append(pick.name)
            res[session.id] = ", ".join(r)
        return res
    
    # get name by type and group id
    def _get_name(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for session in self.browse(cr, uid, ids):
            if (not session.type): # happens when creating from action
                res[session.id] = "-unset-"
            else:
                res[session.id] = self._get_naming(session.type) + 'GRP' + str(session.id)
        return res
    
    # get combined list of moves from all pickings
    def _get_move_ids(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for session in self.browse(cr, uid, ids):
            move_ids = {}
            for p in session.picking_ids:
                for m in p.move_lines:
                    move_ids[m.id] = m.id
            res[session.id] = move_ids.keys()
        return res
    
    # get combined notes from all pickings
    def _get_notes(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for session in self.browse(cr, uid, ids):
            n = ""
            for p in session.picking_ids:
                if (p.note):
                    # add picking name and note, where the note puts in no additional newlines
                    n = n + p.name + ":\n" + p.note.rstrip("\r\n").rstrip("\n") + "\n\n"
            
            n = n.rstrip("\n")
            n = n.strip()
            
            res[session.id] = n
        return res
    
    
    # get type and address_id from any picking (here: first, as they are equal by design)  
    def _get_info(self, cr, uid, ids, field_name=None, arg=None, context=None):
        res = {}
        for session in self.browse(cr, uid, ids):
            company = self.pool.get('res.company')._company_default_get(cr, uid, 'stock.picking.group', context=context)
            res[session.id] = {'type': 'internal', 'address_id': None, 'company_id': company}
            if (session.picking_ids):
                first_picking = session.picking_ids[0]
                res[session.id] = {'type': first_picking.type, 'address_id': first_picking.address_id.id, 'company_id': first_picking.company_id.id}
        return res
    
    # get group ids from picking, for store trigger
    def _getstore_picking(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get("stock.picking")
        r = []
        for p in picking_obj.browse(cr, uid, ids, context=context):
            if (p.picking_group_id):
                r.append(p.picking_group_id.id)
        return r

    # get group ids from group..., for store trigger
    def _getstore_self(self, cr, uid, ids, context=None):
        # working on this end already...
        return ids

    # update stored values (trying to figure out the "-unset-" reference problem, likely semi-concurrent accessing
    def update_stored(self, cr, uid, ids, context=None):
        info = self._get_info(cr, uid, ids, context=context)
        lst = self._get_list(cr, uid, ids, context=context)
        for session in self.browse(cr, uid, ids):
            data = {'name': self._get_naming(info[session.id]['type']) + 'GRP' + str(session.id),
                    'list': lst[session.id],
                    'type': info[session.id]['type'],
                    'address_id': info[session.id]['address_id'],
                    'company_id': info[session.id]['company_id']}
            self.write(cr, uid, session.id, data)
            

    
    _columns = {
        "name": fields.function(_get_name, string="Reference", type='char', size=75, method=True, store=False),
        # this does a lot of -unset- on entries created by action from picking.
        # I suspect it happens when picking_ids is not connected, hence no store as of now
        # update_stored did not work 
#                                    store={'stock.picking': (_getstore_picking, ['type','picking_group_id'], 10),
#                                           'stock.picking.group': (_getstore_self, ['picking_ids'], 20)}),
        "list": fields.function(_get_list, string="Pickings", type='char', size=255, method=True,
                                    store={'stock.picking': (_getstore_picking, ['picking_group_id'], 10),
                                           'stock.picking.group': (_getstore_self, ['picking_ids'], 20)}),
        "type": fields.function(_get_info, multi="type", string="Type", type='char', size=75, method=True,
                                    store={'stock.picking': (_getstore_picking, ['picking_group_id','type'], 10),
                                           'stock.picking.group': (_getstore_self, ['picking_ids'], 20)}),
        "address_id": fields.function(_get_info, multi="address_id", string="Address", type='many2one', relation="res.partner.address", method=True,
                                    store={'stock.picking': (_getstore_picking, ['picking_group_id','address_id'], 10),
                                           'stock.picking.group': (_getstore_self, ['picking_ids'], 20)}),
        "company_id": fields.function(_get_info, multi="address_id", string="Address", type='many2one', relation="res.company", method=True,
                                    store={'stock.picking': (_getstore_picking, ['picking_group_id','company_id'], 10),
                                           'stock.picking.group': (_getstore_self, ['picking_ids'], 20)}),
        "picking_ids": fields.one2many("stock.picking", "picking_group_id", name="Picking group"),
        "partner_id": fields.related("address_id", "partner_id", type="many2one", relation="res.partner", string="Partner"),
        "move_lines": fields.function(_get_move_ids, string="Moves", type='many2many', relation="stock.move", method=True, store=False),
        "date": fields.datetime("Date",help="Date when the grouping was created", required=True),
        "note": fields.function(_get_notes, string="Notes", type='text', method=True, store=False),
    }

    _defaults = {
        "date": lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    # wrapper for multiple group ids checked
    def _check_grouped_compatible_picking(self, cr, uid, ids, context=None):
        for g in self.browse(cr, uid, ids, context=context):
            pickings = [p.id for p in g.picking_ids]
            check = self._check_compatible_picking(cr, uid, pickings, context)
            if (not check):
                return False  
        # all ok? then true
        return True

    # check compatibility
    # yes, operating on picking. Maybe this would be better in picking class, but for now it's here.
    def _check_compatible_picking(self, cr, uid, picking_ids, context=None):
        if (len(picking_ids) < 2):
            # one or no item? is compatible with itself
            return True

        picking_obj = self.pool.get("stock.picking")

        # Without Loss Of Generality, we take the last (pop()) item to compare all later ones to
        wlog_id = picking_ids.pop()
        wlog = picking_obj.browse(cr, uid, wlog_id, context=context)
         
        for p in picking_obj.browse(cr, uid, picking_ids, context=context):
            # compare types
            if (wlog.type <> p.type):
                return False
            
            # compare company
            if (wlog.company_id.id <> p.company_id.id):
                return False
            
            # compare address
            wlog_address = wlog.address_id and wlog.address_id.id or None
            p_address = p.address_id and p.address_id.id or None
            if (wlog_address <> p_address):
                return False
        ## no problems occured
        return True
     
    _constraints = [
        (_check_grouped_compatible_picking, 'The pickings you chose are not compatible (type or address varies, or from different companies)', ['picking_ids']),
    ]
            
        
stock_picking_group()
