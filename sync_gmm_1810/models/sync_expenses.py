# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 OpenERP s.a. (<http://openerp.com>).
#
#    DME SOLUCIONES
#    Jorge Medina <alfonso.moreno@dmesoluciones.com>
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

from openerp.osv import orm, fields
#from openerp import models, fields, api, exceptions, tools
from openerp import api, fields, models
from datetime import datetime, timedelta
from StringIO import StringIO
import openerp.netsvc
import glob
import os.path
import time
import psycopg2
import xmlrpclib
from openerp.tools.translate import _
import os
#log
import logging
import base64
import zipfile
_logger = logging.getLogger(__name__)

COMPANY_ID_MOR = 1
ENTERPRISE = {'GMM':'culiacan', 'MOR':'mayoreo', 'VOH':'vohcom', 'desarrollo':'contpaq_morsa_desarrollo'}
import sync_conexion
class sync_morsa_expense(models.Model):
    _name = 'sync.morsa.expense'

    period = fields.Char(
        'period',
        size = 6,
        help = 'mmaaaa',
        )
    enterprise = fields.Char(
            'Enterprise',
            help='Write the code for enterprise \nGMM: culiacan \nMOR: mayoreo \nVOH: vohcom\n Example: GMM',
        )
    @api.multi
    def action_sync_expense(self):
        dbname = self.enterprise.upper()
        period = self.period
        period = period[:2] + "/" + period[2:]
        _logger.debug("DB: %s" % dbname)
        if dbname not in ENTERPRISE:
             raise osv.except_osv(_("Sym GMM"), _("write a enterprise correct."))
        #get db
        dbname = ENTERPRISE[dbname]
        print "DBNAME", dbname
        conexion = self.env['sync.morsa.conexion']._get_conexion("conexion_openerp_expense.csv", dbname)
        #conexion = self.pool.get('sync.morsa.conexion')._get_conexion("conexion_openerp.csv", dbname)
        cursor = conexion.cursor()
        #sql_query = ('select * from sync_contpaq_openerp_rel limit 5')
        #cursor.execute(sql_query)
        #registros = cursor.fetchall()
        domain = [
            ('code', '=', period),
            ('company_id', '=', COMPANY_ID_MOR)
            ]
        period_id = self.env['account.period'].search(domain)
        obj_invoice = self.env['account.invoice']
        obj_invoice_line = self.env['account.invoice.line']
        attachment = self.env['ir.attachment']
        query_expenses = ("""SELECT scor.c_openerp, scor1.id_partner, scor.id_open, scor.id_ou_new, scor.id_ananew, scor.product_id,
                            p.numero, g.folio, g.sucursal, g.acreedor, g.fecha, g.importe, g.referencia notes,
                            dg.cuenta, cargo, abono,
                            fp.folio Factura, fp.serie, fp.foliofiscal, fp.emirfc, fp.xml, (subtotal::numeric/100)::numeric subtotal, fp.descuento,
                            (dfp.importe::numeric/100)::numeric tax_amount, dfp.impuesto,
                            cdfg.id_prov_fiscal
                            FROM cxpgastos g left join cxpdetallegastos dg ON (dg.folio=g.folio)
                            LEFT JOIN swpr_cfdcomprobanteproveedor fp ON (fp.folio_gasto = g.folio)
                            LEFT JOIN swpr_cfdimpuestosproveedor dfp ON (dfp.foliofiscal=fp.foliofiscal)
                            LEFT JOIN conta_detalle_facturas_gasto cdfg ON (cdfg.uuid=fp.foliofiscal)
                            LEFT JOIN polizas p ON (p.referencia::integer = g.folio)
                            LEFT JOIN sync_contpaq_openerp_rel scor ON (replace(scor.c_contpaq,'-','') = dg.cuenta)
                            LEFT JOIN sync_contpaq_openerp_rel scor1 ON (replace(scor1.c_contpaq,'-','') = g.acreedor)
                            WHERE g.tipo = '1' AND p.tipo_poliza = 'D' /*g.folio = 37409 37244  AND p.tipo_poliza = 'D'*/ AND p.referencia ~ '^\d+(.\d+)?$'
                            AND p.fecha between '2018-02-01' AND '2018-02-28'
                            ORDER BY p.numero, fp.foliofiscal;""")
        cursor.execute(query_expenses)
        registros = cursor.fetchmany(10)
        #print"REGISTROS", registros
        UUID = ''
        res = []
        for reg in registros:
            if reg[18]:
                if reg[18] != UUID:
                    #print"XML", reg[20].replace('\n','')
                    UUID = reg[18]
                    partner = self.env['res.partner'].search([('id', '=', 1797)])
                    invoice_header = {
                            'partner_id': partner.id,
                            'account_id': partner.property_account_payable.id,
                            'journal_id': 14,
                            'period_id' : period_id.id,
                            'type'      : 'in_invoice',
                            'origin'    : reg[7],
                            'comment'   : reg[12].replace(' ',''),
                        }
                    #print"INVOCE_HEADER", invoice_header
                    invoice = obj_invoice.create(invoice_header)
                    res.append(invoice)
                    #print"RES", res
                    xml = reg[20].replace('\n','')
                    xml_file = self._checking_characters(xml)
                    invoice_attachment = {
                    'name':'gasto.xml', #'.'.join([name, extension]),
                    'type': 'binary',
                    'datas': xml_file.encode('base64'),
                    'res_model': 'account.invoice',
                    'res_id': invoice.id,
                    }
                    attachment.create(invoice_attachment)
                cuenta = str(reg[0])
                if reg[18] == UUID:
                    if '6' in cuenta[0:1]:
                        product = self.env['product.product'].search([('id', '=', 292)])
                        invoice_line = {
                                'product_id': product.id,
                                'name': product.name,
                                'account_id' : product.categ_id.property_account_expense_categ.id,
                                'account_analytic_id': reg[3],
                                'quantity': 1,
                                'price_unit': reg[14],
                                'uos_id': product.uom_id.id,
                                'invoice_line_tax_id': [
                                        (6, 0, [x.id for x in product.supplier_taxes_id]),
                                    ],
                                'invoice_id': invoice.id,
                            }
                        #print"INVOICE_LINE", invoice_line
                        obj_invoice_line.create(invoice_line)
        for x in res:
            x.button_reset_taxes()
            x.invoice_open()

    def _checking_characters(self, cadena=None):
        nueva_cadena = ''
        if cadena > '':
            for l in cadena:
                x = l
                if x == u'Ã':
                    x = 'e'
                elif x == u'©':
                    x = 'i'
                elif x == u'\xad':
                    x = ''
                elif x == u'­-':
                    x = ''
                nueva_cadena = nueva_cadena + x
                #print"TTTTTTTTTTTTTTTT", nueva_cadena
        if nueva_cadena == '':
            nueva_cadena = str(cadena)
        return nueva_cadena