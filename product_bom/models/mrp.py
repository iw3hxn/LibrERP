# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2014 Didotech srl (info@didotech.com)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
import re

from openerp.osv import orm
from openerp.tools.config import config
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
ENABLE_CACHE = config.get('product_cache', False)


class mrp_bom(orm.Model):
    _inherit = 'mrp.bom'
    
    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not vals.get('bom_id', False):
            self.pool['product.product'].write(
                cr, uid, vals['product_id'],
                {'supply_method': 'produce', 'purchase_ok': False},
                context
            )
            if vals.get('product_id', False):
                for product_id in self.GetWhereUsed(cr, uid, [vals['product_id']], context)[1].keys():
                    if int(product_id) in self.pool['product.product'].product_cost_cache:
                        del self.pool['product.product'].product_cost_cache[int(product_id)]

        return super(mrp_bom, self).create(cr, uid, vals, context=context)
    
    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        product_obj = self.pool['product.product']
        bom_ids = []

        for bom in self.browse(cr, uid, ids, context):
            if not bom.bom_id:
                bom_ids.append(bom.id)

        boms = self.browse(cr, uid, bom_ids, context)
        for product_id in [bom.product_id.id for bom in boms]:
            bom_ids_count = self.search(cr, uid, [('product_id', '=', product_id), ('bom_id', '=', False)], count=True)

            if bom_ids_count == 1:
                product_obj.write(cr, uid, product_id, {'supply_method': 'buy', 'purchase_ok': True}, context=context)

        return super(mrp_bom, self).unlink(cr, uid, ids, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if isinstance(ids, (int, long)):
            ids = [ids]
        boms = self.browse(cr, uid, ids, context)
        product_ids = []
        for bom in boms:
            product_old_id = bom.product_id.id
            if vals.get('product_id', False) and not product_old_id == vals['product_id']:
                # on new product set that have bom
                self.pool['product.product'].write(cr, uid, vals['product_id'], {'supply_method': 'produce', 'purchase_ok': False}, context)
                bom_ids_count = self.search(cr, uid, [('product_id', '=', product_old_id), ('bom_id', '=', False)], count=True)
                if bom_ids_count == 1:
                    self.pool['product.product'].write(cr, uid, product_old_id, {'supply_method': 'buy', 'purchase_ok': True}, context)
            if ('bom_lines' in vals or 'routing_id' in vals) and ENABLE_CACHE:
                product_ids.append(product_old_id)
                if vals.get('product_id', False):
                    product_ids.append(int(vals['product_id']))
        if product_ids:
            changed_product = self.GetWhereUsed(cr, uid, product_ids, context)[1].keys()
            for product_id in changed_product:
                if int(product_id) in self.pool['product.product'].product_cost_cache:
                    del self.pool['product.product'].product_cost_cache[int(product_id)]

        if 'bom_lines' in vals:
            for bom_line in vals['bom_lines']:
                if bom_line[0] == 2 or isinstance(bom_line[2], dict) and 'product_qty' in bom_line[2]:
                    if product_old_id in self.pool['product.product'].product_cost_cache:
                        del self.pool['product.product'].product_cost_cache[product_old_id]

        return super(mrp_bom, self).write(cr, uid, ids, vals, context=context)

    def action_view_bom(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids, context)[0]

        view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'mrp', 'mrp_bom_tree_view')
        view_id = view and view[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Product BOM'),
            'res_model': 'mrp.bom',
            'view_type': 'tree',
            'view_mode': 'tree',
            'view_id': [view_id],
            'domain': [('product_id', '=', line.product_id.id),
                       ('bom_id', '=', False)],
            # 'target': 'new',
            'res_id': False
        }

    def GetWhereUsed(self, cr, uid, ids, context=None):
        """
            Return a list of all fathers of a Part (all levels)

        """
        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        self._packed = []
        relDatas = []
        if len(ids) < 1:
            return None
        sid = False
        if len(ids) > 1:
            sid = ids[1]
        oid = ids[0]
        relDatas.append(oid)
        relDatas.append(self._implodebom(cr, uid, self._inbomid(cr, uid, oid, sid, context), context))
        prtDatas = self._getpackdatas(cr, uid, relDatas, context)
        return (relDatas, prtDatas, self._getpackreldatas(cr, uid, relDatas, prtDatas, context))

    def _getpackdatas(self, cr, uid, relDatas, context=None):
        prtDatas = {}
        non_decimal = re.compile(r'[^\d.]+')
        tmpbuf = (((str(relDatas).replace('[', '')).replace(']', '')).replace('(', '')).replace(')', '').split(',')
        tmpids = [int(non_decimal.sub('', tmp)) for tmp in tmpbuf if len(non_decimal.sub('', tmp).strip()) > 0]
        if len(tmpids) < 1:
            return prtDatas
        compType = self.pool['product.product']
        tmpDatas = compType.read(cr, uid, tmpids, context)
        for tmpData in tmpDatas:
            for keyData in tmpData.keys():
                if not tmpData[keyData]:
                    del tmpData[keyData]
            prtDatas[str(tmpData['id'])] = tmpData
        return prtDatas

    def _getpackreldatas(self, cr, uid, relDatas, prtDatas, context=None):
        relids = {}
        relationDatas = {}
        non_decimal = re.compile(r'[^\d.]+')
        tmpbuf = (((str(relDatas).replace('[', '')).replace(']', '')).replace('(', '')).replace(')', '').split(',')
        tmpids = [int(non_decimal.sub('', tmp)) for tmp in tmpbuf if len(non_decimal.sub('', tmp).strip()) > 0]
        if len(tmpids) < 1:
            return prtDatas
        for keyData in prtDatas.keys():
            tmpData = prtDatas[keyData]
            if len(tmpData.get('bom_ids', [])) > 0:
                relids[keyData] = tmpData['bom_ids'][0]

        if len(relids) < 1:
            return relationDatas
        setobj = self.pool['mrp.bom']
        for keyData in relids.keys():
            relationDatas[keyData] = setobj.read(cr, uid, relids[keyData], context)
        return relationDatas

    def _implodebom(self, cr, uid, bomObjs, context=None):
        """
            Execute implosion for a a bom object
        """
        pids = []
        for bomObj in bomObjs:
            if not bomObj.product_id:
                continue
            if bomObj.product_id.id in self._packed:
                continue
            self._packed.append(bomObj.product_id.id)
            innerids = self._implodebom(cr, uid, self._inbomid(cr, uid, bomObj.product_id.id, context))
            pids.append((bomObj.product_id.id, innerids))
        return (pids)

    def GetWhereUsedSum(self, cr, uid, ids, context=None):
        """
            Return a list of all fathers of a Part (all levels)
        """
        self._packed = []
        relDatas = []
        if len(ids) < 1:
            return None
        sid = False
        if len(ids) > 1:
            sid = ids[1]
        oid = ids[0]
        relDatas.append(oid)
        relDatas.append(self._implodebom(cr, uid, self._inbomid(cr, uid, oid, sid, context), context))
        prtDatas = self._getpackdatas(cr, uid, relDatas, context)
        return (relDatas, prtDatas, self._getpackreldatas(cr, uid, relDatas, prtDatas))

    def _bomid(self, cr, uid, pid, sid=None, context=None):
        if sid:
            return self._getbomid(cr, uid, pid, sid, context)
        else:
            return self._getbomidnullsrc(cr, uid, pid, context)

    def _inbomid(self, cr, uid, pid, sid=None, context=None):
        if sid:
            return self._getinbom(cr, uid, pid, sid, context)
        else:
            return self._getinbomidnullsrc(cr, uid, pid, context)

    def _getbomid(self, cr, uid, pid, sid, context=None):
        ids = self._getidbom(cr, uid, pid, sid, context)
        return self.browse(cr, uid, list(set(ids)), context)

    def _getidbom(self, cr, uid, pid, sid, context):
        ids = self.search(cr, uid, [('product_id', '=', pid), ('bom_id', '=', False)], context=context)
        return list(set(ids))

    def _getinbom(self, cr, uid, pid, sid, context):
        ids = self.search(cr, uid, [('product_id', '=', pid), ('bom_id', '!=', False)], context=context)
        return self.browse(cr, uid, ids, context)

    def _getinbomidnullsrc(self, cr, uid, pid, context=None):
        counted = []
        ids = self.search(cr, uid, [('product_id', '=', pid), ('bom_id', '!=', False)], context=context)
        for obj in self.browse(cr, uid, ids, context):
            if obj.bom_id in counted:
                continue
            counted.append(obj.bom_id)
        return counted
