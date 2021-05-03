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

class mrp_production(orm.Model):
    _inherit = 'mrp.production' 
    
    def bom_id_change(self, cr, uid, ids, bom_id, context=None):
        """ Finds routing for changed BoM.
        @param product: Id of product.
        @return: Dictionary of values.
        """
        res = super(mrp_production, self).bom_id_change(cr, uid, ids, bom_id, context=context)
        bom_point = self.pool.get('mrp.bom').browse(cr, uid, bom_id, context=context)
        res['value'].update({'location_src_id':bom_point.location_src_id.id})
        res['value'].update({'location_dest_id':bom_point.location_dest_id.id})
        return res

    def _action_compute_lines(self, cr, uid, ids, properties=None, context=None):
        """ Compute product_lines and workcenter_lines from BoM structure
        @return: product_lines
        """
        res = super(mrp_production, self)._action_compute_lines(cr, uid, ids, properties, context=context)    
        prod_line_obj = self.pool.get('mrp.production.product.line')        
        for r in res:
            product_line_id = prod_line_obj.search(cr, uid, [('production_id', '=', r["production_id"]), ('product_id', '=', r["product_id"])])
            update = {'product_theoric_qty': r["product_qty"], 'product_qty' : 0.0 }
            prod_line_obj.write(cr, uid, product_line_id, update)
            r.update(update)
        return res
        
    def save_production_lines(self, cr, uid, ids, product_lines, context=None):
        prod_line_obj = self.pool.get('mrp.production.product.line')
        for line in product_lines:
            if line[2]: #values
                prod_line_obj.write(cr, uid, [line[1]], line[2])
        return True

    def write(self, cr, uid, ids, values, context = None):
        #object production
        mrp_production_obj = self.pool.get('mrp.production').browse(cr, uid, ids, context=context)
        #if draft
        if mrp_production_obj[0].state == 'draft':
            #get lines
            prod_line_obj = self.pool.get('mrp.production.product.line')
            #we search all lines by production_id
            lines = prod_line_obj.search(cr, uid, [('production_id', '=', mrp_production_obj[0].id)])
            #qty
            product_qty = 0.0
            #get obj in lines            
            for line in lines:
                #get line
                obj_line = prod_line_obj.browse(cr, uid, [line], context=context)
                #sum product_qty for each line
                product_qty = product_qty + obj_line[0].product_qty
            density = 0.0
            if 'density' in values:
                density = values["density"]
            else:
                density = mrp_production_obj[0].density            
            #product_qty = 0 in lines
            if product_qty == 0:
                if 'product_qty' in values:
                    product_qty = values["product_qty"]
                else:
                    product_qty = mrp_production_obj[0].product_qty
            #update values
            values.update({'product_qty': product_qty, 'product_uos_qty': product_qty / density })
        
        #save super
        res = super(mrp_production, self).write(cr, uid, ids, values, context = context)
        return res

    def _get_standard_price(self, cr, uid, ids, fields, arg, context):
        res={}
        account_move_line_obj = self.pool.get('account.move.line')
        for record in self.browse(cr, uid, ids):
            #we search in policy 
            lines =  account_move_line_obj.search(cr, uid, [('name', '=', record.name), ('product_id', '=', record.product_id.id), ('credit', '>',0)])
            if len(lines)>0:
                for l in lines:
                    obj_line = account_move_line_obj.browse(cr, uid, l, context=context)
                    if record.product_qty > 0:
                        res[record.id]= obj_line.credit/record.product_qty
                    else:
                        res[record.id]= 0.0
            else:
                res[record.id]= 0.0
        return res
        
    _columns = {
        'standard_price': fields.function(_get_standard_price, method=True, type='float', string='Standard Price (Unit)', digits_compute=dp.get_precision('Account')),
    }

    _defaults = {
        'location_src_id': False,
        'location_dest_id': False
    }
