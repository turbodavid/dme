# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2014 DME Soluciones - http://www.dmesoluciones.com
#    All Rights Reserved.
############################################################################
#    Coded by: Jorge Alfonso Medina Uriarte <jorge.medina@dmesoluciones.com>
############################################################################
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

import time

class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def _get_shipped_purchase_order(self, cr, uid, invoice_id, name, args, context=None):
        res = {}
        # Se recorren cada una de las Facturas
        for invoice in self.browse(cr, uid, invoice_id, context):
            if invoice.type =="in_invoice":
                sql_req = """Select o.shipped, o.* 
                                From purchase_invoice_rel rel
                                Inner Join purchase_order o on rel.purchase_id = o.id
                                Where rel.invoice_id = %d;""" % (invoice.id,)
                cr.execute(sql_req)
                sql_res = cr.fetchall()

                if sql_res: # Se encontraron registros
                    # Se recorren todas las etiquetas encontradas y se concatenan.
                    for row in sql_res:
                        res[invoice.id] = row[0]
                else:
                    res[invoice.id] = False

                # Actualiza el campo si es diferente a lo encontrado.
                #if(invoice.delivered_purchase != stretiqueta):
                if not invoice.delivered_purchase_group:
                    self.write(cr, uid, [invoice.id], {'delivered_purchase_group': res[invoice.id]}, context)
            else:
                res[invoice.id] = False
        return res
        
    _columns = {
        'delivered_purchase':fields.function(_get_shipped_purchase_order,
            type='boolean',
            method=True,
            string='Shipped'
            ),
        'delivered_purchase_group' : fields.boolean('Shipped', size=1000, required=True),
    }
