# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 OpenERP s.a. (<http://openerp.com>).
#
#	 Coded By:
#       Jorge Alfonso Medina Uriarte <jorge.medina@dmsoluciones.com>
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
from openerp.osv import osv, fields
from openerp.tools.translate import _

class collection_type(osv.Model):
    _name= "collection.type"

    def _check_options(self, cr, uid, ids, context=None):
        for collection_type in self.browse(cr, uid, ids, context):
            if (collection_type.supplier_data==True and collection_type.pack_data == True):
                return False
        return True

    _constraints = [(_check_options,"You can't check both options!",['supplier_data','pack_data'])]
    _columns = {
        'name': fields.char(string="Name", size=256, required=True),
        'supplier_data':  fields.boolean("Supplier data"),
        'pack_data':  fields.boolean("Pack data")
    }

