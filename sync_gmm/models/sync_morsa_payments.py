# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 OpenERP s.a. (<http://openerp.com>).
#
#    DME SOLUCIONES
#    David Alberto Perez Payan <david.perez@pcsystems.mx>
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
from __future__ import print_function

from openerp.osv import orm, fields
#from openerp import models, fields, api, exceptions, tools
from openerp.addons.web.controllers.main import Session
from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from datetime import datetime, timedelta
#from StringIO import StringIO
import openerp.netsvc
#import glob
#import os.path
import time
import psycopg2
import xmlrpclib
from openerp.tools.translate import _
import os
#log
import logging
import base64
import sync_conexion
#import zipfile
_logger = logging.getLogger(__name__)

COMPANY_ID_MOR = 1
ENTERPRISE = {'GMM':'culiacan', 'MOR':'mayoreo', 'VOH':'vohcom', 'desarrollo':'contpaq_morsa_desarrollo'}
JOURNALCODE = { '1':'MISC', '2':'GTOREP', '3':'ANTCI', '4':'GTOCOMP', '6':'GTOVIAT'}
PAYMENT_TYPE_CODE = '03'
CTAS_IVAS = {'IVAPORRECUPERAR': 1909, 'IVARECUPERADO': 1901}
TAXCODEID = {16: 66, 8: 107}
ACC_PROV_EXTRANJERO = 1995

