# -*- coding: utf-8 -*-
##############################################################################
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
############################################################################
#   Coded By:
#       Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com
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
from openerp.osv import orm
from openerp.osv import fields
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class account_invoice(orm.Model):
    _inherit = 'account.invoice'
    
    def invoice_cancel(self, cr, uid, ids, context=None):
	if context is None:
		context = {}
	
        invoice_id = 0
        if len(ids) > 0:
            invoice_id = ids[0]

        sql_req= """Select distinct rel.order_line_id
                    From account_invoice ai
                    Inner Join account_invoice_line ail on ai.id = ail.invoice_id
                    Inner Join purchase_order_line_invoice_rel rel on ail.id = rel.invoice_id
                    Where ai.id = %d;""" % (invoice_id)
        cr.execute(sql_req)
        order_lines = cr.fetchall()
        order_line_ids_release = []

        #For lines of Invoice
        for order_line in order_lines:
            order_line_ids_release.append(order_line[0])

        #object
        purchase_line_obj = self.pool.get('purchase.order.line')
	res = super(account_invoice, self).invoice_cancel(cr, uid, ids, context=context)

        #Update lines
	purchase_line_obj.write(cr, uid, order_line_ids_release, {'invoiced' : False})
        return res
