# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    26-APR-2012 (GK) created
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
from osv import fields,osv
from tools.translate import _
import logging

class one2many_sorted(fields.one2many):
    
    _logger = logging.getLogger(__name__)
    
    def parse_order(self, order):
        result = []
        for col in order.split(',') :
            c = col.strip()
            if ' ASC' in c.upper() :
                result.append((c[0:c.index(' ')], False))
            elif ' DESC' in c.upper() :
                result.append((c[0:c.index(' ')], True))
            else :
                result.append((c, False))
        return list(reversed(result))
    # end def parse_order
    
    def __init__(self, obj, fields_id, string='unknown', limit=None, **args) :
        self._order  = []
        self._search = []
        self._set    = {}
        if 'order' in args :
            self._order = self.parse_order(args['order'])
        if 'search' in args :
            self._search = args['search']
        if 'set' in args :
            self._set = args['set']
        (fields.one2many).__init__(self, obj, fields_id, string=string, limit=limit, **args)
    # end def __init__
    
    def property_value(self, cr, user, obj, name):
        property_obj = obj.pool.get('ir.property')
        prop_id = property_obj.search \
            ( cr, user
            , [ ('name', '=', name)
              , ('type', '=', 'text')
              , ('company_id','=', obj.pool.get('res.company')._company_default_get(cr, user))
              ]
            )
        if prop_id :
            return property_obj.browse(cr, user, prop_id[0]).value_text
        return False 
    # end def property_value

    def selected (self, cr, user, obj, ids, context=None) :
        _obj = obj.pool.get(self._obj)
        return _obj.search \
            ( cr, user
            , [(self._fields_id, 'in', ids)] + self._search
            , limit = self._limit
            , context=context
            )
    # end def selected

    def get (self, cr, obj, ids, name, user=None, offset=0, context=None, values={}) :
        _obj = obj.pool.get(self._obj)
        if context and 'one2many_sorted_order' in context :
            prop = self.property_value(cr, user, obj, context['one2many_sorted_order'])
            if prop :
                order = self.parse_order(prop)
        else:
            prop = self.property_value(cr, user, obj, "%s.%s.order" % (self._obj, self._fields_id))
            if prop :
                order = self.parse_order(prop)
            else :
                order = self._order
        ids2 = self.selected(cr, user, obj, ids, context=context)
        sortable = []
        for r in _obj.browse(cr, user, ids2, context=context) :
            d = {}
            for key in ([('id', False)] + order) :
                o = r
                for m in key[0].split('.'):
                    if "()" in m :
                        o = getattr(o, m.strip("()"))()
                    else :
                        o = getattr(o, m)
                d[key[0]] = o if not isinstance(o, str) else _(o)
            sortable.append(d)
        for key in order :
            sortable.sort(key=lambda d: d[key[0]], reverse=key[1])
        res = {}
        for id in ids : res[id] = []
        for r in _obj.browse(cr, user, [d['id'] for d in sortable], context=context) :
            res[getattr(r, self._fields_id).id].append(r.id)
        return res
    # end def get

    def set(self, cr, obj, id, field, values, user=None, context=None):
        for act in values :
            if act[0] == 0 : # "create"
                for k, v in self._set.iteritems() :
                    act[2][k] = v
        return (fields.one2many).set(self, cr, obj, id, field, values, user, context)
    # end def set
# end class one2many_sorted

class many2many_sorted(fields.many2many):
    
    _logger = logging.getLogger(__name__)
    
    def parse_order(self, order):
        result = []
        for col in order.split(',') :
            c = col.strip()
            if ' ASC' in c.upper() :
                result.append((c[0:c.index(' ')], False))
            elif ' DESC' in c.upper() :
                result.append((c[0:c.index(' ')], True))
            else :
                result.append((c, False))
        return list(reversed(result))
    # end def parse_order
    
    def __init__(self, obj, rel=None, id1=None, id2=None, string='unknown', limit=None, **args) :
        self._order  = []
        self._set    = {}
        if 'order' in args :
            self._order = self.parse_order(args['order'])
        if 'set' in args :
            self._set = args['set']
        (fields.many2many).__init__(self, obj, rel, id1=id1, id2=id2, string=string, limit=limit, **args)
    # end def __init__
    
    def property_value(self, cr, user, obj, name):
        property_obj = obj.pool.get('ir.property')
        prop_id = property_obj.search \
            ( cr, user
            , [ ('name', '=', name)
              , ('type', '=', 'text')
              , ('company_id','=', obj.pool.get('res.company')._company_default_get(cr, user))
              ]
            )
        if prop_id :
            return property_obj.browse(cr, user, prop_id[0]).value_text
        return False 
    # end def property_value

    def get (self, cr, obj, ids, name, user=None, offset=0, context=None, values={}) :
        _obj = obj.pool.get(self._obj)
        if context and 'many2many_sorted_order' in context :
            prop = self.property_value(cr, user, obj, context['many2many_sorted_order'])
            if prop :
                order = self.parse_order(prop)
        else:
            prop = self.property_value(cr, user, obj, "%s.%s.%s.%s.order" % (self._obj, self._rel, self._id1, self._id2))
            if prop :
                order = self.parse_order(prop)
            else :
                order = self._order
        res = {}
        for id in ids : res[id] = []
        got = (fields.many2many).get(self, cr, obj, ids, name, user=user, offset=offset, context=context, values=values)
        for k, ids2 in got.iteritems() :
            sortable = []
            for r in _obj.browse(cr, user, ids2, context=context) :
                d = {}
                for key in ([('id', False)] + order) :
                    o = r
                    for m in key[0].split('.'):
                        if "()" in m :
                            o = getattr(o, m.strip("()"))()
                        else :
                            o = getattr(o, m)
                    d[key[0]] = o if not isinstance(o, str) else _(o)
                sortable.append(d)
            for key in order :
                sortable.sort(key=lambda d: d[key[0]], reverse=key[1])
            self._logger.debug("many2many order criteria: %s", order) ######
            for d in sortable : self._logger.debug("sorted %s", d) #############
            for r in _obj.browse(cr, user, [d['id'] for d in sortable], context=context) :
                res[k].append(r.id)
        return res
    # end def get

    def set(self, cr, model, id, name, values, user=None, context=None):
        for act in values :
            if act[0] == 0 : # "create"
                for k, v in self._set.iteritems() :
                    act[2][k] = v
        return (fields.many2many).set(self, cr, model, id, name, values, user, context)
    # end def set
# end class many2many_sorted

