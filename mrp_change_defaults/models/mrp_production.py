# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: César Alfredo Sánchez Beltrán            cesar_sb@hotmail.com
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
from openerp.osv import fields, osv, orm

from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp 
#from openerp.tools import float_compare, float_round, DEFAULT_SERVER_DATETIME_FORMAT
#from openerp import netsvc

class mrp_production(osv.osv):
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

    _defaults = {
        'location_src_id': False,
        'location_dest_id': False
    }
