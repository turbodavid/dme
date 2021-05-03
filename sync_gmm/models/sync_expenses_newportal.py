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
import sync_conexion
_logger = logging.getLogger(__name__)

COMPANY_ID_MOR = 1
ENTERPRISE = {'GMM':'culiacan', 'MOR':'mayoreo', 'VOH':'vohcom', 'desarrollo':'contpaq_morsa_desarrollo'}
JOURNALCODE = { '1':'MISC', '2':'GTOREP','3':'ANTCI', '4':'GTOCOMP','6':'GTOVIAT','7':'NCGTOS', 'ND': 'GTOND'}
PAYMENT_TYPE_CODE = '03'
TAXCODESALE = {'16': 50, '8': 69}

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

    ou  = fields.Many2one(
                'operating.unit', 'Operating Unit:',
                domain=[('code', 'not ilike', '-')],
                required=True
        )

    expense_type = fields.Selection(
         string='Tipo de Gasto:',
         default='1',
         selection=[('1','1-Normal'),
                    ('2','2-Reposición/Reembolso'),
                    ('3','3-Anticipos'),
                    ('4','4-Comprobación'),
                    ('6','6-Comprobación Viáticos')
                ]
    )

    afectar_estatus  = fields.Boolean('Afectar el Estatus de las Facturas al procesar', default=True)

    @api.multi
    def action_sync_expense_newportal(self):

        period = self.dFechaIni[5:7] + "/" + self.dFechaIni[0:4]
        if period != self.dFechaFin[5:7] + "/" + self.dFechaFin[0:4]:
            raise UserError("El rango de fechas debe de estar dentro del mismo periodo:", period)

        if self.expense_type == '3':
            self._do_anticipos()
            return

        dbname = self.enterprise
        # _logger.debug("DB: %s" % dbname)
        # if dbname not in ENTERPRISE:
        #     raise UserError("Base de datos erronea favor de correr el proceso en la base de datos GMM")
        #get db
        dbname = ENTERPRISE[dbname]
        print "DBNAME", dbname
        conexion = self.env['sync.morsa.conexion']._get_conexion("conexion_openerp_expense_newportal.csv", dbname)
        #conexion = self.pool.get('sync.morsa.conexion')._get_conexion("conexion_openerp.csv", dbname)
        cursor = conexion.cursor()

        domain = [
            ('code', '=', period),
            ('company_id', '=', COMPANY_ID_MOR)
            ]

        period_id = self.env['account.period'].search(domain)
        obj_invoice = self.env['account.invoice']
        obj_invoice_line = self.env['account.invoice.line']
        obj_expense = self.env['hr.expense.expense']
        obj_expense_line = self.env['hr.expense.line']
        attachment = self.env['ir.attachment']
        obj_ir_attachment_facturae = self.env['ir.attachment.facturae.mx']
        acc_journal = self.env['account.journal'].search([('code', '=', JOURNALCODE[self.expense_type])])
        acc_journal_nc = self.env['account.journal'].search([('code', '=', JOURNALCODE['7'])])
        acc_journal_nd = self.env['account.journal'].search([('code', '=', JOURNALCODE['ND'])])
        res_company = self.env['res.company'].search([('id', '=', COMPANY_ID_MOR)])

        """NECESITO SACAR LOS IVAS DE CREDITO Y DE CONTADO PARA LOS GASTOS NORMALES"""
        account_tax = self.env['account.tax'].search([('description','=','IVA16GASTOS')])
        taxcredito = account_tax.id
        account_tax = self.env['account.tax'].search([('description', '=', 'IVA16GTOCONT')])
        taxcontado = account_tax.id

        #primero valido que la información este congruente
        query_expenses = self._get_sql_update_info()
        cursor.execute(query_expenses)
        conexion.commit()

        query_expenses = self._valida_rfcs()
        cursor.execute(query_expenses)
        registros = cursor.fetchall()
        query_expenses = ''
        folio = ''
        try:
            for reg in registros:
                query_expenses = query_expenses + \
                                "\nFolio: %s, Tipo: %s, Serie: %s, Factura: %s, RFC: %s, Nombre: %s"%\
                                 (reg[1],reg[0],reg[3],reg[4], reg[5], reg[7])

            if query_expenses:
                raise UserError("Los siguientes folios no cuentan con RFC asignado: ", query_expenses)

            #ejecuto el query
            query_expenses = self._get_sql_expenses()
            cursor.execute(query_expenses)
            registros = cursor.fetchall()

            #print"REGISTROS", registros
            dgids = ''
            dgsqlupdate = ''
            ginvoice = ''
            UUID = ''
            folio = ''
            query_expenses = ''
            ataxes_ = []
            res = []
            invoice = ''

            for reg in registros:

            #NECESITO CONTROLAR LOS FOLIOS PARA DETECTAR LOS NO DEDUCIBLES CUANDO NO SEAN GASTO 1
            #EL folio_fiscal vacio indica si es o no deduble o el archivo vacio

            #como reonocer qeu cumple fiscalmente
            #xmlfil es vacio

                xml = ''
                xml_file = ''
                if reg[17]:
                    xml = reg[17].replace('\n', ' ').rstrip()
                    xml_file = self._checking_characters(xml)

                idpartner = int(reg[1]) if reg[1].rstrip() else ''

                if folio != reg[5]:

                    #es posible que exista un pago, crear el pago
                    # if follio:
                    #     self._crea_pago(reg)
                    if folio and self.afectar_estatus:
                        if not esfiscal:
                            ginvoice = idexpense
                            query_expenses = "UPDATE cxpgastos SET erp=%s, estatus=%s, estatusgasto='%s' WHERE folio=%s;" % (
                                                    '1', '9', 'V', folio)
                        if dgids:
                            dgsqlupdate = dgsqlupdate + query_expenses + "UPDATE cxpdetallegastos SET invoice_id = %s WHERE id_detallegastos IN (%s);"%\
                                          (ginvoice ,dgids)

                        query_expenses = ''
                        dgids = ''

                    idexpense = ''
                    expense = ''
                    folio = reg[5]

                    #crea el vinculo al Hr Expense
                    if self.expense_type in ['2','4','6']:

                        if self.expense_type != '4' or (self.expense_type == '4' and self._is_employee(reg)):

                            aids = self._get_employee(reg[29], reg[34], reg[32])
                            expense_header = {
                                'name': self.expense_type + ':' + str(folio) + "|" + reg[8].strip(),
                                'employee_id': aids[0],
                                'partner_id': aids[1],
                                'date': reg[7],
                                'operating_unit_id': self.ou.id,
                                    }
                            expense = obj_expense.create(expense_header)
                            idexpense = expense.id

                esfiscal = True if (xml_file and xml_file != "0") and idpartner else False
                #if reg[15].strip():
                if esfiscal or self.expense_type == '1':
                   # if dgids:
                   #     dgsqlupdate = dgsqlupdate + "UPDATE cxpdetallegastos SET invoice_id = %s WHERE id_detallegastos IN (%s);"%(ginvoice,dgids)

                    if reg[15] != UUID:
                        if dgids:
                            dgsqlupdate = dgsqlupdate + query_expenses + "UPDATE cxpdetallegastos SET invoice_id = %s WHERE id_detallegastos IN (%s);"%(ginvoice, dgids)

                        if invoice:
                            invoice.button_reset_taxes()

                        #print "Folio Gasto: ", reg[5]
                        #print"XML", reg[20].replace('\n','')
                        dgids = ''
                        query_expenses = ''
                        internalnumber = str(folio)
                        UUID = reg[15]
                        partner = self.env['res.partner'].search([('id', '=', idpartner if idpartner else res_company.partner_id.id)])

                        supplierinvoice = reg[20].strip() if reg[20] else ''
                        journalid = acc_journal.id
                        doctotype = 'in_invoice'
                        if esfiscal:
                            if supplierinvoice == '0':
                                supplierinvoice = UUID[-4:]

                            if reg[38] == 'E':
                                journalid = acc_journal_nc.id
                                doctotype = 'in_refund'

                            internalnumber +=  '/' + supplierinvoice
                        else:
                            internalnumber += '/ND'
                            journalid = acc_journal_nd.id

                        # ou = self.env['operating.unit'].search([('code', '=', reg[22])])
                        invoice_header = {
                                'partner_id': partner.id if partner else 1,
                                'account_id': partner.property_account_payable.id,
                                'journal_id': journalid,
                                'period_id' : period_id.id,
                                'operating_unit_id': self.ou.id,
                                'date_invoice': reg[7],
                                'internal_number': internalnumber,
                                'type'      : doctotype,
                                'supplier_invoice_number': supplierinvoice,
                                'origin'    : reg[5],
                                'comment'   : reg[8].strip(),
                                'expense_id': idexpense,
                            }
                        #print"INVOCE_HEADER", invoice_header
                        invoice = obj_invoice.create(invoice_header)
                        res.append(invoice)
                        ginvoice = invoice.id
                        ataxes_ = []


                        if esfiscal:
                            #PARA EL ATTACHMENTE DE ARCHIVO AL DOCUMENTO
                            #print"RES", res
                            invoice_attachment = {
                                'name': reg[21].rstrip(),
                                'type': 'binary',
                                'datas': xml_file.encode('base64'),
                                'res_model': 'account.invoice',
                                'res_id': invoice.id,
                            }
                            attch = attachment.create(invoice_attachment)

                            """LOGICA PARA ASIGNAR EL UUID A LA FACTURA CREADA EL UUID SE SACA DEL 
                            REGISTRO DONDE SE CREA EL ATTACHMENT"""
                            attachment_facturae = {
                                'name': "%s/%s"%(reg[5],reg[20]),
                                'rfc_emisor': partner.vat[2:].strip().upper(),
                                'uuid': reg[15],
                                'state': 'done',
                                'company_id': 1,
                                'cfdi_type': 'outgoing',
                                'file_xml_sign': attch.id,
                                'type_attachment': 'account.invoice',
                                'res_id': invoice.id,
                            }
                            attch = ''
                            attch = obj_ir_attachment_facturae.create(attachment_facturae)
                            if attch:
                                invoice.write( {'cfdi_id' : attch.id })
                        elif self.expense_type == '1':
                            idexpense = ginvoice

                        #query_expenses = query_expenses + "UPDATE cxpgastos SET erp=%s WHERE folio=%s;"%(invoice.id,reg[5])
                        if self.afectar_estatus:
                            query_expenses = "UPDATE cxpgastos SET erp=%s, estatus=%s, estatusgasto='%s' WHERE folio=%s;"%( '1', '9', 'V', reg[5])

                    cuenta = reg[4].rstrip()
                    if reg[15] == UUID:
                        analytic_acc = ''
                        analytic_acc_id = ''
                        if reg[23]:
                            analytic_acc_id = int(reg[23].rstrip())

                        if analytic_acc_id:
                            analytic_acc = self.env['account.analytic.account'].search([('id','=', analytic_acc_id)])

                            if (not analytic_acc and '6' in cuenta[0:1]) or analytic_acc.type <> 'normal':
                                analytic_acc = self.env['account.analytic.account'].search([('name', 'like', cuenta)])
                                analytic_acc_id = analytic_acc.id


                        """AGREGA LOS IMPUESTOS Y HAZ EL CAMBIO SI APARECE UN IVA DE CREDITO Y NO ES GASTO NORMAL"""
                        taxtoadd = ''
                        for i in range(24,27):
                            if reg[i]:
                                taxtoadd = int(reg[i].rstrip())
                                if self.expense_type <> '1' and taxtoadd == taxcredito:
                                    taxtoadd = taxcontado
                                ataxes_.append(taxtoadd)

                        invoice_line = {
                                'name': reg[22].rstrip() + '|' + reg[0].rstrip(),
                                'account_id' : reg[2],
                                'account_analytic_id': analytic_acc_id,
                                'quantity': 1,
                                'price_unit': reg[9],
                                'invoice_line_tax_id': [
                                       (6, 0,  ataxes_), #[x.id for x in product.supplier_taxes_id]),
                                   ],
                                'invoice_id': invoice.id,
                            }
                        #print"INVOICE_LINE", invoice_line
                        obj_invoice_line.create(invoice_line)
                        if dgids:
                            dgids = dgids + ', ' + str(reg[28])
                        else:
                            dgids = str(reg[28])

                elif idexpense:
                    #se crea el no deducible
                    obj_expense_line = self._crea_nodeducible(idexpense,reg)
                    ginvoice = expense.id
                    if dgids:
                        dgids = dgids + ', ' + str(reg[28])
                    else:
                        dgids = str(reg[28])

            # for x in res:
            #     try:
            #         x.button_compute()
            #         x.invoice_open()
            #     except:
            #         raise UserError("El folio de gasto/factura %s presenta errores en los importes"%(x['internal_number']))

            if invoice:
                invoice.button_reset_taxes()

            if folio and self.afectar_estatus:
                ginvoice = idexpense if not esfiscal else ginvoice
                query_expenses = "UPDATE cxpgastos SET erp=%s, estatus=%s, estatusgasto='%s' WHERE folio=%s;" % (
                    '1', '9', 'V', folio)
            if dgids:
                if dgsqlupdate:
                    dgsqlupdate = dgsqlupdate + query_expenses + "UPDATE cxpdetallegastos SET invoice_id = %s WHERE id_detallegastos IN (%s);" % (ginvoice, dgids)
                else:
                    dgsqlupdate = query_expenses + "UPDATE cxpdetallegastos SET invoice_id = %s WHERE id_detallegastos IN (%s);" % (ginvoice, dgids)

            if dgsqlupdate:
                cursor.execute(dgsqlupdate)

                conexion.commit()
        except Exception as e:
            if folio:
                raise UserError("Error Folios de Gastos",
                           "Folio: %s, ID DetGatos: %s, Factura: %s. \n\nERROR: %s" % (folio, reg[28], reg[13], repr(e)))
            else:
                raise UserError("Aviso de Error",repr(e))
        finally:
            conexion.close()

    def _crea_pago(self,datos):
        paymentid = ''
        return paymentid

    def _crea_nodeducible(self,expense_id,datos):


        #si trae cuenta, esa debe de ser la buena
        if datos[2]:
            acc_obj = self.env['account.account'].search([('id','=',datos[2])])
        else:
            acc_obj = self.env['account.account'].search([('code','=',datos[4][0:datos[4].find(" ")])])

        product = ''
        if acc_obj:
            product_obj = self.env['product.product'].search(
                        [('default_code', '=', acc_obj.code)])
            if not product_obj:
                product = product_obj.create( {'name' : acc_obj.name,
                                               'default_code': acc_obj.code,
                                               'property_account_expense' : acc_obj.id,
                                               'hr_expense_ok': True,
                                               'type': 'service',
                                               })
            else:
                product = product_obj

        non_deduc_line = {
            'product_id' : product.id if product else '',
            'name' : datos[0],
            'unit_amount' : datos[9],
            'date_value' : datos[7],
            'ref' : datos[28],
            'expense_id' : expense_id,
            'analytic_account' : int(datos[23]) if datos[23] else '',
        }

        obj_expense_line = self.env['hr.expense.line']
        obj_expense_line = obj_expense_line.create(non_deduc_line)
        return obj_expense_line

    def _get_sql_expenses(self):

        sql_expenses = ("""
            SELECT dg.descripcion, dg.id_prov id_prov, dg.id_cuenta, id_sucursal, 
                    dg.concepto || ' ' || case when position('-' in sucupro) > 0 then left(sucupro,position('-' in sucupro)-1) else sucupro end id_ananew,
                    dg.folio, dg.id_sucursal sucursal,  
                    g.fecha, g.referencia notes,
                    case when trim(dg.totalprorreteado) ~ '^\d+(.\d+)?$' then trim(dg.totalprorreteado)::numeric else dg.importe end cargo, dg.abono, 
                    dg.impuesto_importe, dg.impuesto_tasa,
                    fp.folio Factura, trim(fp.serie) serie, trim(fp.foliofiscal) foliofiscal, fp.emirfc, 
                    regexp_replace(fp.xml, '[^\x20-\x7f\x0d\x1b]', '', 'g') xmlfile, 
                    (subtotal::numeric/100)::numeric subtotal, fp.descuento,
                    trim(fp.serie) || case when trim(fp.serie) <> '' and fp.serie is not null then '-' else 'Fact-' end || fp.folio FactProv,
                    fp.emirfc || '_' || fp.serie || case when trim(serie) <> '' and serie is not null then '-' else '' end  || fp.folio || '.xml' XmlName,
                    trim(sucupro) SucG,
                    trim(dg.id_ctaana), trim(dg.impuesto_id), 
                    trim(dg.impuesto_id2), trim(dg.impuesto_id3), trim(dg.impuesto_id4), dg.id_detallegastos,
                    trim(dg.id_emp), g.acreedor acrfolio, acr.rfc rfcfolio, acr.nombre nombrefolio, acr.clabe clabe, 
                    scor.id_partner partner_id_folio, 
                    bank.codigo_interno bankcode, cpag.cuenta numctapagadora, scorbank.id_open bank_acc_id, fp.tipo_de_documento
            FROM cxpgastos g  left join cxpdetallegastos dg ON (g.folio=dg.folio)
                    LEFT JOIN swpr_cfdcomprobanteproveedor fp ON (dg.folio_fiscal = fp.foliofiscal)
                    left join acrectas acr on (g.acreedor=acr.acreedor)
                    left join fn_scor() scor on (g.acreedor=replace(scor.c_contpaq,'-',''))
                    left join cxcctaspag cpag on (g.banco=cpag.numero)
                    left join cxcbancos bank on (cpag.banco=bank.banco)
                    left join fn_scor() scorbank on (trim(cpag.ctacon_bco)=replace(scorbank.c_contpaq,'-',''))
            WHERE %s
            ORDER BY dg.folio, fp.tipo_de_documento desc, dg.folio_fiscal, dg.id_detallegastos;""")%(self._get_where_clause())

        #g.tipo = '%s' and  %s and dg.id_sucursal_erp = %s and dg.invoice_id is null
        #            and g.fecha between '%s' AND '%s'
        #    ORDER BY dg.folio, dg.folio_fiscal, dg.id_detallegastos;""")%(self.expense_type, self._get_where_clause(), int(self.ou.co
        #
        # and (id_prov is not null and id_prov <> '')

        return sql_expenses

    def _valida_rfcs(self):

        sql = "select distinct g.tipo, g.folio, dg.id_prov, swpr.serie, swpr.folio factura, " \
                               "swpr.emirfc, rfcs.rfc_sat, swpr.eminombre " \
               "from cxpgastos g inner join cxpdetallegastos dg on (dg.folio = g.folio) " \
	                 "inner join swpr_cfdcomprobanteproveedor swpr on (dg.folio_fiscal=swpr.foliofiscal) " \
	                 "left join openerp_get_rfcs() rfcs on swpr.emirfc = rfcs.rfc_sat " \
               "where (dg.folio_fiscal is not null and trim(dg.folio_fiscal) != '' ) and" \
               " ( (trim(emirfc) <> '' and (rfcs.rfc_sat <> swpr.emirfc or rfc_sat is null)) or trim(dg.id_prov) = '') and %s" \
               "order by g.tipo, g.folio, dg.id_prov, swpr.serie, swpr.folio , swpr.emirfc, rfcs.rfc_sat, swpr.eminombre;"%(self._get_where_clause(True))

        return sql

    def _get_sql_update_info(self):

        swhere = self._get_where_clause(False)

        #Sucursales
        sql = ("""update cxpdetallegastos dg set id_sucursal_erp = s.codigo_erp 
                 from cxpgastos g, cat_sucursales s 
                 where dg.folio = g.folio  and dg.id_sucursal::int = s.num_suc 
                        and (id_sucursal_erp is null or id_sucursal_erp <> s.codigo_erp) and %s;""")%(swhere)

        swhere = self._get_where_clause(True)

        sqlanok = "(select id from " \
		              "openerp_get_ctasana() " \
		                "where nombre like trim(dg.concepto) || ' ' || case " \
		                                        "when position('-' in sucupro) > 0 then left(trim(sucupro),position('-' in sucupro)-1) " \
		                                        "else trim(sucupro) end || '%' limit 1) anaok, "


        sqlana = "( select dg.id_detallegastos, %s " \
		                    "dg.concepto || ' ' || case " \
		                                    "when position('-' in sucupro) > 0 then left(sucupro,position('-' in sucupro)-1) " \
		                                    "else sucupro end concepto " \
                                "from cxpgastos g inner join cxpdetallegastos dg on (dg.folio = g.folio) " \
                                "where left(dg.concepto,1) >= '6' and %s ) tmp"%(sqlanok,swhere)

        #Analiticas
        sql = sql + ("""update cxpdetallegastos set id_ctaana = tmp.anaok::text
                        from  %s
                 where cxpdetallegastos.id_detallegastos = tmp.id_detallegastos and
                        (cxpdetallegastos.id_ctaana <> tmp.anaok::text or cxpdetallegastos.id_ctaana is null);""")%(sqlana)

        #Cuentas Contable
        sql =  sql + ("""update cxpdetallegastos dg set id_cuenta = aa.id 
                  from cxpgastos g, openerp_get_ctascon() aa 
                  where dg.folio = g.folio and dg.concepto = aa.code
                        and dg.id_cuenta <> aa.id and %s;""")%(swhere)

        #RFC's
        sql = sql + ("""update cxpdetallegastos dg set id_prov = rfcs.id::text 
                  from cxpgastos g, swpr_cfdcomprobanteproveedor swpr, openerp_get_rfcs() rfcs
                  where dg.folio = g.folio and dg.folio_fiscal=swpr.foliofiscal and 
                        trim(swpr.emirfc)=rfcs.rfc_sat and dg.id_cuenta > 0 
                        and rfcs.id::text <> id_prov and trim(emirfc) <> '' and %s;""")%(swhere)

        # empleados
        if self.expense_type in ['2','6']:
            sql = sql + \
                  ("""update cxpdetallegastos dg set id_emp = scor.id_partner 
                      from cxpgastos g, fn_scor() scor 
                      where dg.folio = g.folio and
                            g.acreedor=replace(scor.c_contpaq,'-','') and
                            g.tipo in ('2','6') and 
                            (id_emp is null or trim(id_emp) in ( '0', 't')) and %s;""")%(swhere)

        # elif self.expense_type == '4':
        #     sql = sql +\
        #           ("""update cxpdetallegastos dg set id_emp = null
        #               from cxpgastos g, fn_scor() scor
        #               where dg.folio = g.folio and
        #                     g.acreedor=replace(scor.c_contpaq,'-','') and
        #                     g.tipo =  '4' and trim(id_emp) in ('0', 't') and %s;""")%(swhere)

        return sql


    def _get_where_clause(self, incluyesucursal=True):

        ctipogasto = self.expense_type

        if ctipogasto == '3':
            sqlwhere = ("""g.tipo = '3' and g.estatus ='4' and estatusgasto='A' and
                            (g.erp is null or g.erp = '0') and  
                            suc.codigo_erp = %s and to_date(g.ref_pago, 'YYYYMMDD') between '%s' and '%s'
                        """) % (int(self.ou.code), self.dFechaIni, self.dFechaFin)
            return sqlwhere

        sqlwhere = """(g.estatus ='1' and estatusgasto='V')"""

        if incluyesucursal:
            sqlwhere = ("""g.tipo = '%s' and  %s and dg.id_sucursal_erp = %s and dg.invoice_id is null 
                    and g.fecha between '%s' AND '%s' """)%(ctipogasto, sqlwhere, int(self.ou.code), self.dFechaIni, self.dFechaFin)
        else:
            sqlwhere = ("""g.tipo = '%s' and  %s  and dg.invoice_id is null 
                    and g.fecha between '%s' AND '%s' """)%(ctipogasto, sqlwhere, self.dFechaIni, self.dFechaFin)

        return sqlwhere

    def _get_employee(self,  idemp, idpartnerfolio, empname):

        emp_id = ''
        partner_id = ''
        if idemp and idemp not in ('0', 't'):
            if self.expense_type != '4' and idpartnerfolio and idemp != idpartnerfolio:
                partner_id = idpartnerfolio
            else:
                partner_id = int(idemp)
        else:
            partner_id = idpartnerfolio

        obj_emp = self.env['hr.employee'].search([('address_id', '=', partner_id)])
        if not obj_emp.id:
            emp_data = {
                'name' : empname,
                'address_home_id': partner_id,
                'address_id': partner_id,
            }
            employee = obj_emp.create(emp_data)
            emp_id = employee.id
        else:
            emp_id = obj_emp.id

        return [emp_id,partner_id]

    def _is_employee(self,datos):

        isemployee = True
        idemp = ''
