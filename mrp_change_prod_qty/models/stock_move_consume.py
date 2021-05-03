# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class stock_move_consume(osv.osv_memory):
    _inherit = "stock.move.consume"
     
    def onchange_location_id(self, cr, uid, ids, product_id, location_id, context=None):
        res = {}
        stock_real = 0.0
        if location_id:
            if context is None:
                context = {}
            c = context.copy()
            c.update({'product_id' : product_id})
            stock_location = self.pool.get('stock.location').browse(cr, uid, location_id, context=c)        
            stock_real = stock_location.stock_real
        res = {'value': {'qty_available': stock_real}}
        return res
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(stock_move_consume, self).default_get(cr, uid, fields, context=context)
        move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
        c = context.copy()        
        c.update({'product_id' : move.product_id.id})
        stock_location = self.pool.get('stock.location').browse(cr, uid, move.location_id.id, context=c)
        res.update({'qty_available': stock_location.stock_real, 'product_qty_ff': move.product_qty})
        return res

    def _get_qty(self, cr, uid, ids, fields, arg, context):
        x={}
        for record in self.browse(cr, uid, ids):
            x[record.id]= record.product_qty
        return x

    _columns = {        
        'qty_available': fields.float('Quantity Available', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'product_qty_ff':fields.function(_get_qty, method=True, type='float', string='Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
