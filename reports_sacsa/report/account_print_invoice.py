# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 OpenPyme - http://www.openpyme.mx
#    All Rights Reserved.
#    info OpenPyme (info@openpyme.mx)
#    Coded by: Agustín Cruz (agustin.cruz@openpyme.mx)
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
import time

from openerp.tools.translate import _
from openerp.report import report_sxw
from openerp.addons.report_webkit import webkit_report
import openerp
import qrcode

logger = logging.getLogger(__name__)


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.context = context

        self.localcontext.update({
            'get_taxes': self._get_taxes,
            'get_taxes_ret': self._get_taxes_ret,
            'get_emitter_data': self._get_emitter_data,
            'get_partner_data': self._get_partner_data,
            'qrcode': self._get_qrcode,
            'get_text_promissory': self._get_text_promissory,
            'legend': self._get_legend,
            'get_date_invoice': self._get_date_invoice,
            'get_ref_BNMX': self._get_ref_BNMX,
            'get_transfer_ref': self._get_transfer_ref,
        })

    def _get_text_promissory(self, company, partner):
        text = ''
        context = {}
        lang = self.pool.get('res.partner').browse(
            self.cr, self.uid,
            partner.id
        ).lang
        if lang:
            context.update({'lang': lang})
        company = self.pool.get('res.company').browse(
            self.cr, self.uid,
            company.id, context=context
        )
        if company.dinamic_text:
            try:
                text = company.dinamic_text % eval("{" + company.dict_var + "}")
            except:
                pass
        return text

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
        if partner.parent_id:
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

    def _get_taxes(self, invoice):
        # TODO: Optimizar esta funcion y combinarla con _get_taxes_ret
        lista = []
        lista2 = []

        taxes = [tax for tax in invoice.tax_line if tax.tax_percent >= 0.0]

        # comparacion de los taxes, para que todos sean distintos entre sí
        for tax in taxes:
            lista.append([tax.name2, tax.amount])

        for i in range(0, len(lista)):
            for j in range(i + 1, len(lista)):
                if (lista[i][0] == lista[j][0])and (lista[j][0] != 0):
                    lista[j][0] = 0
                    lista[i][1] = lista[i][1] + lista[j][1]

        for k in range(0, len(lista)):
            if lista[k][0] != 0:
                lista2.append(lista[k])
        
        if len(lista2)==0: #JAMU
            lista2.append(['IVA',0.0])
            
        return lista2

    def _get_taxes_ret(self, invoice):
        lista = []
        lista2 = []

        taxes = [tax for tax in invoice.tax_line if tax.tax_percent < 0.0]

        # comparacion de los taxes, para que todos sean distintos entre sí
        for tax in taxes:
            lista.append([tax.name2, tax.amount])

        for i in range(0, len(lista)):
            for j in range(i + 1, len(lista)):
                if (lista[i][0] == lista[j][0])and (lista[j][0] != 0):
                    lista[j][0] = 0
                    lista[i][1] = lista[i][1] + lista[j][1]

        for k in range(0, len(lista)):
            if lista[k][0] != 0:
                lista2.append(lista[k])

        if len(lista2)==0: #JAMU
            lista2.append(['RET',0.0])

        return lista2

    def _get_legend(self, invoice):
        """ Helper funcion to print legend according
            to invoice type.
        """
        legend = _('This document is a printed representation od the CFDI')
        if invoice.journal_id.name.split('-')[1] =="NOTA DE CARGO":
            legend = _("Nota Cargo")
        else:
            if invoice.type == 'out_invoice':
                legend = _("Factura")
            else:
                legend = _("Nota Crédito")
        return legend + ' ' + invoice.internal_number
        
    def _get_date_invoice(self, invoice):
        dt = ''
        try:
            dt = datetime.strptime(invoice.invoice_datetime, '%Y-%m-%d %H:%M:%S').strftime('%Y/%m/%d')
        except ValueError:
            dt = "Oops! " + ValueError
        return dt

    def _get_Letter_Value_MOD97(self, letter):
        nValor = 0
        if letter in ('A','B','C'):
            nValor = 2
        elif letter in ('D','E','F'):
            nValor = 3
        elif letter in ('G','H','I'):
            nValor = 4
        elif letter in ('J','K','L'):
            nValor = 5
        elif letter in ('M','N','O'):
            nValor = 6
        elif letter in ('P','Q','R'):
            nValor = 7
        elif letter in ('S','T','U'):
            nValor = 8
        elif letter in ('V','W','X'):
            nValor = 9
        elif letter in ('Y','Z'):
            nValor = 0

        return nValor

    def _get_ref_Banorte(self, mod_empresa, partner_id):
        ref = ''
        cero = '0'
        #sCliente = sCliente.upper()
        sCliente = cero * (20 - len(str(partner_id))) + str(partner_id)
        sEmpresa = cero * (5 - len(str(mod_empresa))) + str(mod_empresa)
        sCadena = sEmpresa + sCliente

        iCount = 1
        nSuma = 0
        nValue = 0
        cValue = ''
        sChar = ''
        while (iCount <=25):
            nValue = 0
            sChar = sCadena[iCount-1]
            sChar = sChar.upper()
            if ord(sChar) >=48 and ord(sChar) <=57:
                nValue = int(sChar)
            if ord(sChar) >=65 and ord(sChar) <=90:
                nValue = _get_Letter_Value_MOD97(sChar)
            
            if iCount % 2==0:
                nValPos = 1
            else:
                nValPos = 2
            
            nValue = nValue * nValPos
            cValue = str(nValue)
            if len(cValue)>1:
                nSuma = nSuma + int(cValue[:1]) + int(cValue[-1])
            else:
                nSuma = nSuma + nValue

            iCount = iCount + 1
            
        nSuma = nSuma % 10
        nSuma = 10 - nSuma
        if nSuma > 9:
            nSuma = 0
        sCadena = sCadena + str(nSuma)
        ref = str(int(sCadena[-21:]))
        return ref

    def _get_ref_BNMX(self, mod_suc, mod_cta, partner_id):
        ref = ''
        cero = '0'
        sCliente = cero * (18 - len(str(partner_id))) + str(partner_id)
        sSucursal = cero * (4 - len(str(mod_suc))) + str(mod_suc)
        sCta = cero * (7 - len(str(mod_cta))) + str(mod_cta)
        sCadenaTmp = sSucursal + sCta + sCliente

        sCadena = []
        for c in sCadenaTmp: sCadena.append(c)
        iCount = 1
        nSuma = 0
        nValue = 0
        sChar = ''
        while (iCount <=29):
            nValue = 0
            sChar = sCadena[iCount-1]
            sChar = sChar.upper()
            
            if ord(sChar) >=48 and ord(sChar) <=57:
                nValue = int(sChar)
            if ord(sChar) >=65 and ord(sChar) <=90:
                nValue = _get_Letter_Value_MOD97(sChar)
            
            context = {}
            mod97_obj = self.pool.get('mod97')
            mod97_id = mod97_obj.search(self.cr, self.uid, [('name','=','MOD97_POS' + str(iCount))])
            mod97 = mod97_obj.browse (self.cr, self.uid, mod97_id, context)
            nValPos = int(mod97[0].value)
            
            nSuma = nSuma + (nValue * nValPos)
            
            iCount = iCount + 1
            
        nSuma = nSuma % 97
        nSuma = 99 - nSuma
        ref = mod_suc + mod_cta + str(partner_id) + cero * (2 - len(str(nSuma))) + str(nSuma)
        return ref

    def _get_qrcode(self, invoice):
        """Genera el código de barras bidimensional para una factura
            @param invoice: Objeto invoice con los datos de la factura

            @return: Imagen del código de barras o None
        """
        # Procesar invoice para obtener el total con 17 posiciones
        tt = string.zfill('%.6f' % invoice.amount_total, 17)

        # Init qr code
        qr = qrcode.QRCode(version=4, box_size=4, border=1)
        # Add the data to qr code
        qr.add_data('?re=' + invoice.company_id.partner_id.vat_split or invoice.company_id.partner_id.vat)
        qr.add_data('&rr=' + invoice.partner_id.vat_split or invoice.company_id.vat)
        qr.add_data('&tt=' + tt)
        qr.add_data('&id=' + invoice.cfdi_folio_fiscal)
        qr.make(fit=True)

        # Genera la imagen y la pone en memoria para poder
        # codificarla en 64bits y mandarla al reporte
        img = qr.make_image()
        output = StringIO.StringIO()
        img.save(output, 'PNG')
        output_s = output.getvalue()
        
        return base64.b64encode(output_s)

    def _get_transfer_ref(self, name, mod_suc, mod_cta, partner_id, mod_empresa):
        ref = name
        if name == 'Banamex':
            ref = self._get_ref_BNMX(mod_suc, mod_cta, partner_id)
        elif name == 'Banorte':
            ref = self._get_ref_Banorte(mod_empresa, partner_id)
        else:
            ref = 'No definido'
        return ref

        
