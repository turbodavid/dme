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

class mrp_production(orm.Model):
    _inherit = 'mrp.production'

    #def product_id_change(self, cr, uid, ids, product_id, context=None):
        #""" Changes UoM and name if product_id changes.
        #@param product_id: Changed product_id
        #@return:  Dictionary of changed values
        #"""
        #res = {}
        #if product_id:
            #res = super(mrp_production, self).product_id_change(cr, uid, ids, product_id, context=context)
            #print res
            #prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            #if prod.uos_coeff:
                #res['value'].update({
                    #'product_qty': 1, 
                    #'product_uos_qty': prod.uos_coeff, 
                    #'product_uos': prod.uos_id.id,
                    #'density': prod.density
                #})
        #return res
        
    def bom_id_change(self, cr, uid, ids, bom_id, context=None):
        """ Finds routing for changed BoM.
        @param product: Id of product.
        @return: Dictionary of values.
        """
        res = super(mrp_production, self).bom_id_change(cr, uid, ids, bom_id, context=context)
        bom_point = self.pool.get('mrp.bom').browse(cr, uid, bom_id, context=context)        
        res['value'].update({'density':bom_point.density})
        return res
    
    def onchange_product_qty_density(self, cr, uid, ids, product_id, product_qty, density, context=None):
        res = {'value':{
                'product_uos_qty': product_qty * density
            }
        }
        return res

    _columns = {
        'density': fields.float('Density', digits_compute = dp.get_precision('Account'), help=_('Apparent Density (Convertion Factor)')),
    }
