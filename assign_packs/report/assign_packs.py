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
import datetime
import locale
from openerp.report import report_sxw
from l10n_mx_invoice_amount_to_text import amount_to_text_es_MX

class assign_packs(report_sxw.rml_parse):
    # Metodo inicial
    def __init__(self, cr, uid, name, context):
        super(assign_packs, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_amount': self._get_amount,
            'get_amount_format': self._get_amount_format,
            'convert_to_words': self._convert_to_words,
            'convert_date_to_words': self._convert_date_to_words,
            'get_name_contact': self._get_name_contact,
            'display_own_street_contact': self._display_own_street_contact,
            'display_fiscal_street_contact': self._display_fiscal_street_contact,
            'get_phone_contact': self._get_phone_contact,
            'get_city_state_contact': self._get_city_state_contact,
            'get_city_state_partner': self._get_city_state_partner,
            'get_description_tracking': self._get_description_tracking,
            'get_blocks_in_line': self._get_blocks_in_line,
        })
    def _get_amount(self, tracking_ids, product):
        return (len(tracking_ids) * product.lst_price * 10)
    def _get_amount_format(self, amount):
        locale.setlocale(locale.LC_ALL, 'es_MX.utf-8')
        return locale.currency(amount, grouping=True )
    def _convert_to_words(self, amount, cur):
        return amount_to_text_es_MX.get_amount_to_text(self, amount, 'es_cheque', cur)
    def _convert_date_to_words(self, date):
        locale.setlocale(locale.LC_ALL, 'es_MX.utf-8')
        d = datetime.datetime.strptime(str(date), "%d/%m/%Y").strftime("%A %d de %B de %Y")
        #return '{0:%d} de {0:%B} de {0:%Y} .'.format(d)
        return str(d).upper()
    def _get_name_contact(self, partner):
        name = ''
        if len(partner.child_ids)>0:
            name = partner.child_ids[0].name
        return name
    def _display_own_street_contact(self, partner):
        street = ''
        if len(partner.child_ids)>0:
            street = partner.child_ids[0].street
        return street
    def _display_fiscal_street_contact(self, partner):
        street2 = ''
        if len(partner.child_ids)>0:
            street2 = partner.child_ids[0].street2
        return street2
    def _get_phone_contact(self, partner):
        phone = ''
        if len(partner.child_ids)>0:
            phone = partner.child_ids[0].phone
        return phone
    def _get_description_tracking(self, tracking):
        return tracking.name
    def _get_blocks_in_line(self, trakings):
        line = ''
        
        # Se recorren los paquetes
        for traking in trakings:
            # Se asignan los paquetes en una sola linea
            line += traking.name + ', '
        
        # Se devuelve la linea y se le quita la ultma coma
        return line[:-2]
    def _get_city_state_contact(self, partner):
        city = ''
        if len(partner.child_ids)>0:
            city = partner.child_ids[0].city + ', ' + partner.child_ids[0].state_id.name
        return city
    def _get_city_state_partner(self, partner):
        return partner.city + ', ' + partner.state_id.name
report_sxw.report_sxw('report.assign.packs',
                'assign.packs',
                'assign_packs/report/assign_packs.rml',
                parser=assign_packs)