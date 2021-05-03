# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2016 DME Soluciones - http://www.dmesoluciones.com
#    All Rights Reserved.
############################################################################
#    Coded by: Jorge Alfonso Medina Uriarte(jorge.medina@dmesoluciones.com)
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
from openerp.addons.account.report import account_print_invoice
from openerp.report import report_sxw
from openerp.tools.translate import _
#from l10n_mx_invoice_amount_to_text import amount_to_text_es_MX
from num2words import num2words

import logging
_logger = logging.getLogger(__name__)

class invoice(account_print_invoice.account_invoice):
    def __init__(self, cr, uid, name, context):
        res = super(invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'date_to_text': self._get_date_to_text,
            'amount_total': self._get_amount_total,
            'convert_to_words': self._convert_to_words
        })

    def _get_date_to_text(self, date):
        MES=["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        dates = str(date).split('/')
        if len(dates) > 1:
            m = int(dates[1])
            return dates[0] + " de " + str(MES[m-1]) + " de " + dates[2]
        else:
            dates = str(date).split('-')
            m = int(dates[1])
            return dates[2] + " de " + str(MES[m-1]) + " de " + dates[0]
    
    def _get_amount_total(self, amount_total):
        amount_total = amount_total + amount_total * .10;
        return amount_total
 
    def _convert_to_words(self, invoice):
        return num2words(invoice.amount_total, lang='es').upper() + ' ' + invoice.currency_id.name
        #return amount_to_text_es_MX.get_amount_to_text(self, self._get_amount_total(invoice.amount_total), 'es_cheque', invoice.currency_id.name)
        
#from netsvc import Service
#del Service._services['report.invoice.promissory.note']
#del Service._services['report.invoice.promissory.note.webkit']
# Inicia con report.[nombre del reporte] ej.report.invoice.promissory.note.webkit
report_sxw.report_sxw(
    'report.invoice.promissory.note.webkit',
    'account.invoice',
    'reports_sacsa/report/promissory_note.mako',
    parser=invoice,
)
