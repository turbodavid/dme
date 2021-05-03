# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2014 DME Soluciones - http://www.dmesoluciones.com
#    All Rights Reserved.
############################################################################
#    Coded by: Jesus Meza(jesus.meza@dmesoluciones.com)
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

import time
from openerp.report import report_sxw
##from openerp.tools import amount_to_text
##from openerp.tools import amount_to_text_en
from l10n_mx_invoice_amount_to_text import amount_to_text_es_MX

class picking_tec(report_sxw.rml_parse):
    #_inherit = 'stock.picking'
    def __init__(self, cr, uid, name, context):
        super(picking_tec, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_product_desc': self.get_product_desc,
            'get_total_tickets': self.get_total_tickets,
            'convert_to_words': self.convert_to_words,
        })
    def get_product_desc(self, move_line):
        desc = move_line.product_id.name
        if move_line.product_id.default_code:
            desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
        return desc
    def get_total_tickets(self, move_lines):
        return len(move_lines)
    def convert_to_words(self, amount, cur):
        return amount_to_text_es_MX.get_amount_to_text(self, amount, 'es_cheque', cur)
# Se registra el nuevo servicio de reporte
#for suffix in ['', '.in', '.out']:
# Se elimina el reporte anterior report.stock.picking.list
from netsvc import Service
del Service._services['report.stock.picking.list']# + suffix]
report_sxw.report_sxw('report.stock.picking.list',# + suffix,
                      'stock.picking.out', #+ suffix,
                      'picking_tec/report/picking_tecnologico.rml',
                      parser=picking_tec)