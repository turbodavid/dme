# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 OpenERP s.a. (<http://openerp.com>).
#
#    DME SOLUCIONES
#    David Alberto Pérez Payán <david.perez@pcsystems.mx>
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

import openerp.addons.decimal_precision as dp
from openerp import api, fields, models
import psycopg2
from openerp.tools.translate import _
import logging
import base64
from datetime import datetime
from openerp.addons.web.controllers.main import Session
from openerp.exceptions import Warning as UserError
from decorator import append

_logger = logging.getLogger(__name__)

COMPANY_ID_MOR = 1
ENTERPRISE = {'GMM':'culiacan', 'MOR':'mayoreo', 'VOH':'vohcom', 'desarrollo':'contpaq_morsa_desarrollo'}
JOURNALCODE = {'0':'CMPNAC', '1':'CMPNACUS', '2':'CMPUS'}
TAXCODEPURCHASE = {'16': 53, '8': 69}
TAXCODESALE = {'16': 50, '8': 69}
CURRENCY_ID = {'0': 34, '1': 3}
PAYMENT_TYPE_CODE = '03'
ID_CTA_IVA_POR_PAGAR = 2071
SPECIALS_ACCOUNTS = {'500': '', '510': 2299, '520': 2305, '530': 2291}
DEFAULT_UNIT_ID = 318
DEFAULT_UNIT_CODE = '01'

