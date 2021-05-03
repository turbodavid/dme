# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
############################################################################
#    Coded by: Jorge Alfonso Medina Uriarte(jorge.medina@dmesoluciones.com)
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

from openerp.osv import fields, osv

class product_product(osv.osv):
    _inherit = 'product.product'

    def _check_supplier_select(self, cr, uid, ids, context=None):
        product_obj = self.browse(cr, uid, ids, context=context)
        for data in product_obj:
            if data.seller_ids:
                return True
            else:
                return False
        
    _constraints = [(_check_supplier_select, 
                    'You must select a supplier.', ['seller_ids'])]

product_product()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
