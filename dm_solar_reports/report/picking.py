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
from openerp.tools.translate import _
from l10n_mx_invoice_amount_to_text import amount_to_text_es_MX

class picking(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_product_desc': self.get_product_desc,
            'SI_NO' : self.SI_NO,
            'type_service' : self.type_service,
            'convert_to_words': self.convert_to_words,
            'amount_total_picking' : self.amount_total_picking
        })

    def type_service(self, value):
        #Instancia tu objeto
        obj_sale_order = self.pool.get('sale.order')
        type_service_values = obj_sale_order.fields_get(self.cr, self.uid, 'type_service').get('type_service').get('selection')
        type_service_values_dict = dict(type_service_values)
        return _(type_service_values_dict[value])

    def get_product_desc(self, move_line):
        desc = move_line.product_id.name
        if move_line.product_id.default_code:
            desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
        return desc

    def SI_NO(self, value):
        if (value == True):
            return "SI"
        else:
            return "NO"   

    def amount_total_picking(self,obj):
        cur_obj = self.pool.get('res.currency')
        total = 0    
        res = 0   
        for line in obj.order_line:
            if (line.product_id.type == 'service'):
                continue
            else:
                #tax = line.tax_id[0].amount*line.price_subtotal
                #total= total + line.price_subtotal + tax
                #cur = line.order_id.pricelist_id.currency_id
                #res = res + cur_obj.round( self.cr ,self.uid, cur, total)
                res= res + line.price_subtotal

        return res

    def convert_to_words(self, amount, cur):
        return amount_to_text_es_MX.get_amount_to_text(self, amount, 'es_cheque', cur)

from netsvc import Service
del Service._services['report.stock.picking.list']# + suffix]
del Service._services['report.stock.picking.list.in']# + suffix]
del Service._services['report.stock.picking.list.out']# + suffix]
for suffix in ['', '.in', '.out']:
    report_sxw.report_sxw('report.stock.picking.list' + suffix,
                          'stock.picking' + suffix,
                          'dm_solar_reports/report/picking.rml',
                          parser=picking)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