class sync_morsa_incomes(models.Model):
    _name = 'sync.morsa.incomes'


    def _get_enterprise_used(self):

        sesion = Session()
        informacion = sesion.get_session_info()
        bd = informacion.get('db')

        return bd[0:3]

    enterprise = fields.Char(
         'Enterprise:',
         default=lambda self: self._get_enterprise_used(),
         help='Write the code for enterprise \nGMM: culiacan \nMOR: mayoreo \nVOH: vohcom\n Example: GMM',
                )

    date_stop = fields.Date(
        'Fecha Final',
        default = fields.Date.today(),
        required=True,
        help='Considerar pagos de clientes hasta este día',
    )

    date_start = fields.Date(
        'Fecha Inicial:',
        default=fields.Date.today(),
        required=True,
        help='Considerar pagos de clientes a partir de este día',
    )

    journal_income_id = fields.Many2one(
        'account.journal',
        'Diarios de Ingresos',
        required=True,
        domain=[('type', '=', 'bank')],
        help='Diario Ingresos/Pagos de Cliente',
    )

    # acc_income_id = fields.Many2one(
    #             'account.account',
    #             'Cuenta Ingresos',
    #             default=164,
    #             required=True,
    #             domain=[('user_type', '=', 4), ('type', '!=', 'view')],
    #             help='Cuenta para Ingresos/Pagos de Cliente',
    # )

    acc_relative_partner = fields.Many2one(
                'account.account',
                'Cuenta Partes Relacionadas',
                default=1869,
                required=True,
                domain=[('user_type', 'like', '112'), ('type', '!=', 'view')],
                help='Cuenta para Ingresos/Pagos de Cliente',
    )

    acc_benefit_id = fields.Many2one(
            'account.account',
            'Cuenta Bonifaciones',
            default=2163,
            required=True,
            domain=[('code', 'like', '410-2'), ('type', '!=', 'view')],
            help='Cuenta para Descuentos y Bonificaciones de Clientes'
    )

    acc_refund_id = fields.Many2one(
            'account.account',
            'Cuenta Devoluciones',
            default=2162,
            required=True,
            domain=[('code', 'like', '410-2'), ('type', '!=', 'view')],
            help='Cuenta para Devoluciones de Clientes'
    )

    ou = fields.Many2one(
                'operating.unit', 'Operating Unit:',
                domain=[('code', 'not ilike', '-')],
        )

    only_process = fields.Boolean('Solo Procesar')

    move_type = fields.Selection(
         string='Tipo de Movimiento:',
         default='500',
         selection=[('500', '500-Ingresos Normales'),
                    ('510', '510-Cuentas Incobrables'),
                    ('520', '520-Caso Fortuito'),
                    ('530', '530-Incobrables No Deducibles'),
                ]
    )

    acc_debit_receivable = fields.Many2one(
            'account.account',
            'Cuenta de Contrapartida',
            help='Cuenta de Cargo para contrapartida del Movimiento')

    journal_special_id = fields.Many2one(
        'account.journal',
        'Diario para el Movimiento',
        domain=[('type', '!=', 'bank')],
        help='Diario dónde se registrará el Movimiento Especial',
    )

    conexion = ''
    period = ''
    msgErr = ''
    solo_aplicar = False
    ir_attach = ''
    ir_attach_fe = ''
    aml = ''
    credits = ''
    av = ''
    avl = ''
    oldaml = ''
    oldamlpr = ''
    residual = ''
    currentoldaml = 0
    currentoldamlpr = 0
    refundsused = ''
    movesused = ''
    paymenttype = ''
    movesresidual = {}

    @api.multi
    @api.onchange('only_process')
    def onchange_onlyprocess(self):

        if not self.only_process:
            self.move_type = '500'

        return {}

    @api.onchange('move_type')
    def onchange_move_type(self):

        self.acc_debit_receivable = SPECIALS_ACCOUNTS[self.move_type]
        domain = {'acc_debit_receivable': [('user_type.code', '=', 'expense'), ('code', 'like', '610-')]}
        invisible = {'acc_debit_receivable': [('only_process', '=', False), ('move_type', '=', '500')]}

        return {'domain': domain, 'invisible': invisible}

    @api.multi
    def action_sync_incomes(self):

        sql = ''
        self.period = self.date_start[5:7] + "/" + self.date_stop[0:4]
        try:
            if self.only_process:
                if self.move_type == '500':
                    self._create_payments()
                else:
                    self._create_special_moves()
            else:
                #self.conexion = self.env['sync.morsa.conexion']._get_conexion_direct(self.ou.ip_address,
                #                                                                     self.ou.data_base)
                self._create_incomes()
                self.conexion.commit()
        except Exception as e:
            raise
        finally:
            if self.conexion:
                self.conexion.close()

        return

    def _create_incomes(self):

        domain = [
            ('code', '=', self.period),
            ('company_id', '=', COMPANY_ID_MOR)
            ]

        period_id = self.env['account.period'].search(domain)
        income_obj = self.env['sync.morsa.refunds']
        msgErr = ''
        ouid = self.ou.id if self.ou.code != '99' else DEFAULT_UNIT_ID
        crsincomes = ''

        try:
            #if self.solo_aplicar:
            income_obj.create_refunds('out_invoice',
                                      'date_refund, num_mov, refund_number_serie, refund_number, refund_uuid')
            return
            #else:
              ##    income_obj.create_table_erpid(self.ou)
               #    crsincomes = self.conexion.cursor()
               #    crsincomes.execute(self._get_sql_incomes())
        except Exception as err:
            if crsincomes and crsincomes.rowcount > 0:
                crsincomes.rollback()
            raise

        maxtoprocess = 0
        incomes = crsincomes.fetchall()
        sql = ''

        if len(incomes) == 0:
            if income_obj.create_refunds('out_invoice',
                                       'date_refund, num_mov, refund_number_serie, refund_number, refund_uuid',
                                         ouid):
                return
            raise UserError("No existen registros de Ingresos o Notas de Cŕedito con los parametros proporcionados")

        income_id = self.id

        for income in incomes:

            msgdocto = ''
            haserror = False
            tipomov = income[7]

            maxtoprocess += 1
            #print "Proceso: %s, Movto: %s, Refund: %s,  Rfc: %s, Amount: %s" % (maxtoprocess, tipomov, income[13], income[3], income[17])

            dictincome = {
                'sync_morsa_incomes_id': income_id,
                'invoice_type': 'in_payment' if 500 <= tipomov <= 599 else 'out_invoice',
                'partner_id_internal': income[1],
                'partner_id_internal_socio': income[2],
                'partner_vat': income[3],
                'partner_id': self.ou.partner_id.id,
                'state': 'draft',
                'invoice_id': income[9] if income[9] > 0 else '',
                'invoice_uuid': income[12],
                'date_refund': income[5],
                'amount_untaxed': income[18],
                'amount_total': income[17],
                'amount_taxes': income[17] - income[18],
                'refund_ref': income[13],
                'invoice_number': income[10],
                'invoice_number_serie': income[11],
                'refund_number': income[13],
                'refund_number_serie': income[14].strip(),
                'refund_uuid': income[15],
                'xmlfile': income[16], #self._checking_characters(income[16]),
                'comment': income[19].strip(),
                'operating_unit_id': ouid,
                'num_mov': income[7],
                'id_kardex': income[8],
                'acc_relative_partner_id': self.acc_relative_partner.id if income[20] == 'S' else '',
                'journal_id': income[21],
                'folio_ingreso': income[22]
            }
            # SE CREA LA INFORMACIÓN DE INGRESO/NOTA DE CREDITO
            income_obj = income_obj.create(dictincome)
            sql += "insert into erpid values (%s, %s, 'cxckardex', 'sync_morsa_refunds'); " \
                       % (income[8], income_obj.id)
            #maxtoprocess -= 1
            # except Exception as err:
            #     raise UserError(repr(err))

        if sql:
            crsincomes.execute(sql)

        #income_obj.create_refunds('out_invoice',
        #                          'date_refund, num_mov, refund_number_serie, refund_number, refund_uuid',
        #                          ouid)

        return

    def _get_sql_incomes(self):
        #sucursal	    0
        #numcte	        1
        #numsocio   	2
        #rfc            3
        #fecha_gen	    4
        #fechadoc	    5
        #invoice_date	6
        #tipomov        7
        #id_kar	        8
        #invoice_id	    9
        #invoice_number	10
        #invoice_serie	11
        #invoice_uuid	12
        #referencia	    13
        #serie	        14
        #folio_fiscal	15
        #xmlfile	    16
        #importe	    17
        #impsiniva	    18
        #concepto       19
        #parte_rel      20
        #diario         21
        #folio_ingreso  22

        where = "where k.importe > 0.04 and k.tipomov in (500, 510, 520, 530, " \
                            "605, 610, 618, 619, 620, 630, 640, 650, 660, " \
                            "710, 720, 730, 740, 750) and k.estatus = 'V' " \
                  "and to_date( k.fechadoc::text, 'YYYYMMDD' ) between '%s' and '%s' " \
                  "and k.id_kar not in (select id from erpid where tabla = 'cxckardex')" \
                % (self.date_start, self.date_stop)

        if self.ou and self.ou.code != '99':
            where += " and k.sucursal = %s " % int(self.ou.code)

        sql = """
            select k.sucursal, k.numcte, k.numsocio, cli.rfc, k.fecha_gen, 
                    to_date( k.fechadoc::text, 'YYYYMMDD' ) fechadoc, 
                    to_date( f.fechadoc::text, 'YYYYMMDD' )invoice_date, 
                    k.tipomov, k.id_kar, f.invoice_id, k.numdocto invoice_number, trim(k.seriedoc) invoice_serie, upper(cfdif.folio_fiscal) invoice_uuid,
                    k.referencia, trim(k.serie) serie, upper(cfdi.folio_fiscal) folio_fiscal, regexp_replace(cfdi.cfdi_xml, '[^\x20-\x7f\x0d\x1b]', ' ', 'g') xmlfile,
                    k.importe, round( k.importe / (1+ (k.iva/100)), 2) impsiniva, k.concepto, cli.parte_rel, 
                    coalesce( dep.diario, 621) diario, k.folio_ingreso
            from cxckardex k
                    left join cxcfacturas f on (trim(k.seriedoc)=trim(f.serie) and k.numdocto = f.numdocto  and k.tipomov2=f.tipomov)
                    left join cxcclientes cli on (k.numcte = cli.numcte)
                    left join cfdi_sellado cfdi on (trim(k.serie) = trim(cfdi.serie) and k.referencia=cfdi.numdocto)
                    left join cfdi_sellado cfdif on (trim(f.serie) = trim(cfdif.serie) and f.numdocto=cfdif.numdocto)
                    left join cxcctasdep dep on (k.cta_ingreso = dep.numero)           
            """ + where + \
            """
            order by k.fechadoc, k.tipomov, k.numcte, k.serie, k.referencia, cfdi.folio_fiscal, k.seriedoc, k.numdocto
	        limit 500;
            """
        return sql

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
                elif x == u'\x91':
                    x = ''
                elif x == u'\x93':
                    x = ''
                elif x == u'\x9a':
                    x = ''
                elif x == u'\x9c':
                    x = ''
                nueva_cadena = nueva_cadena + x
                #print"TTTTTTTTTTTTTTTT", nueva_cadena
        if nueva_cadena == '':
            nueva_cadena = str(cadena)
        return nueva_cadena

    def _create_payments(self):

        domain = [
            ('invoice_type', '=', 'in_payment'),
            ('num_mov', '=', 500),
            ('state', '=', 'draft'),
            #('date_refund', '>=', self.date_start),
            #('date_refund', '<=', self.date_stop),
            # ('refund_number', 'in', ['1666', '1669', '1670', '1676']),
            # ('refund_number_serie', '=', 'CCNLTHP'),
            ]

        order = ''
        reftoeval = ''

        ouid = DEFAULT_UNIT_ID
        if self.ou:
            ouid = self.ou.id
            if self.ou.code == '99':
                ouid = DEFAULT_UNIT_ID
                reftoeval = 'CLNMZ 99-Activos'

            domain.append(('operating_unit_id', '=', ouid))
            order = 'operating_unit_id,'

        order += "date_refund, partner_id_internal, num_mov, refund_number_serie, refund_number, refund_uuid, " \
                 "invoice_id, invoice_number_serie, invoice_number"

        self.paymenttype = self.env['payment.type'].search([('code','=', PAYMENT_TYPE_CODE)])
        self.ir_attach_fe = self.env['ir.attachment.facturae.mx']
        self.ir_attach = self.env['ir.attachment']
        self.aml = self.env['account.move.line']
        self.credits = self.env['sync.morsa.refunds']
        self.av = self.env['account.voucher']
        self.avl = self.env['account.voucher.line']
        period = self.env['account.period']
        income_obj = self.env['sync.morsa.refunds']
        #payments = income_obj.search(domain, order=order)
        partner_id = ''
        uuid = ''
        periodcode = ''
        lines = {}
        totalpayment = 0
        totaltaxes = 0
        taxesinvoiced = 0
        xmlfile = ''
        av_header = {}
        paymentdate = ''
        nummaxtoprocess = 200
        hastoprocess = False

        #primero crea alguna Nota de Credito que haya quedado pendiente de aplicar
        hastoprocess = income_obj.create_refunds('out_invoice',
                                  'date_refund, num_mov, refund_number_serie, refund_number, refund_uuid',
                                  ouid
                                  )
        if hastoprocess:
            self.env.cr.commit()

        sqlpayments = """
                select distinct date_refund, partner_id_internal
                from sync_morsa_refunds 
                where invoice_type =  'in_payment' and num_mov = 500 and state = 'draft' 
                        and date_refund between '%s' and  '%s' and operating_unit_id = %s
                order by date_refund, partner_id_internal
                """ % (self.date_start, self.date_stop, ouid)

        self.env.cr.execute(sqlpayments)
        curpayments = self.env.cr.fetchall()
        for custpayment in curpayments:

            payments = income_obj.search([('date_refund', '=', custpayment[0]),
                                          ('partner_id_internal', '=', custpayment[1])] + domain, order=order)
            totalpayment = 0
            nummaxtoprocess = 1
            for payment in payments:

                print "**** PROCESANDO EL ID: %s, Invoice Number: %s, NumMax: %s, Partner: %s" % (payment.id, payment.invoice_number, nummaxtoprocess, payment.partner_id_internal)
                if partner_id != payment.partner_id.id:

                    partner_id = payment.partner_id.id
                    if not payment.partner_id.vat_subjected:
                        payment.partner_id.write({'vat_subjected': True})

                    self.oldaml = self.aml.search([('state', '=', 'valid'),
                                                   (
                                                       'account_id.id', '=',
                                                       self.ou.partner_id.property_account_receivable.id),
                                                   ('debit', '>', 0),
                                                   ('amount_residual', '>', 0),
                                                   ('partner_id', '=', partner_id),
                                                   ('date', '<=', '2018-12-31')
                                                   ], order="date desc")

                    self.oldamlpr = self.aml.search([('state', '=', 'valid'),
                                                     ('account_id.id', '=', self.acc_relative_partner.id),
                                                     ('debit', '>', 0),
                                                     ('amount_residual', '>', 0),
                                                     ('partner_id', '=', partner_id),
                                                     ('date', '<=', '2018-12-31')
                                                     ], order="date desc")
                    self.currentoldaml = 0
                    self.currentoldamlpr = 0
                    if payment.acc_relative_partner_id:
                        if self.currentoldamlpr:
                            currentmove = self.oldamlpr[self.currentoldamlpr].id
                            residualamount = self.oldamlpr[self.currentoldamlpr].amount_residual
                        # self.movesresidual.append(self.oldamlpr[self.currentoldamlpr].amount_residual)
                        # self.movesresidual.update({self.oldaml[self.currentoldaml].id: self.oldaml[]})
                        # self.residual = self.movesresidual[self.currentoldamlpr]
                    else:
                        currentmove = self.oldaml[self.currentoldaml].id
                        residualamount = self.oldaml[self.currentoldaml].amount_residual

                    self.movesresidual.update({currentmove: residualamount})
                    self.residual = residualamount

                if periodcode != payment.date_refund[5:7] + "/" + payment.date_refund[0:4]:
                    periodcode = payment.date_refund[5:7] + "/" + payment.date_refund[0:4]
                    period = period.search([('code', '=', periodcode)])

                if uuid != payment.refund_uuid:

                    if totalpayment > 0:
                        self.av.write({'amount': totalpayment})
                        taxesinvoiced = self._create_voucher_lines(lines)
                        self._increment_move(payment)
                        hastoprocess = True
                        #self.currentoldaml += 1
                        #self.residual = self.oldaml[self.currentoldaml].amount_residual


                    partner = payment.partner_id_internal
                    uuid = payment.refund_uuid
                    xmlfile = payment.xmlfile
                    totalpayment = 0
                    totaltaxes = 0
                    taxesinvoiced = 0
                    paymentdate = payment.date_refund

                    lines = []
                    vouchernumber = ''
                    if uuid:
                        vouchernumber = payment.refund_number_serie.strip() + "-" + payment.refund_number.strip()

                    av_header = {
                        'partner_id': partner_id,
                        'amount': 0,
                        'payment_type_id': self.paymenttype.id,
                        'date': payment.date_refund,
                        'number': vouchernumber,
                        'name': payment.partner_vat + "[" + str(payment.partner_id_internal) + "-" + str(payment.partner_id_internal_socio) + "]",
                        'journal_id': payment.sync_morsa_incomes_id.journal_income_id.id,
                        'account_id': payment.sync_morsa_incomes_id.journal_income_id.default_debit_account_id.id,
                        'period_id': period.id,
                        'type': 'receipt',
                        'voucher_operating_unit_id': payment.operating_unit_id.id,
                        'company_id': COMPANY_ID_MOR,
                        'pre_line': True,
                     }
                    self.av = self.av.create(av_header)
                    self._create_payment_attachment(uuid, xmlfile)
                    #print "Creando Pago: %s, rfc: %s, voucher id: %s. ID: %s " % (vouchernumber, self.av.name, self.av.id, payment.id)

                #'partner_bank_id': self._get_partner_bank_acc(payment),

                #print repr(payment)
                lines.append(payment)
                totalpayment += payment.amount_total
                totaltaxes += payment.amount_taxes
                payment.write({'state': 'paid', 'voucher_id': self.av.id})
                nummaxtoprocess += 1
            else:
                if totalpayment > 0:
                    self.av.write({'amount': totalpayment})
                    taxesinvoiced = self._create_voucher_lines(lines)
                    hastoprocess = True

            self.env.cr.commit()

        return hastoprocess

    def _create_payment_attachment(self, uuid, xmlfile):

        if uuid:
            vat = self.av.name[0:self.av.name.find("[")]
            numrep = self.av.number
            datos = {
                'name': vat + '_' + numrep + '.xml',
                'type': 'binary',
                'datas': xmlfile.encode('base64'),
                'res_name': numrep,
                'res_model': 'account.voucher',
                'company_id': 1,
                'datas_fname': vat + '_' + numrep + '.xml',
                'res_id': self.av.id,
            }
            self.ir_attach = self.ir_attach.create(datos)

            """LOGICA PARA ASIGNAR EL UUID A LA VOUCHER CREDO """
            datos = {
                'name': vat + '_' + numrep,
                'uuid': uuid,
                'state': 'done',
                'company_id': 1,
                'cfdi_type': 'incoming',
                'file_xml_sign': self.ir_attach.id,
                'type_attachment': 'account.voucher',
                'res_id': self.av.id,
            }
            self.ir_attach_fe = self.ir_attach_fe.create(datos)
            if self.ir_attach_fe:
                self.av.write({'cfdi_id': self.ir_attach_fe.id})

        return

    def _create_voucher_lines(self, lines):

        vlines = {}
        vrefunds = {}
        self.movesused = []
        self.refundsused = []
        taxesinvoiced = 0
        res = {}

        for line in lines:

            domain = [('num_mov', '>=', 610),
                      ('invoice_number', '=', line.invoice_number),
                      ('invoice_number_serie', '=', line.invoice_number_serie),
                      ('invoice_type', '=', 'out_invoice'),
                      ('refund_uuid', '!=', False),
                      ('voucher_id', '=', False),
                      ]

            self.credits = self.credits.search(domain)
            totalcredit = 0

            vkey = line.invoice_number_serie.strip() + "-" + str(line.invoice_number)
            if line.invoice_id == 0:
                #valida que exista
                inv = self.env['account.invoice'].search([('internal_number', '=', vkey)])
                if inv:
                    line.invoice_id = inv.id

            if line.invoice_id != 0:
                if vkey in vlines.keys():
                    vlines[vkey][0]['amount'] += line.amount_total
                else:
                    vlines.setdefault(vkey, []).append(self._get_move_from_invoice(line, 'cr'))

                taxesinvoiced += line.amount_taxes

                for credit in self.credits:
                    vkeyforrefund = credit.refund_number_serie.strip() + "-" + str(credit.refund_number)
                    res = self._get_move_from_invoice(credit, 'dr')
                    if res:
                        vrefunds.setdefault(vkeyforrefund, []).append(res)
                    else:
                        vrefunds[vkeyforrefund][0]['amount'] += credit.amount_total
                    totalcredit += credit.amount_total
                    credit.write({'state': 'paid', 'voucher_id': self.av.id})

                vlines[vkey][0]['amount'] += totalcredit
            else:
                amount = line.amount_total
                while True:
                    vkey = self._get_current_move(line) #self.oldaml[self.currentoldaml].id
                    if self.residual <= 0:
                        self._increment_move(line)
                        #self.currentoldaml += 1
                        vkey = self._get_current_move(line) #self.oldaml[self.currentoldaml].id
                        #self.residual = self.oldaml[self.currentoldaml].amount_residual

                    if self.residual < amount:
                        leftresidual = self.residual
                        amount -= self.residual
                        res = self._get_move_line(line, 'cr', leftresidual)
                        if res:
                            vlines.setdefault(vkey, []).append(res)
                        else:
                            vlines[vkey][0]['amount'] += leftresidual
                        self.residual = 0
                        continue
                    else:
                        res = self._get_move_line(line, 'cr', amount)
                        if res:
                            vlines.setdefault(vkey, []).append(res)
                        else:
                            vlines[vkey][0]['amount'] += amount
                        break

                for credit in self.credits:
                    vkeyforrefund = credit.refund_number_serie.strip() + "-" + str(credit.refund_number)
                    res = self._get_move_from_invoice(credit, 'dr')
                    if res:
                        vrefunds.setdefault(vkeyforrefund, []).append(res)
                    else:
                        vrefunds[vkeyforrefund][0]['amount'] += credit.amount_total
                    totalcredit += credit.amount_total
                    credit.write({'state': 'paid', 'voucher_id': self.av.id})

                if self.residual >= totalcredit:
                    vlines[vkey][0]['amount'] += totalcredit
                    self.residual -= totalcredit
                else:
                    totalcredit -= self.residual
                    vlines[vkey][0]['amount'] += self.residual
                    self.residual = 0
                    while True:
                        if self.residual <= 0:
                            self._increment_move(line)
                            #self.currentoldaml += 1
                            vkey = self._get_current_move(line) #self.oldaml[self.currentoldaml].id
                            #self.residual = self.oldaml[self.currentoldaml].amount_residual

                        if self.residual < totalcredit:
                            totalcredit -= self.residual
                            vlines.setdefault(vkey, []).append(self._get_move_line(line, 'cr', self.residual))
                            self.residual = 0
                            continue
                        else:
                            vlines.setdefault(vkey, []).append(self._get_move_line(line, 'cr', totalcredit))
                            #self.residual -= totalcredit
                            break

        for v in vlines.values():
            for vl in v:
                try:
                    vl['reconcile'] = abs(vl['amount']) == abs(vl['amount_unreconciled'])
                    self.avl.create(vl)
                except Exception as e:
                    #print repr(e)
                    pass

        for v in vrefunds.values():
            for vl in v:
                vl['reconcile'] = abs(vl['amount']) == abs(vl['amount_unreconciled'])
                self.avl.create(vl)


        #self.av.proforma_voucher()

        return taxesinvoiced

    def _get_move_from_invoice(self, vline, debit_credit):

        if debit_credit == 'cr':
            invoiceid = vline.invoice_id
        else:
            invoiceid = vline.refund_id

        invoice = self.env['account.invoice'].search([('id', '=', invoiceid)])
        if invoice and invoice.state == 'draft':
            invoice.invoice_open()

        acc_id = vline.acc_relative_partner_id.id if vline.acc_relative_partner_id else invoice.account_id.id

        #aml = self.aml.search([('move_id', '=', invoice.move_id.id),
        #                       ('account_id', '=', acc_id)])

        for ml in invoice.move_id.line_id:
            if ml.account_id.id == invoice.account_id.id:
                aml = ml
                break
        residual = vline.amount_total #min(aml.amount_residual, vline.amount_total)
        try:
            if aml.id in self.refundsused:
                return {}
        except Exception as err:
            raise UserError( "Fallo al quere asignar el movmiento de la NC: %s", invoice.internal_number)

        self.refundsused.append(aml.id)
        avl = {
            'name': aml.name,
            'type': debit_credit,
            'move_line_id': aml.id,
            'account_id': aml.account_id.id,
            'amount_original': aml.debit or aml.credit or 0.0,
            'amount': residual,
            'date_original': aml.date,
            'date_due': aml.date_maturity,
            'amount_unreconciled': abs(aml.amount_residual) or aml.debit or aml.credit or 0.0,
            'reconcile': False,
            'voucher_id': self.av.id
        }

        return avl

    def _get_move_line(self, vline, debit_credit, amount=None):

        aml = self.oldaml[self.currentoldaml]
        if vline.acc_relative_partner_id:
            aml = self.oldamlpr[self.currentoldamlpr]

        if not amount:
            amount = vline.amount_total

        if aml.id in self.movesused:
            self.residual -= amount
            return {}

        self.movesused.append(aml.id)
        avl = {
                'name': aml.name,
                'type': debit_credit,
                'move_line_id': aml.id,
                'account_id': aml.account_id.id,
                'amount_original': aml.debit or aml.credit or 0.0,
                'amount': min(self.residual, amount),
                'date_original': aml.date,
                'date_due': aml.date_maturity,
                'amount_unreconciled': self.residual or aml.debit or aml.credit or 0.0,
                'reconcile': False,
                'voucher_id': self.av.id
            }

        self.residual -= amount

        return avl

    def _get_current_move(self, line):
        currentmove = self.oldaml[self.currentoldaml].id

        if line.acc_relative_partner_id:
            currentmove = self.oldamlpr[self.currentoldamlpr].id

        return currentmove

    def _increment_move(self, line):

        if line.acc_relative_partner_id:
            if self.oldamlpr:
                currentmove = self.oldamlpr[self.currentoldamlpr]
                self.movesresidual.update({currentmove.id: self.residual})
                while True:
                    if self.currentoldamlpr == len(self.oldamlpr) - 1:
                        self.currentoldamlpr = 0
                    else:
                        self.currentoldamlpr += 1

                    currentmove = self.oldamlpr[self.currentoldamlpr]
                    self.movesresidual.update({currentmove.id: currentmove.amount_residual})
                    self.residual = self.movesresidual[currentmove.id]
                    if self.residual <= 0:
                        continue
                    else:
                        break
        else:
            currentmove = self.oldaml[self.currentoldaml]
            self.movesresidual.update({currentmove.id: self.residual})
            #self.movesresidual[self.currentoldaml] = self.residual
            while True:
                if self.currentoldaml == len(self.oldaml) - 1:
                    self.currentoldaml = 0
                else:
                    self.currentoldaml += 1

                #if len(self.movesresidual) == self.currentoldaml:
                    #self.movesresidual.append(self.oldaml[self.currentoldaml].amount_residual)

                currentmove = self.oldaml[self.currentoldaml]
                self.movesresidual.update({currentmove.id: currentmove.amount_residual})
                self.residual = self.movesresidual[currentmove.id]

                #self.residual = self.movesresidual[self.currentoldaml]
                if self.residual <= 0:
                    continue
                else:
                    break


        return

    def _create_special_moves(self):

        smr = self.env['sync.morsa.refunds']
        am = self.env['account.move']
        aml = self.env['account.move.line']
        amuuid = self.env['account.move.uuid']
        period_id = self.env['account.period']

        domain = [('state', '=', 'draft'),
                  ('num_mov', '=', self.move_type)
                ]

        if self.ou:
            domain.append(('operating_unit_id', '=', self.ou.id if self.ou.code != '99' else DEFAULT_UNIT_ID))

        smr = smr.search(domain, order='date_refund,partner_id_internal,refund_ref,id')

        if len(smr) == 0:
            raise UserError('No existen movimientos a procesar')

        for movto in smr:

            period_id = period_id.search([('code', '=', movto.date_refund[5:7] + "/" + movto.date_refund[0:4])])

            factura = ''
            refundnumber = "[" + movto.refund_number.strip() + "]" if movto.refund_number else ''
            if movto.invoice_number:
                factura = movto.invoice_number_serie.strip() + '-' if movto.invoice_number_serie else ''
                factura += movto.invoice_number.strip()

            if not am:
                data = {
                    'partner_id': movto.partner_id.id,
                    'date': movto.date_refund,
                    'ref': factura + refundnumber,
                    'journal_id': self.journal_special_id.id,
                    'company_id': COMPANY_ID_MOR,
                    'period_id': period_id.id,
                    'narration': str(movto.num_mov) + ('. ' + movto.comment.strip()) if movto.comment else ''
                    }
                am = am.create(data)

            cname = movto.partner_vat + \
                    "[" + str(movto.partner_id_internal) + "-" + \
                    str(movto.partner_id_internal_socio) + "]"
            aml_ = [
                    [cname, movto.partner_id.property_account_receivable.id, 0, movto.amount_total],
                    [factura, ID_CTA_IVA_POR_PAGAR, movto.amount_taxes, 0],
                    [factura, self.acc_debit_receivable.id, movto.amount_untaxed, 0],
                   ]

            uuid = movto.invoice_uuid.strip() if movto.invoice_uuid else ''

            for i in range(3):

                data = {
                    'partner_id':movto.partner_id.id,
                    'name': aml_[i][0],
                    'journal_id': self.journal_special_id.id,
                    'account_id': aml_[i][1],
                    'debit': aml_[i][2],
                    'credit': aml_[i][3],
                    'operating_unit_id': movto.operating_unit_id.id,
                    'company_id': COMPANY_ID_MOR,
                    'period_id': period_id.id,
                    'move_id': am.id,
                    'guid': uuid
                }
                aml = aml.create(data)

                if uuid:
                    data = {
                        'guid_ref': uuid,
                        'uuid': uuid,
                        'account_move_id': am.id,
                        'account_move_line_id': aml.id,
                    }
                    amuuid = amuuid.create(data)

                movto.write({'state': 'posted'})

        return
