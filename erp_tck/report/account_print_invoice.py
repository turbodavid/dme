# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Dme Soluciones - http://dmsoluciones.com
#    All Rights Reserved.
#
#    Coded by: Jorge Alfonso Medina Uriarte (jorge.medina@dmsoluciones.com)
#       Based : Agustín Cruz (agustin.cruz@openpyme.mx)
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

import string
import logging
import base64
import StringIO

from openerp.tools.translate import _
#from l10n_mx_facturae.report import account_print_invoice
from openerp.addons.account.report import account_print_invoice

from openerp.report import report_sxw
import openerp
import qrcode

logger = logging.getLogger(__name__)

class PrintInvoice(account_print_invoice.account_invoice):
    def __init__(self, cr, uid, name, context):
        super(PrintInvoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'legend': self._get_legend1,
            'get_emitter_data': self._get_emitter_data,
        })

    def _get_legend1(self, invoice):
        """ Helper funcion to print legend according
            to invoice type.
        """
        legend = _('This document is a printed representation of the CFDI')
        return legend

    def _get_emitter_data(self, partner, data='name'):
        # Simple cache for speed up
        if not hasattr(self, 'emitter_data'):
            self.emitter_data = self._get_invoice_address(partner)
        return self.emitter_data[data]

    def _get_partner_data(self, partner, data='name'):
        # Simple cache for speed up
        if not hasattr(self, 'partner_data'):
            self.partner_data = self._get_invoice_address(partner)
        return self.partner_data[data]

    def _get_invoice_address(self, partner):
        # Si la dirección del partner no es default o invoice
        if partner.type not in ['invoice', 'default']:
            # Obtiene la dirección del padre
            add_invoice = partner.parent_id
        else:
            add_invoice = partner

        # Aseguramos que la dirección sea de facturación
        if add_invoice.type in ['invoice', 'default']:
            res = {
                'name': add_invoice.name or '',
                'vat': add_invoice.vat_split or add_invoice.vat or '',
                'street': add_invoice.street or False,
                'no_ext': add_invoice.l10n_mx_street3 or '',
                'no_int': add_invoice.l10n_mx_street4 or '',
                'suburb': add_invoice.street2 or '',
                'city': add_invoice.city or '',
                'state': add_invoice.state_id.name or '',
                'country': add_invoice.country_id.name or '',
                'county': add_invoice.l10n_mx_city2 or '',
                'zip': add_invoice.zip or '',
                'phone': add_invoice.phone or '',
                'fax': add_invoice.fax or '',
                'mobile': add_invoice.mobile or '',
            }
            if not res['vat']:
                # Comprobamos que tengamos un RFC definido
                raise openerp.exceptions.Warning(
                    _('Not Vat Number set on partner'))
        else:
            raise openerp.exceptions.Warning(
                _('Customer Address Not Invoice Type'))
        return res
    
#Delete report
from netsvc import Service
del Service._services['report.account.invoice.facturae.webkit']

#create new report
report_sxw.report_sxw('report.account.invoice.facturae.webkit', 'account.invoice', 'erp_tck/report/account_print_invoice.mako', parser=PrintInvoice)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
