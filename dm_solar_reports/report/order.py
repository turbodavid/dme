# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Coded by:
#       Cindy Yukie ley Garcia (cindy.ley@dmesoluciones.com)
#       Jorge Alfonso Medina Uriarte (cindy.ley@dmesoluciones.com)
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

import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler
from l10n_mx_invoice_amount_to_text import amount_to_text_es_MX

class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert_to_words': self.convert_to_words,
            'get_contact_supplier': self.get_contact_supplier,
            'get_type_picking': self.get_type_picking,
        })

    def convert_to_words(self, amount, lang, cur):
        if lang==False:
            lang = "en_US"
        return amount_to_text_es_MX.get_amount_to_text(self, amount, lang, cur)

    def get_contact_supplier(self, supplier_id):
        contact =''
        for child in supplier_id.child_ids:
            contact = child.name
            break
        return contact

    def get_type_picking(self, value):
        return value.name

from netsvc import Service
del Service._services['report.purchase.order']

report_sxw.report_sxw('report.purchase.order','purchase.order','dm_solar_reports/report/order.rml',parser=order)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
