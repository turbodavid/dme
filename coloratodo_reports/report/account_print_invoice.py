# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 OpenERP s.a. (<http://openerp.com>).
#
#	 Coded By:
#       Jesus Antonio Meza Espinoza <jesus.meza@dmsoluciones.com>
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

from datetime import datetime
from openerp.tools.translate import _
from openerp.addons.account.report import account_print_invoice
from openerp.report import report_sxw
import openerp
import qrcode
#from l10n_mx_invoice_amount_to_text import amount_to_text_es_MX

_logger = logging.getLogger(__name__)

class PrintInvoice(account_print_invoice.account_invoice):
	def __init__(self, cr, uid, name, context):
		res = super(PrintInvoice, self).__init__(cr, uid, name, context = context)        
		self.localcontext.update({
			'time': time,
			'get_taxes': self._get_taxes,
			'get_taxes_ret': self._get_taxes_ret,
			'get_text_promissory': self._get_text_promissory,
			'get_emitter_data': self._get_emitter_data,
			'get_partner_data': self._get_partner_data,
			'qrcode': self._get_qrcode,
			'legend': self._get_legend,
			'get_date_invoice': self._get_date_invoice,
		})
	#def _get_discount(self, invoice_line, type):
		#total = 0.0
		#for x in invoice_line:
		#	if type == "discount":
		#		total =  total + ((x.price_unit * x.quantity) * (x.discount/100))
		#	else:
		#		total = total + (x.price_unit * x.quantity)
		#return total
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

		return lista2

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
		#Se saca la direccion que tenga en facturacion
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

	def _get_legend(self, invoice):
		""" Helper funcion to print legend according
			to invoice type.
		"""
		legend = _('This document is a printed representation od the CFDI')
		return legend

	def _get_date_invoice(self, invoice):
		dt = ''
		try:
			dt = datetime.strptime(invoice.invoice_datetime, '%Y-%m-%d %H:%M:%S').strftime('%Y/%m/%d')
		except ValueError:
			dt = "Oops! " + ValueError
		return dt
		
#from netsvc import Service

#del Service._services['report.account.invoice.facturae.webkit']
report_sxw.report_sxw(
    'report.account.invoice.facturae.webkit',
    'account.invoice',
    'coloratodo_reports/report/invoice.mako',
    parser=PrintInvoice,
)
