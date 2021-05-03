# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com 
############################################################################
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
from openerp.osv import fields, orm

from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp 
from openerp.tools import float_compare, float_round, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import netsvc

class mrp_production_line(orm.Model):
    _inherit = 'mrp.production.product.line' 
    
    def onchange_final_qty(self, cr, uid, ids, final_qty, product_theoric_qty, context=None):
        res = {}
        product_id = None
        production_id = None
        for obj in self.browse(cr, uid, ids, context=context):
            production_id = obj.production_id.id
            product_id = obj.product_id.id
        
        lines =  self.search(cr, uid, [('production_id', '=', production_id)])
        final_qty_sum = 0.0
        for line in lines:
            if line not in ids:
                obj_line = self.browse(cr, uid, [line], context=context)
                final_qty_sum = final_qty_sum + obj_line[0].product_qty
        #assign real qty
        product_qty = final_qty - final_qty_sum        
        adv = ((product_qty - product_theoric_qty)/product_theoric_qty) * 100
        msj = ''
        if abs(adv) > 1:            
            msj = _("The real quantity is shifting the maximum allowed 1 %s, by a percentage %s %s") % ("%", str(round(adv, 2)), "%")
        res = {'value': {
                        'product_qty': product_qty, 
                        'product_qty_ff': product_qty,
                        'msj_theoric_real': _(msj)
                        }
                }
        return res
    
    def _get_qty(self, cr, uid, ids, fields, arg, context):
        x={}
        for record in self.browse(cr, uid, ids):
            x[record.id]= record.product_qty
        return x
        
    _columns = {
        'product_theoric_qty': fields.float('Product Theoric Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'final_qty': fields.float('Final Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'product_qty_ff':fields.function(_get_qty, method=True, type='float', string='Real Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'msj_theoric_real': fields.char(string='Message')
    }