#        if datos[29] and datos[29] not in ['0','t']:
#            idemp = int(datos[29])
        idpartnerfolio = datos[34] if datos[34] else ''
        if datos[29] and datos[29] not in ['0', 't']:
            if self.expense_type != '4' and idpartnerfolio and idemp != idpartnerfolio:
                idemp = idpartnerfolio
            else:
                idemp = int(datos[29])

        if not idemp:
            isemployee = False
            partnerid = int(datos[1]) if datos[1] else ''
            if partnerid:
                partner_obj = self.env['res.partner'].search([('id','=',partnerid)])
                isemployee = partner_obj.employee if partner_obj else False

        return isemployee

    def _do_anticipos(self):
        dbname = ENTERPRISE[self.enterprise]
        conexion = self.env['sync.morsa.conexion']._get_conexion("conexion_openerp_expense_newportal.csv", dbname)

        curanticipo =  conexion.cursor()
        query_anticipos = self._get_sql_anticipos()
        curanticipo.execute(query_anticipos)
        records = curanticipo.fetchall()


        if not records:
            raise UserError("There are not advance payments within the given parameters")

        #folio                  0
        #fecha                  1
        #sucursal               2
        #notes                  3
        #importe                4
        #acrfolio               5
        #rfcfolio               6
        #nombrefolio            7
        #clabe                  8
        #partner_id_folio       9
        #bankcode               10
        #numctapagadora         11
        #bank_acc_id            12
        #bannkname              13

        try:
            period = self.dFechaIni[5:7] + "/" + self.dFechaIni[0:4]
            ap = self.env['account.period'].search([('code','=',period)])
            obj_am = self.env['account.move']
            obj_aml = self.env['account.move.line']
            obj_partner = self.env['res.partner']
            sql_update = ''
            partnerid = ''
            msgdata = ''

            for record in records:

                msgdata = 'Folio: ' + str(record[0]) + ". "
                # PRIMERO BUSCO POR EL RFC
                rfc = 'MX'+record[6]
                if rfc:
                    msgdata += 'RFC: ' + record[6] + ". "
                    partner = obj_partner.search([('vat', '=', rfc),('active','=',True)])
                    if not partner:
                        partnerid = record[9]
                        partner = obj_partner.search([('id', '=', partnerid)])
                        if not partner:
                            continue
                    partnerid = partner.id

                if not partner.vat_subjected:
                    partner.write( {'vat_subjected' : True })


                journalid = self._get_journal_anticipos(record)
                #ENCABEZADO
                header = {
                    'partner_id'        : partnerid,
                    'date'              : record[1],
                    'ref'               : record[0],
                    'journal_id'        : journalid,
                    'operating_unit_id' : self.ou.id,
                    'company_id'        : COMPANY_ID_MOR,
                    'period_id'         : ap.id,
                    'narration'         : record[3] + '. Depositado a la cuenta: ' + record[8]
                    }

                am = obj_am.create(header)

                adatos_ = [
                    [record[0], partner.property_account_receivable.id, record[4], 0],
                    [record[8], record[12], 0, record[4]]
                        ]

                msgdata += "Cuenta Contable: " + partner.property_account_receivable.code + " " + \
                                partner.property_account_receivable.name

                #DETALLE DE POLIZA
                for i in (0, 1):

                    header = {
                        'partner_id': partnerid,
                        'name': adatos_[i][0],
                        'journal_id': journalid,
                        'account_id': adatos_[i][1],
                        'debit'     : adatos_[i][2],
                        'credit'    : adatos_[i][3],
                        'operating_unit_id': self.ou.id,
                        'company_id': COMPANY_ID_MOR,
                        'period_id' : ap.id,
                        'move_id'   : am.id
                    }
                    aml = obj_aml.create(header)

                sql_update += "update cxpgastos set erp = '2' where folio = %s;"%(record[0])

            if sql_update:
                curanticipo.execute(sql_update)
                conexion.commit()
        except Exception as e:
            if msgdata:
                msgdata += "\n" + repr(e)
                raise UserError("Error procesando anticipos\n", msgdata)
            else:
                raise e
        finally:
            curanticipo.close()
            conexion.close()

        return

    def _get_journal_anticipos(self, record):

        journalcode = 'AN' + record[10] + record[11][-4:]
        obj_journal = self.env['account.journal'].search([('code', '=', journalcode)])
        journalid = obj_journal.id

        if not journalid:
            data = {
                'name': 'Anticipos ' + record[13].title() + ' ' + record[11][-4:],
                'prefix': journalcode + '/%(y)s%(month)s/',
                'padding': 5,
                'number_next_actual': 1,
                'number_increment': 1,
                'implementation': 'standard'

            }
            sequence = self.env['ir.sequence'].create(data)
            obj_payment_type = self.env['payment.type'].search([('code','=', PAYMENT_TYPE_CODE)])

            data = {
                'name': 'Anticipos ' + record[13].title() + ' ' + record[11][-4:],
                'code': journalcode,
                'type': 'bank',
                'payment_type_id': obj_payment_type.id,
                'default_debit_account_id': record[12],
                'default_credit_account_id': record[12],
                'update_posted': True,
                'sequence_id': sequence.id

            }
            journal = obj_journal.create(data)
            journalid = journal.id

        return journalid

    def _get_sql_anticipos(self):


        sql_anticipos = ("""
            select  g.folio, to_date(g.ref_pago, 'YYYYMMDD') fecha, g.sucursal, trim(g.referencia) notes, 
                    g.importe, trim(g.acreedor) acrfolio, trim(acr.rfc) rfcfolio, trim(acr.nombre) nombrefolio, trim(acr.clabe) clabe, 
                    scor.id_partner partner_id_folio, 
                    trim(bank.codigo_interno) bankcode, trim(cpag.cuenta) numctapagadora, 
                    scorbank.id_open bank_acc_id, trim(bank.nombre) bankname
            from  cxpgastos g  
                left join acrectas acr on (g.acreedor=acr.acreedor)
                left join fn_scor() scor on (trim(g.acreedor)=replace(trim(scor.c_contpaq),'-',''))
                left join cxcctaspag cpag on (g.banco=cpag.numero)
                left join cxcbancos bank on (cpag.banco=bank.banco)
                left join fn_scor() scorbank on (trim(cpag.ctacon_bco)=replace(trim(scorbank.c_contpaq),'-',''))
                inner join cat_sucursales suc on (g.sucursal = suc.num_suc)            
            where %s order by g.folio;""") % (self._get_where_clause())

        return sql_anticipos

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
    # dg.id_prov::int id_prov 1,
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
    # FactProv 20
    # XmlName 21
    # SucG 22
    # dg.id_ctaana 23
    # dg.impuesto_id 24
    # dg.impuesto_id2 25
    # dg.impuesto_id3 26
    # dg.impuesto_id4 27
    # dg.id_detallegastos 28
    # dg.id_emp  29
    # g.acreedor acrfolio 30
    # acr.rfc rfcfolio 31
    # acr.nombre nombrefolio 32
    # acr.clabe clabe  33
    # scor.id_partner partner_id_folio 34
    # bank.codigo_interno bankcode 35
    # cpag.cuenta umctapagadora 36
    # scorbank.id_open bank_acc_id 37
    # fp.tipo_de_documento 38