class SyncMorsaPayment(models.Model):
    _name = 'sync.morsa.payments'


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

    enterprise = fields.Char(
            'Enterprise:',
            default=lambda self: self._get_enterprise_used(),
            help='Write the code for enterprise \nGMM: culiacan \nMOR: mayoreo \nVOH: vohcom\n Example: GMM',
        )

    ou = fields.Many2one(
                'operating.unit', 'Operating Unit:',
                domain=[('code', 'not ilike', '-')],
                required=True
        )

    expense_type = fields.Selection(
         string='Pagos de Gastos y Compras:',
         default='1',
         selection=[('1', '1-Normal (misceláneos)'),
                    ('7', '7-Compras a Proveedores')
                ]
    )

    conexion = ''
    paymentType = ''
    periodid = ''

    @api.multi
    @api.onchange('dFechaIni')
    def onchange_dFechaIni(self):
        self.dFechaFin = self.dFechaIni

        return

    @api.multi
    def action_sync_morsa_payments(self):

        self.dFechaFin = self.dFechaIni
        period = self.dFechaIni[5:7] + "/" + self.dFechaIni[0:4]
        #if period != self.dFechaFin[5:7] + "/" + self.dFechaFin[0:4]:
        #    raise UserError("El rango de fechas debe de estar dentro del mismo periodo:", period)

        self.periodid = self.env['account.period'].search([('code', '=', period)]).id

        if self.expense_type == '7':
            self._do_purchase_payments()
            return

        try:
            self._do_payments()
        except Exception as e:
            raise UserError("",repr(e))
        finally:
            self.conexion.close()


    def _do_payments(self):

        dbname = ENTERPRISE[self.enterprise]
        self.conexion = self.env['sync.morsa.conexion']._get_conexion("conexion_openerp_expense_newportal.csv", dbname)

        curpayment = self.conexion.cursor()
        query_payments = self._get_sql_payments()
        curpayment.execute(query_payments)
        records = curpayment.fetchall()


        if not records:
            raise UserError("There are not payments with the given parameters")


        # ctaprov               0
        # ctachq                1
        # num_prov              2
        # rfc                   3
        # fecha_pago            4
        # fecha_pago_real       5
        # sucprov               6
        # sat_cod               7
        # codigo_interno        8
        # bcobenefi             9
        # acreedor              10
        # partner_id            11
        # account_id            12
        # imppagado             13
        # folio			14

        try:
            obj_av = self.env['account.voucher']
            obj_invoice = self.env['account.invoice']
            obj_partner = self.env['res.partner']
            obj_payment_type = self.env['payment.type'].search([('code','=', PAYMENT_TYPE_CODE)])

            self.paymentType = obj_payment_type.id
            sql_update = ''
            partnerid = ''

            for record in records:

                if partnerid != record[11]:
                    partnerid = record[11]
                    partner = obj_partner.search([('id','=',partnerid)])
                    if not partner.vat_subjected:
                        partner.write( {'vat_subjected' : True })


                av_header = {
                    'partner_id'        : partnerid,
                    'amount'            : record[13],
                    'payment_type_id'   : self.paymentType,
                    'date'              : record[5],
                    'name'              : record[0],
                    'journal_id'        : self._get_journal(record).id,
                    'account_id'        : record[12],
                    'period_id'         : self.periodid,
                    'type'              : 'payment',
                    'voucher_operating_unit_id' : self.ou.id,
                    'company_id'        : COMPANY_ID_MOR,
                    'partner_bank_id'   : self._get_partner_bank_acc(record),
                    'pre_line': True,
                    }

                payment = obj_av.create(av_header)
                folios = self._do_detail_payments(payment.id,record[14])
                folios_to_affect = ','.join(map(str,folios))
                payment.write( { 'reference' : folios_to_affect } )
                sql_update += "update cxpgastos set erp = '2' where folio in (%s);"%(folios_to_affect)


            if sql_update:
                curpayment.execute(sql_update)
                self.conexion.commit()
        except Exception as e:
            raise e
        finally:
            curpayment.close()
            self.conexion.close()

    def _get_partner_bank_acc(self, record):

        bank_acc_id = ''
        obj_bank_acc = self.env['res.partner.bank'].search([('partner_id','=',record[11]),
                                                            ('acc_number','=',record[0])])
        if not obj_bank_acc:
            bank = ''
            if record[7]:
                obj_bank = self.env['res.bank'].search([('sat_code','=',record[7])])
                bank = obj_bank.id

            clabeok = record[0]
            if len(clabeok) != 18:
                clabeok = ''

            data = {
                'state': 'bank',
                'partner_id': record[11],
                'acc_number': record[0],
                'clabe': clabeok,
                'last_acc_number': record[0][-4:],
                'bank': bank,
                'bank_name': record[9],
                'reference': record[8],
            }
            bank_acc = obj_bank_acc.create(data)
            bank_acc_id = bank_acc.id
        else:
            bank_acc_id = obj_bank_acc.id

        return bank_acc_id

    def _get_journal(self, record):

        journalcode = record[8] + record[1][-4:]
        obj_journal = self.env['account.journal'].search([('code','=',journalcode)])
        journal = obj_journal
        journalid = obj_journal.id

        if not journalid:
            data = {
                'name'      : record[8] + ' ' + record[1],
                'prefix'    : journalcode + '/%(y)s%(month)s/',
                'padding'   : 5,
                'number_next_actual': 1,
                'number_increment' : 1,
                'implementation' : 'standard'

            }
            sequence = self.env['ir.sequence'].create(data)

            data = {
                'name' : record[8] + ' ' + record[1],
                'code' : journalcode,
                'type' : 'bank',
                'payment_type_id' : self.paymentType,
                'default_debit_account_id' : record[12],
                'default_credit_account_id': record[12],
                'update_posted' : True,
                'sequence_id': sequence.id
            }
            journal = obj_journal.create(data)
            journalid = journal.id

        return journal

    def _do_detail_payments(self,payment_id,folio):

        folios = []
        obj_avl = self.env['account.voucher.line']

        curinvoicepay = self.conexion.cursor()
        query_detpayments  = self._get_sql_detail_payments(folio)
        curinvoicepay.execute(query_detpayments)
        records = curinvoicepay.fetchall()

        folios.append(folio)
        for record in records:

            ai = self.env['account.invoice'].search([('id', '=', record[7])])
            aml = self.env['account.move.line'].search([('move_id', '=', ai.move_id.id),
                                                        ('account_id', '=', ai.account_id.id)])

            tipomovto = 'dr'
            if ai.type == 'in_refund':
                tipomovto = 'cr'

            importe = aml.amount_residual
            importe_invoice = ai.residual
            if aml:
                avl_header = {
                        'voucher_id'        : payment_id,
                        'move_line_id'      : aml.id,
                        'account_id'        : aml.account_id.id,
                        'reconcile'         : True,
                        'amount_original'   : importe,
			            'amount_unreconciled': importe,
                        'type'              : tipomovto,
                        'company_id'        : COMPANY_ID_MOR,
                    }

                avl = obj_avl.create(avl_header)
                if avl:
                    avlid = avl.id
                    avl = obj_avl.search([('id', '=', avlid)])
                    if avl.amount_unreconciled == 0 or avl.amount == 0:
                        avl.write({'amount_unreconciled': importe_invoice, 'amount': importe_invoice,})



        return folios

    def _get_sql_payments(self):

        sql = ("""SELECT trim(g.cuentabanco) AS CtaProv, trim(ch.cuenta) AS CtaChq, p.num_prov, trim(p.rfc) rfc, g.fechapago AS fecha_pago, 
		            (left(g.ref_pago,4) || '-' || substring(ref_pago from 5 for 2) || '-' || right(ref_pago,2))::date fecha_pago_real, 
		            suc.codigo_erp AS SucProv, trim(b.sat_cod) sat_cod,  trim(b2.codigo_interno) codigo_interno, 
		            trim( b.nombre ) AS BcoBenefi,  trim(g.acreedor) acreedor, rfcs.id partner_id, scor.id_open account_id, 
		             g.importe AS ImpPagado, g.folio
                FROM cxpgastos g INNER JOIN AcreCtas p ON g.acreedor = p.acreedor 
		                        INNER JOIN cuentacont cc ON g.acreedor = cc.cuenta 
		                        INNER JOIN cxcctaspag ch ON g.banco = ch.numero 
		                        INNER JOIN cxcbancos b ON p.banco = b.banco 
		                        INNER JOIN cxcbancos b2 ON ch.banco = b2.banco 
		                        inner join cat_sucursales suc on suc.num_suc = g.sucursal
		                        left join openerp_get_rfcs() rfcs on p.rfc = rfcs.rfc_sat
		                        left join fn_scor() scor on (ch.ctacon_bco=replace(scor.c_contpaq,'-',''))
                WHERE %s
                order by (left(g.ref_pago,4) || '-' || substring(ref_pago from 5 for 2) || '-' || right(ref_pago,2))::date,
               		g.folio,  rfc, partner_id;""")%(self._get_where_clause())

        return sql

    def _get_sql_detail_payments(self, folio):

        sql = ("""
                select distinct g.folio, g.fecha, g.ref_pago, g.fechaprog, g.fechapago,
	                dg.id_prov,  dg.folio_fiscal, dg.invoice_id, g.importe
                from cxpgastos g inner join cxpdetallegastos dg on (dg.folio = g.folio)
                where  dg.folio = %s
                order by dg.invoice_id;
              """) % folio

        return sql

    def _get_where_clause(self, rangoFechas=True):
        #g.estatus = '4' and g.fecha >= '2019-01-01' and g.tipo = '1' and g.pagar = '1'

        ctipogasto = self.expense_type
        sqlwhere = """(g.estatus ='4' and pagar='1' and g.fecha >= '2019-01-01')"""
        if rangoFechas:
            sqlwhere = ("""g.erp = '1' and g.tipo = '%s' and %s and suc.codigo_erp = %s 
                        and (left(g.ref_pago,4) || '-' || substring(ref_pago from 5 for 2) || '-' || right(ref_pago,2))::date 
                                between '%s' AND '%s' """)%\
                       (ctipogasto, sqlwhere, int(self.ou.code), self.dFechaIni, self.dFechaFin)
        else:
            sqlwhere = ("""g.tipo = '%s' and  dg.id_sucursal_erp = %s and pagar = '1' """)%(ctipogasto,int(self.ou.code))

        return sqlwhere

    def _do_purchase_payments(self):
        dbname = ENTERPRISE[self.enterprise]
        conexion = self.env['sync.morsa.conexion']._get_conexion("conexion_openerp_expense_newportal.csv", dbname)

        payment = self.env['gmm.cfdi.supplier.payment']
        payment_line = self.env['gmm.cfdi.supplier.payment.line']
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)
        #crssuppliers = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)
        #crspurchases = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(self._get_sql_data('supplier'))
        suppliers = cursor.fetchall()
        if not suppliers:
            raise UserError("There are not Purchases Payments within the given parameters")

        obj_am = self.env['account.move']
        obj_aml = self.env['account.move.line']
        obj_partner = self.env['res.partner']
        obj_ou = self.env['operating.unit']
        company = self.env['res.company'].search([('id', '=', COMPANY_ID_MOR)])
        journalcur = ''
        paiddate = ''
        am = ''
        journalid = ''
        msgdata = ''
        sql_update = ''

        try:
            for supplier in suppliers:
                #query_payments = self._get_purchasespayments_sql(False, supplier['num_prov'])
                #crspurchases.execute(query_payments)
                #records = crspurchases.fetchall()
    #            period = self.dFechaIni[5:7] + "/" + self.dFechaIni[0:4]
    #            ap = self.env['account.period'].search([('code','=',period)])

                partnerid = ''
                msgdata = ''
                oucode = ''
                ou = ''
                imppagado = 0
                depositadoen = ''

                ivapagadocur = 0
                ivaporpagarcur = 0
                imppagadocur = 0
                descuentoscur = 0
                importecur = 0

                ivapagado = 0
                ivaporpagar = 0
                imppagado = 0
                descuentos = 0
                importe = 0

                partnerid = supplier['partner_id'] or supplier['id_partner']
                partner = obj_partner.search([('id', '=', partnerid)])
                if not partner.vat_subjected:
                    partner.write({'vat_subjected': True})

                ctacosto = supplier['acc_id_descuento'] or 2184
                depositadoen = supplier['cuenta_banco'] or '/'

                msgdata = 'RFC: ' + partner.vat[2:] + "(%s). " % partner.id
                paiddate = self.dFechaIni

                journal = self._get_journal(supplier)
                journalcur = journal.currency
                if not journalcur:
                    journalcur = company.currency_id
                journalid = journal.id
                #ENCABEZADO
                header = {
                    'partner_id'        : partnerid,
                    'date'              : paiddate,
                    'ref'               : 'Pagado el: ' + paiddate,
                    'journal_id'        : journalid,
                    'company_id'        : COMPANY_ID_MOR,
                    'period_id'         : self.periodid,
                    'narration'         : str(supplier['num_prov']) + '. Depositado a la cuenta: ' + depositadoen
                    }
                am = obj_am.create(header)
                invoices = []
                whereprov = 'f.num_prov = %s and ' % supplier['num_prov']
                cursor.execute(self._get_sql_data('ou', whereprov))
                branches = cursor.fetchall()
                for branch in branches:
                    ou = obj_ou.search([('code', '=', branch['ou_code'])])
                    whereou = whereprov + 'f.num_suc = %s and ' % branch['num_suc']
                    cursor.execute(self._get_sql_data('folio', whereou))
                    folios = cursor.fetchall()
                    for folio in folios:
                        where = whereprov + whereou + 'fg.folio = %s and ' % folio['folio']

                # cuenta_banco          0
                # cuenta                1
                # acc_id_descuento      2
                # num_prov              3
                # num_suc               4
                # folio                 5
                # fecha_pago            6
                # sat_code              7
                # codigo_interno        8
                # ctacon_bco            9
                # banknombre            10
                # partner_id            11
                # acc_id_cheque         12
                # id_partner            13
                # rfc                   14
                # succode               15
                # ctacon_pp             16
                # ctacon_vol            17
                # ctacon_adi            18
                # ctacon_ncr            19
                # ctacon_mer            20
                # importe               21
                # impiva                22
                # impdescuentos         23
                # imppagado             24
                # ivapagado             25

                        msgdata = 'RFC: ' + partner.vat[2:] + ' Folio: ' + str(folio['folio']) + ". "
                        cursor.execute(self._get_sql_data('purchase', where))
                        records = cursor.fetchall()
                        paidamount = 0
                        amountcurrency = 0
                        print("Pagando: %s en sucursal %s" % (msgdata, branch['num_suc']))
                        for record in records:
                            paidamount += journalcur.with_context(
                                date=paiddate).compute(record[21], company.currency_id)
                            amountcurrency += record[21]
                            ivapagadocur += record[25]
                            ivaporpagarcur += record[22]
                            imppagadocur += record[24]
                            descuentoscur += record[23]
                            importecur += record[21]

                            ivapagado += journalcur.with_context(
                                date=paiddate).compute(record[25], company.currency_id)
                            ivaporpagar += journalcur.with_context(
                                date=paiddate).compute(record[22], company.currency_id)
                            imppagado += journalcur.with_context(
                                date=paiddate).compute(record[24], company.currency_id)
                            descuentos += journalcur.with_context(
                                date=paiddate).compute(record[23], company.currency_id)

                            invoices.append(
                                {'serie': record['serie'].strip(),
                                 'foliofact': record['foliofact'],
                                 'foliofiscal': record['foliofiscal'].strip().upper(),
                                 'importe': record['importe'],
                                 'anterior': record['importe'],
                                 'pagado': record['imppagado'],
                                 'imppagado': record['imppagado'],
                                 'pendiente': record['importe'] - record['imppagado'],
                                 'invoice_id': record['invoice_id'] if record['invoice_id'] > 0 else False
                                 })

                        importe += paidamount
                        if journalcur.id == company.currency_id.id:
                            msgdata += "Cuenta Contable: " + partner.property_account_payable.code + " " + \
                                            partner.property_account_payable.name
                            header = {'account_id': partner.property_account_payable.id}
                        else:
                            msgdata += "Cuenta Contable: 211-1-3 Proveedores - Extranjeros"
                            header = {'amount_currency': amountcurrency,
                                      'currency_id': journalcur.id,
                                      'account_id': ACC_PROV_EXTRANJERO,
                                      }

                        header.update(
                            {'partner_id': partnerid,
                             'name': str(folio['folio']),
                             'date': paiddate,
                             'journal_id': journalid,
                             'debit': paidamount,
                             'credit': 0,
                             'operating_unit_id': ou.id,
                             'company_id': COMPANY_ID_MOR,
                             'period_id': self.periodid,
                             'move_id': am.id})
                        aml = obj_aml.create(header)
                sql_update = "OK"
                acctax = ''
                basetax = ''
                taxrate = int(round((ivapagado / (imppagado - ivapagado)), 2) * 100)
                if taxrate >= 15 and taxrate <= 17:
                    taxrate = 16

                if taxrate in TAXCODEID.keys():
                    acctax = TAXCODEID[taxrate]
                    basetax = imppagado - ivapagado

                print("Data: %s" % msgdata)
                aml_ = [
                    ['/', CTAS_IVAS['IVAPORRECUPERAR'], 0.0, ivaporpagar, '', '', -ivaporpagarcur],
                    [depositadoen, journal.default_debit_account_id.id, 0.0, imppagado, '', '', -imppagadocur, False],
                    ['/', CTAS_IVAS['IVARECUPERADO'], ivapagado, 0.0, acctax, basetax, ivapagadocur],
                    ['/', ctacosto, 0.0, (importe + ivapagado) - (ivaporpagar + imppagado), '', '',
                     -((importecur + ivapagadocur) - (ivaporpagarcur + imppagadocur)), False]
                ]

                for i in range(4):
                    if round(aml_[i][2], 2) == 0.0 and round(aml_[i][3], 2) == 0.0:
                        continue

                    cuenta = 'Cuenta: ' + str(aml_[i][1])
                    header = {
                        'partner_id': partner.id,
                        'name': aml_[i][0],
                        'journal_id': journalid,
                        'account_id': aml_[i][1],
                        'debit': aml_[i][2],
                        'credit': aml_[i][3],
                        'operating_unit_id': self.ou.id,
                        'company_id': COMPANY_ID_MOR,
                        'period_id': self.periodid,
                        'tax2_id': aml_[i][4],
                        'tax2_base': aml_[i][5],
                        'tax2_base_company_currency': aml_[i][6],
                        'move_id': am.id
                    }
                    if journalcur.id != company.currency_id.id:
                        header.update(
                            {'amount_currency': aml_[i][6],
                             'currency_id': journalcur.id,
                             }
                        )
                    aml = obj_aml.create(header)
                    if len(aml_[i]) > 7:
                        aml_[i][7] = aml.id

                pay_info = {
                    'partner_id': partner.id,
                    'serie': False,
                    'number': False,
                    'uuid': aml_[1][7],
                    'date': False,
                    'amount': False,
                    'company_paid_date': paiddate,
                    'state': 'draft',
                    'name': 'SIN PAGO'
                }

                paymentid = payment.create(pay_info)
                pay_info = {'payment_id': paymentid.id,
                            'move_line_id': aml_[1][7],
                            'type': 'payment',
                            'concilied': True
                            }
                payment_line.create(pay_info)
                pay_info = {'payment_id': paymentid.id,
                            'move_line_id': aml_[3][7],
                            'type': 'credit',
                            'concilied': False
                            }
                payment_line.create(pay_info)
                paymentid.add_invoices_paid(conexion, invoices, True)
                paymentid.add_credits_used(conexion, paiddate, paiddate, True)

            #if sql_update:
                #sql_update = self._get_purchasespayments_sql(True)
                #cursor.execute(sql_update)
                #conexion.commit()
        except Exception as e:
            sql_update = False
            if msgdata:
                msgdata += "\n" + repr(e)
                raise UserError("Error procesando Pagos de Compras\n", msgdata)
            else:
                raise e
        finally:
            conexion.close()

        return

    def _get_purchasespayments_sql(self, update=False, supplier=None):

        if update:
            sql_purchasepayments = ("""
                update cxpfacturas set erp = '2' 
                where (erp is null or erp <> '2') and estatus_f = '5' and fec_venc3 > 0 and 
                    to_date(fecha_pago::text, 'YYYYMMDD') BETWEEN '%s'  and '%s'
                    """) % (self.dFechaIni, self.dFechaIni)

            return sql_purchasepayments

        sql_purchasepayments=("""
            SELECT trim(p.cuenta_banco) cuenta_banco, trim(ch.cuenta) cuenta, scordcto.id_open acc_id_descuento, 
                f.num_prov, f.num_suc, fg.folio, f.fecha_pago, trim(bank.sat_cod) sat_code, 
                trim(bank.codigo_interno) codigo_interno, trim(ch.ctacon_bco) ctacon_bco,  trim(bank.nombre) banknombre, 
                rfcs.id partner_id, scorbco.id_open acc_id_cheque, scorprov.id_partner, replace(trim(p.rfc),'-','') rfc,
                lpad(suc.codigo_erp::text, 2, '0') succode, 
                p.ctacon_pp, p.ctacon_vol, p.ctacon_adi, p.ctacon_ncr, p.ctacon_mer,
                round( importe-devolucion-faltante_real, 02) Importe, 
                round( (importe+iva2010-devolucion-faltante_real) -  ((importe+iva2010-devolucion-faltante_real)/(1+(f.iva/100))), 02) ImpIva,
                round( (saldo_notas + p_promocion + n_cargo + anticipo + saldo_desctos + faltante - faltante_real)/(1+(f.iva/100)), 02) Impdescuentos,
                round( importe - (saldo_notas + p_promocion + n_cargo + anticipo + saldo_desctos + devolucion + faltante), 02) ImpPagado,
                round( ( (importe - (saldo_notas + p_promocion + n_cargo + anticipo + saldo_desctos + devolucion + faltante )) - 
                      (importe - (saldo_notas + p_promocion + n_cargo + anticipo + saldo_desctos + devolucion + 
                      faltante))/(1+(f.iva/100))), 02) IvaPagado,
                f.serie, f.foliofact, f.invoice_id, trim(upper(cfdi.foliofiscal)) foliofiscal
            FROM cxpfacturas f 
                    INNER JOIN cxpproveedores p ON f.num_prov = p.num_prov
                    INNER JOIN cat_sucursales s ON f.num_suc = s.num_suc
                    INNER JOIN foliosgen fg ON (f.num_prov = fg.num_prov AND f.fec_venc = fg.fecha_ven )
                    INNER JOIN cxcctaspag ch ON (f.fec_venc3 = ch.numero)
                    inner join cxcbancos bank on (bank.banco = ch.banco)
                    inner join cat_sucursales suc on (f.num_suc=suc.num_suc)
                    left join openerp_get_rfcs() rfcs on (replace(trim(p.rfc),'-','') = rfcs.rfc_sat)
                    left join fn_scor() scorprov on (trim(p.cta_prov) = replace(scorprov.c_contpaq,'-',''))
                    left join fn_scor() scorbco on (ch.ctacon_bco = replace(scorbco.c_contpaq, '-',''))
                    left join fn_scor() scordcto on (coalesce(p.ctacon_pp, p.ctacon_vol, p.ctacon_adi, 
                            p.ctacon_ncr, p.ctacon_mer)=replace(scordcto.c_contpaq,'-',''))
                    left join swpr_cfdcomprobanteproveedor cfdi on ( trim(cfdi.emirfc) = rfcs.rfc_sat  
	                	and cfdi.folio=f.foliofact and cfdi.serie=f.serie)
            WHERE f.num_prov = %s and 
                (erp is null or erp <> '2') and estatus_f = '5' and 
                f.fec_venc3 > 0 and 
                to_date(f.fecha_pago::text, 'YYYYMMDD') = '%s' and 
                (importe-devolucion) > 0
            order by f.fecha_pago, f.num_prov, num_suc, folio;
                        """) % (supplier, self.dFechaIni)

        return sql_purchasepayments

    def _get_sql_data(self, getdata, swhere=''):

        data = { 'supplier':
                     { 'sql':
                           """  trim(p.cuenta_banco) cuenta_banco, trim(ch.cuenta) cuenta, 
				                scordcto.id_open acc_id_descuento, 
                                f.num_prov, 0 num_suc, 0 folio, f.fecha_pago, trim(bank.sat_cod) sat_code, 
                                trim(bank.codigo_interno) codigo_interno, trim(ch.ctacon_bco) ctacon_bco,  
                                trim(bank.nombre) banknombre, 
                                rfcs.id partner_id, scorbco.id_open acc_id_cheque, 
                                scorprov.id_partner, replace(trim(p.rfc),'-','') rfc
                            """,
                       'group': '4, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15'
                       },
                 'ou': {'sql': "f.num_suc, lpad(f.num_suc::varchar, 2, '0') ou_code",
                        'group': '1, 2',
                        },
                 'folio':
                     { 'sql': 'fg.folio',
                       'group': '1'
                       },
                 'purchase':
                     { 'sql':
                           """trim(p.cuenta_banco) cuenta_banco, trim(ch.cuenta) cuenta, scordcto.id_open acc_id_descuento, 
                            f.num_prov, f.num_suc, fg.folio, f.fecha_pago, trim(bank.sat_cod) sat_code, 
                            trim(bank.codigo_interno) codigo_interno, trim(ch.ctacon_bco) ctacon_bco,  trim(bank.nombre) banknombre, 
                            rfcs.id partner_id, scorbco.id_open acc_id_cheque, scorprov.id_partner, replace(trim(p.rfc),'-','') rfc,
                            lpad(suc.codigo_erp::text, 2, '0') succode, 
                            p.ctacon_pp, p.ctacon_vol, p.ctacon_adi, p.ctacon_ncr, p.ctacon_mer,
                            round( importe-devolucion-faltante_real, 02) Importe, 
                            round( (importe+iva2010-devolucion-faltante_real) -  ((importe+iva2010-devolucion-faltante_real)/(1+(f.iva/100))), 02) ImpIva,
                            round( (saldo_notas + p_promocion + n_cargo + anticipo + saldo_desctos + faltante - faltante_real)/(1+(f.iva/100)), 02) Impdescuentos,
                            round( importe - (saldo_notas + p_promocion + n_cargo + anticipo + saldo_desctos + devolucion + faltante), 02) ImpPagado,
                            round( ( (importe - (saldo_notas + p_promocion + n_cargo + anticipo + saldo_desctos + devolucion + faltante ) - 
                                  (importe - (saldo_notas + p_promocion + n_cargo + anticipo + saldo_desctos + devolucion + faltante))/(1+(f.iva/100)))
                                ), 02) IvaPagado,
                            f.serie, f.foliofact, f.invoice_id, cfdi.foliofiscal
                           """,
                       'order': 'f.fecha_pago, f.num_prov, num_suc, folio'
                     }
                 }

        groupby = ''
        orderby = ''
        if 'group' in data[getdata]:
            groupby = 'group by %s ' % data[getdata]['group']
            orderby = 'order by %s ' % data[getdata]['group']
        else:
            groupby = ''
            orderby = 'order by %s' % data[getdata]['order']

        sql = """
            SELECT %s
            FROM cxpfacturas f 
                    INNER JOIN cxpproveedores p ON f.num_prov = p.num_prov
                    INNER JOIN cat_sucursales s ON f.num_suc = s.num_suc
                    INNER JOIN foliosgen fg ON (f.num_prov = fg.num_prov AND f.fec_venc = fg.fecha_ven )
                    INNER JOIN cxcctaspag ch ON (f.fec_venc3 = ch.numero)
                    inner join cxcbancos bank on (bank.banco = ch.banco)
                    inner join cat_sucursales suc on (f.num_suc=suc.num_suc)
                    left join openerp_get_rfcs() rfcs on (replace(trim(p.rfc),'-','') = rfcs.rfc_sat)
                    left join fn_scor() scorprov on (trim(p.cta_prov) = replace(scorprov.c_contpaq,'-',''))
                    left join fn_scor() scorbco on (ch.ctacon_bco = replace(scorbco.c_contpaq, '-',''))
                    left join fn_scor() scordcto on (coalesce(p.ctacon_pp, p.ctacon_vol, p.ctacon_adi, 
                            p.ctacon_ncr, p.ctacon_mer)=replace(scordcto.c_contpaq,'-',''))
                    left join swpr_cfdcomprobanteproveedor cfdi on ( trim(cfdi.emirfc) = rfcs.rfc_sat  
	                	and cfdi.folio=f.foliofact and cfdi.serie=f.serie)
            WHERE %s f.num_prov = 43 and 
                    (erp is null or erp != '2') and estatus_f = '5' and f.fec_venc3 > 0 and 
                    to_date(f.fecha_pago::text, 'YYYYMMDD') = '%s'  
            %s 
            %s;
        """ % (data[getdata]['sql'], swhere, self.dFechaIni, groupby, orderby)

        return sql