# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#    Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com
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

from openerp.osv import osv, fields

#se cambia
class product(osv.Model):
    """Inherited product"""
    # The line above is the Python’s way to document
    # your objects (like classes)
    _inherit = 'product.product'
    _columns = {
        # A one2many is the inverse link of a many2one
        'product_related_code_ids' : fields.one2many('product.related.code', 'product_id',
            string='Related Code')
    }

	
class product_related_code(osv.Model):
	_name = "product.related.code"
	# _rec_name redefine the field to get when seeing the record in
	# another object. In this case, the partner’s name will be printed
	_rec_name = 'code'
	# (useful when no field ’name’ has been defined)
	_columns = {
		'code' : fields.char(string="Code", size=256, required=True, help="Related Code of a product"),
		# There is only relational fields
		'product_id': fields.many2one('product.product', string="Product",
		required=True, ondelete='cascade'),
	}