class AccountInvoice(orm.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_open(self):

        curinternalnumber = ''
        if self.type == 'in_invoice' and self.origin and self.supplier_invoice_number:
            curinternalnumber = self.origin.strip() + "/" + self.supplier_invoice_number.strip()
            if curinternalnumber != self.internal_number:
                self.write({'internal_number': curinternalnumber})
        super(AccountInvoice, self).invoice_open()

        return

    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        """finalize_invoice_move_lines(cr, uid, invoice, move_lines) -> move_lines
        Hook method to be overridden in additional modules to verify and possibly alter the
        move lines to be created by an invoice, for special cases.
        :param invoice_browse: browsable record of the invoice that is generating the move lines
        :param move_lines: list of dictionaries with the account.move.lines (as for create())
        :return: the (possibly updated) final move_lines to create for this invoice

        Lo utilizo para cambiar las unidades operativas en el detalle de la poliza.
        """
        #invoice_browse.operating_unit_id
        # move_lines = super(account_invoice, self).finalize_invoice_move_lines(
        #     cr, uid, invoice_browse, move_lines)
        new_move_lines = []
        new_tuple = ''
        for line_tuple in move_lines:
            new_name = line_tuple[2]['name']
            ou_position = new_name.find("|")
            if ou_position > 0:
                ou_code = new_name[0:ou_position]
                # acc = self.ppol.get('account.account').search(cre,uid,[('id','=',line_tuple[2]['account_id'])])
                # if acc['type'] in ['payable','receivable']:
                #     ou_position = ou_code.find("-")
                #     if ou_position > 0:
                #         ou_code = ou_code[0:ou_position]
                ou = self.pool.get('operating.unit').search(cr, uid, [('code', '=', ou_code)],context=None)
                new_name = new_name[ou_position+1::]
                line_tuple[2]['operating_unit_id'] = ou[0]
                line_tuple[2]['name'] = new_name
            else:
                acc = self.pool.get('account.account').browse(cr, uid, line_tuple[2]['account_id'], context=None)
                if acc and acc.type in ['receivable','payable']:
                    line_tuple[2]['operating_unit_id'] = invoice_browse.operating_unit_id.id

                if new_name.strip() == '':
                    line_tuple[2]['name'] = '/'

            new_move_lines.append(line_tuple)

        if invoice_browse.journal_id.code == 'VTANF':
            taxid = self.pool.get('account.tax').search(cr, uid, [('id', '=', TAXCODESALE['16'])], context=None)
            tax = self.pool.get('account.tax').browse(cr, uid, taxid, context=None)
            aml_ = [tax.account_reconcile_id.id,
                    tax.account_collected_id.id]

            taxes = round( invoice_browse.amount_total - (invoice_browse.amount_total / (1 + tax.amount)), 2)
            for i in range(2):

                header = {
                    'account_id': aml_[i],
                    'date': invoice_browse.date_invoice,
                    'name': invoice_browse.name,
                    'partner_id': invoice_browse.partner_id.id,
                    'debit': taxes if i == 0 else 0,
                    'credit': taxes if i == 1 else 0,
                    'operating_unit_id': invoice_browse.operating_unit_id.id,
                    'company_id': 1,
                }

                new_tuple = (0, 0, header)
                new_move_lines.append(new_tuple)

        return new_move_lines


# class AccountMoveLine(orm.Model):
#     _inherit = "account.move.line"
#
#     def create(self, cr, uid, vals, context=None, check=True):
#
#         if vals.get('move_id', False):
#             move = self.pool['account.move'].browse(cr, uid,
#                                                     vals['move_id'],
#                                                   context=context)
#
#             acc = self.pool.get('account.account').browse(cr,uid,vals['account_id'],context=context)
#             if acc.type in ['payable','receivable']:
#                 octx = context.copy()
#                 #ai = self.pool.get('account.invoice').search(cr,uid,[('internal_number','=',vals['name'])],context=context)
#                 vals['operating_unit_id'] = octx['invoice'].operating_unit_id.id
#             # else:
#             #     if move.operating_unit_id:
#             #         vals['operating_unit_id'] = move.operating_unit_id.id
#         return super(AccountMoveLine, self).create(cr, uid, vals,
#                                                    context=context,
#                                                    check=check)

