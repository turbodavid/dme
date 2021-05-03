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

    def _check_tax_invoice_line(self, cr, uid, ids, context=None):
        resultado = False
        for invoice in self.browse(cr, uid, ids, context):
            #if dont have lines, can pass
            if len(invoice.invoice_line) == 0:
                resultado = True
            else: #else, check each line if have tax
                for line in invoice.invoice_line:
                    if len(line.invoice_line_tax_id)>0:
                        resultado = True
                    else:
                        resultado = False
                        break
        return resultado
            
    _constraints = [(_check_tax_invoice_line,"The invoice cannot be without taxes in lines!",['invoice_line']),]
