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
from openerp.addons.web.controllers.main import Session
from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
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
ENTERPRISE = {'GMM':'clnpagos', 'MOR':'mayoreo', 'VOH':'vohcom', 'desarrollo':'contpaq_morsa_desarrollo'}
import sync_conexion
class sync_morsa_expense_newportal(models.Model):
    _name = 'sync.morsa.expense.newportal'


    def _get_enterprise_used(self):

        sesion = Session()
        informacion = sesion.get_session_info()
        bd = informacion.get('db')

        return bd[0:3]

    dFechaIni = fields.Date(
        'Fecha Inicial:',
        default = fields.Date.today(),
        required=True,
        help = 'Dia a partir del cual se sincronizarán gastos',
    )

    dFechaFin = fields.Date(
        'Fecha Final:',
        default = fields.Date.today(),
        required=True,
        help = 'Hasta que día se sincronizarán gastos',
    )


    # period = fields.Char(
    #     'Periodo: ',
    # )

    enterprise = fields.Char(
            'Enterprise:',
            default=lambda self: self._get_enterprise_used(),
            help='Write the code for enterprise \nGMM: culiacan \nMOR: mayoreo \nVOH: vohcom\n Example: GMM',
        )
    @api.multi
    def action_sync_expense_newportal(self):

        period = self.dFechaIni[5:7] + "/" + self.dFechaIni[0:4]
        if period != self.dFechaFin[5:7] + "/" + self.dFechaFin[0:4]:
            raise UserError("El rango de fechas debe de estar dentro del mismo periodo:", period)

        dbname = self.enterprise
        # _logger.debug("DB: %s" % dbname)
        # if dbname not in ENTERPRISE:
        #     raise UserError("Base de datos erronea favor de correr el proceso en la base de datos GMM")
        #get db
        dbname = ENTERPRISE[dbname]
        print "DBNAME", dbname
        conexion = self.env['sync.morsa.conexion']._get_conexion("conexion_openerp_expense.csv", dbname)
        #conexion = self.pool.get('sync.morsa.conexion')._get_conexion("conexion_openerp.csv", dbname)
        cursor = conexion.cursor()

        domain = [
            ('code', '=', period),
            ('company_id', '=', COMPANY_ID_MOR)
            ]

        period_id = self.env['account.period'].search(domain)
        obj_invoice = self.env['account.invoice']
        obj_invoice_line = self.env['account.invoice.line']

        attachment = self.env['ir.attachment']
        query_expenses = ("""SELECT dg.descripcion, dg.id_prov::int4 id_prov, dg.id_cuenta, id_sucursal, 
                                dg.concepto || ' ' || dg.id_sucursal id_ananew, 
                                dg.folio, dg.id_sucursal sucursal,  
                                g.fecha, g.referencia notes,
                                dg.cargo, dg.abono, dg.impuesto_importe, dg.impuesto_tasa,
                                fp.folio Factura, fp.serie, fp.foliofiscal, fp.emirfc, fp.xml, (subtotal::numeric/100)::numeric subtotal, fp.descuento,
                                fp.serie || '-' || fp.folio FactProv,
                                fp.emirfc || '_' || fp.serie || '-' || fp.folio || '.xml' XmlName,
                                lpad(g.sucursal::varchar,2,'0') SucG
                            FROM cxpdetallegastos dg left join cxpgastos g ON (dg.folio=g.folio)
                                    LEFT JOIN swpr_cfdcomprobanteproveedor fp ON (fp.foliofiscal = dg.folio_fiscal)
                            WHERE  g.tipo = '1' and g.fecha between '%s' AND '%s' 
                                    and id_prov is not null and id_prov <> '' and g.folio = 160022
                            ORDER BY g.fecha, dg.folio, fp.foliofiscal;"""%(self.dFechaIni,self.dFechaFin))
        cursor.execute(query_expenses)
        registros = cursor.fetchmany(10)
        print"REGISTROS", registros
        UUID = ''
        query_expenses = ''
        res = []
        for reg in registros:
            if reg[15]:
                if reg[15] != UUID:
                    #print"XML", reg[20].replace('\n','')
                    UUID = reg[15]
                    partner = self.env['res.partner'].search([('id', '=', reg[1])])
                    ou = self.env['operating.unit'].search([('code', '=', reg[22])])
                    invoice_header = {
                            'partner_id': partner.id,
                            'account_id': partner.property_account_payable.id,
                            'journal_id': 5,
                            'period_id' : period_id.id,
                            'operating_unit_id': ou.id,
                            'date_invoice': reg[7],
                            'internal_number': "%s/%s"%(reg[5],reg[20]),
                            'type'      : 'in_invoice',
                            'supplier_invoice_number': reg[20].rstrip(),
                            'origin'    : reg[5],
                            'comment'   : reg[12].replace(' ',''),
                        }
                    #print"INVOCE_HEADER", invoice_header
                    invoice = obj_invoice.create(invoice_header)
                    res.append(invoice)
                    #print"RES", res
                    xml = reg[17].replace('\n','')
                    xml_file = self._checking_characters(xml)
                    invoice_attachment = {
                    'name': reg[21].rstrip(),
                    'type': 'binary',
                    'datas': xml_file.encode('base64'),
                    'res_model': 'account.invoice',
                    'res_id': invoice.id,
                    }
                    attachment.create(invoice_attachment)
                    query_expenses = query_expenses + "UPDATE cxpgastos SET erp=%s WHERE folio=%s;"%(invoice.id,reg[5])

                cuenta = reg[4].rstrip()
                if reg[15] == UUID:
                    analytic_acc = ''
                    analytic_acc_id = ''
                    if '6' in cuenta[0:1]:
                        analytic_acc = self.env['account.analytic.account'].search([('name', 'like', cuenta)])
                        analytic_acc_id = analytic_acc.id

                    invoice_line = {
                            'name': reg[3].rstrip() + '|' + reg[0].rstrip(),
                            'account_id' : reg[2],
                            'account_analytic_id': analytic_acc_id,
                            'quantity': 1,
                            'price_unit': reg[9],
                            'invoice_line_tax_id': [
                                   (6, 0, [55]), #[x.id for x in product.supplier_taxes_id]),
                               ],
                            'invoice_id': invoice.id,
                        }
                    #print"INVOICE_LINE", invoice_line
                    obj_invoice_line.create(invoice_line)

        cursor.execute(query_expenses)
        conexion.commit()
        #
        # for x in res:
        #     try:
        #         x.button_compute()
        #         x.invoice_open()
        #     except:
        #         raise UserError("El folio de gasto/factura %s presenta errores en los importes"%(x['internal_number']))


    def _get_enterprise_used(self):

        sesion = Session()
        informacion = sesion.get_session_info()
        bd = informacion.get('db')

        return bd[0:3]

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

    # SELECT
    # dg.descripcion 0,
    # dg.id_prov::int4
    # id_prov 1,
    # dg.id_cuenta 2,
    # id_sucursal 3,
    # dg.concepto | | ' ' | | dg.id_sucursal id_ananew 4,
    # dg.folio 5,
    # dg.id_sucursal sucursal 6,
    # g.fecha 7,
    # g.referencia notes 8,
    # dg.cargo 9,
    # dg.abono 10,
    # dg.impuesto_importe 11,
    # dg.impuesto_tasa 12,
    # fp.folio Factura 13,
    # fp.serie 14,
    # fp.foliofiscal 15,
    # fp.emirfc 16,
    # fp.xml 17,
    # (subtotal::numeric / 100)::numeric subtotal 18,
    # fp.descuento 19

class account_invoice(orm.Model):
    _inherit = "account.invoice"


    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        """finalize_invoice_move_lines(cr, uid, invoice, move_lines) -> move_lines
        Hook method to be overridden in additional modules to verify and possibly alter the
        move lines to be created by an invoice, for special cases.
        :param invoice_browse: browsable record of the invoice that is generating the move lines
        :param move_lines: list of dictionaries with the account.move.lines (as for create())
        :return: the (possibly updated) final move_lines to create for this invoice

        Lo utilizo para cambiar las unidades operativas en el detalle de la poliza.
        """

        # move_lines = super(account_invoice, self).finalize_invoice_move_lines(
        #     cr, uid, invoice_browse, move_lines)
        new_move_lines = []
        for line_tuple in move_lines:
            new_name = line_tuple[2]['name']
            ou_position = new_name.find("|")
            if ou_position > 0:
                ou_code = new_name[0:ou_position]
                ou = self.pool.get('operating.unit').search(cr, uid, [('code', '=', ou_code)],context=None)
                new_name = new_name[ou_position+1::]
                line_tuple[2]['operating_unit_id'] = ou[0]
                line_tuple[2]['name'] = new_name
            new_move_lines.append(line_tuple)

        return new_move_lines
