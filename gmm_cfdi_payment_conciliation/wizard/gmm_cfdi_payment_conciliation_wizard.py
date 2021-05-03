
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2019 Grupo MORSA - http://www.morsa.com.mx
#    All Rights Reserved.
############################################################################
#    Coded by:
#       David Alberto Perez Payán (davidperez@dmesoluciones.com)
############################################################################
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

#from openerp.addons.web.controllers.main import Session
#import datetime as dt

import psycopg2
import psycopg2.extras
from lxml import etree as ET
from datetime import datetime as dt, timedelta
from openerp.exceptions import Warning as UserError
from openerp import fields, models, api


SERVER = 'culiacan.morsa.com.mx'
DB = 'culiacan'
MASS_DISCOUNT = 2184


class CFDISupplierPaymentWizard(models.TransientModel):
    _name = 'gmm.cfdi.supplier.payment.wizard'
    _description = "Wizard to find Supplier's CFDIs"

    def _get_first_day_of_month(self):
        return dt.now().strftime("%Y-%m-01")

    partner_id = fields.Many2one(
        'res.partner',
        'Supplier',
        help='Select Supplier to find CFDI Payment (left blank for all)',
        domain=[('supplier', '=', True)]
        )

    date_from = fields.Date(
        string='From Date', help='Supplier CFDIs issued from this Date',
        default=lambda self: self._get_first_day_of_month())

    date_to = fields.Date(
        string='To Date', help='Supplier CFDIs issued up to this Date',
        default=fields.Date.today())

    from_company = fields.Boolean(
        string='Take Payments done by Company',
        help='Check if you need to look for Payments done by Company instead of the Suppliers Issued date',
        default=True)

    credits_to_date = fields.Date(
        string='Credits date', help='Look for Credits up to this date'
    )

    @api.multi
    @api.onchange('date_to')
    def onchange_date_to(self):

        if self.date_to < self.date_from:
            self.date_to = fields.Date.today()

        dateto = dt.strptime(self.date_to, '%Y-%m-%d')
        self.credits_to_date = dateto + timedelta(days=60)

        return

    @api.multi
    def get_supplier_payments(self):

        if self.from_company:
            self._get_company_payments()
            return True

        cn = self.env['sync.morsa.conexion'].get_direct_connection(SERVER, DB)
        payments = cn.cursor()
        credits = cn.cursor()
        invoices = cn.cursor()
        payments.execute(self._get_sql_cfdi_payments())
        opayment = self.env['gmm.cfdi.supplier.payment']
        paymentinvoice = self.env['gmm.cfdi.supplier.payment.invoices']
        creditinvoice = self.env['gmm.cfdi.supplier.payment.credits']
        obj_iratt = self.env['ir.attachment.facturae.mx']

        for payment in payments:
            pay_info = {
                'partner_id': self.partner_id.id,
                'serie':   payment[0],
                'number':  payment[1],
                'uuid':    payment[2],
                'date':    payment[3],
                'amount':  payment[4],
                'name':    'Pago Emitido el ' + str(payment[3])
            }
            paymentid = opayment.create(pay_info)
            invoices.execute(self._get_sql_payment_invoices(payment[2]))
            if invoices.rowcount == 0:
                invoices = self._read_from_xml(payment[5].encode("UTF-8"))

            for invoice in invoices:
                ir_att = obj_iratt.search([('uuid', '=', invoice[2])])
                inv_info = {
                    'payment_id': paymentid.id,
                    'serie': invoice[0],
                    'number': invoice[1],
                    'uuid': invoice[2],
                    'amount_paid': invoice[3],
                    'amount': invoice[4],
                    'amount_residual': invoice[5],
                    'invoice_id': ir_att.res_id or False
                }
                invoice_id = paymentinvoice.create(inv_info)
                credits = cn.cursor()
                credits.execute(self._get_sql_payment_credits(invoice[0], invoice[1]))
                for credit in credits:

                    # kp.num_mov 0
                    # kp.serie    1
                    # kp.foliofact  2
                    # kp.seriedoc, 3
                    # kp.referencia, 4
                    # kp.importe, 5
                    # kp.fec_fact, 6
                    #cp.tipo_de_documento, 7
                    # cp.foliofiscal, 8
                    # cp.serie, 9
                    # cp.folio 10

                    creditid = False
                    amtcredit = credit[5]
                    sserie = credit[3]
                    sfolio = credit[4]
                    if credit[8]:
                        ir_att = obj_iratt.search([('uuid', '=', credit[8])])
                        sserie = credit[9]
                        sfolio = credit[10]
                        creditid = ir_att.res_id or False

                    inv_info = {
                        'payment_id': paymentid.id,
                        'serie': sserie,
                        'number': sfolio,
                        'inv_serie': credit[1],
                        'inv_number': credit[2],
                        'uuid': credit[8],
                        'amount': amtcredit,
                        'credit_id': creditid,
                        'invoices_applied': [(4, invoice_id.id)]
                    }
                    creditinvoice.create(inv_info)

        if cn:
            cn.close()

        return True

    def _get_company_payments(self):

        opayment = self.env['gmm.cfdi.supplier.payment']
        paymentinvoice = self.env['gmm.cfdi.supplier.payment.invoices']
        creditinvoice = self.env['gmm.cfdi.supplier.payment.credits']
        line_obj = self.env['gmm.cfdi.supplier.payment.line']
        move_obj = self.env['account.move.line']
        obj_iratt = self.env['ir.attachment.facturae.mx']

        self.env.cr.execute(self._get_sql_company_payments())
        mls = self.env.cr.dictfetchall()
        cn = self.env['sync.morsa.conexion'].get_direct_connection(SERVER, DB)
        cursor = cn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        payments = ''
        invoices = ''
        credits = ''

        for ml in mls:
            first = True
            ainvoices_ = []
            ainvuuids_ = []
            resinv = {}
            rfc = self.partner_id.vat[2:].strip()
            sumcredits = 0
            datefrom = ml['date']
            dateto = self.credits_to_date
            cursor.execute(self._get_sql_company_folios_paid(ml['move_id'], ml['date'].replace('-', ''), True))
            payments = cursor.fetchall()
            status = 'draft'
            for payment in payments:
                paymentid = False
                withuuid = False
                pagouuid = payment['pagouuid']
                if pagouuid:
                    withuuid = True
                    status = 'process'
                else:
                    pagouuid = str(ml['id'])
                paymentid = opayment.search([('uuid', '=', pagouuid)])
                ainvoices_ = []
                ainvuuids_ = []
                resinv = {}
                sumcredits = 0

                if not paymentid:
                    pay_info = {
                        'partner_id': self.partner_id.id,
                        'serie':   payment['seriepago'],
                        'number':  payment['foliopago'],
                        'uuid':    pagouuid,
                        'date':    payment['fecha_cfdi'],
                        'amount':  payment['total_cfdi'],
                        'company_paid_date': ml['date'],
                        'state':   status,
                        'name':    'Pago Emitido el ' + str(payment['fecha_cfdi']) if payment['fecha_cfdi'] else 'SIN PAGO'
                    }
                    paymentid = opayment.create(pay_info)
                    paymentid.add_payment_lines(ml['id'])

                paymentid.add_invoices_paid(cn)
                #paymentid.add_credits_used(cn, datefrom, dateto)
                paymentid.action_confirm()

        if cn:
            cn.close()

        return True


    # def _get_company_payments(self):
    #
    #     opayment = self.env['gmm.cfdi.supplier.payment']
    #     paymentinvoice = self.env['gmm.cfdi.supplier.payment.invoices']
    #     creditinvoice = self.env['gmm.cfdi.supplier.payment.credits']
    #     line_obj = self.env['gmm.cfdi.supplier.payment.line']
    #     move_obj = self.env['account.move.line']
    #     obj_iratt = self.env['ir.attachment.facturae.mx']
    #
    #     self.env.cr.execute(self._get_sql_company_payments())
    #     mls = self.env.cr.dictfetchall()
    #     cn = self.env['sync.morsa.conexion'].get_direct_connection(SERVER, DB)
    #     cursor = cn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #     payments = ''
    #     invoices = ''
    #     credits = ''
    #
    #     for ml in mls:
    #         first = True
    #         ainvoices_ = []
    #         ainvuuids_ = []
    #         resinv = {}
    #         rfc = self.partner_id.vat[2:].strip()
    #         sumcredits = 0
    #         datefrom = ml['date']
    #         dateto = self.credits_to_date
    #         cursor.execute(self._get_sql_company_folios_paid(ml['move_id'], ml['date'].replace('-', ''), True))
    #         payments = cursor.fetchall()
    #         status = 'draft'
    #         for payment in payments:
    #             paymentid = False
    #             withuuid = False
    #             pagouuid = payment['pagouuid']
    #             if pagouuid:
    #                 withuuid = True
    #                 status = 'process'
    #             else:
    #                 pagouuid = str(ml['id'])
    #             paymentid = opayment.search([('uuid', '=', pagouuid)])
    #             ainvoices_ = []
    #             ainvuuids_ = []
    #             resinv = {}
    #             sumcredits = 0
    #
    #             if not paymentid:
    #                 pay_info = {
    #                     'partner_id': self.partner_id.id,
    #                     'serie':   payment['seriepago'],
    #                     'number':  payment['foliopago'],
    #                     'uuid':    pagouuid,
    #                     'date':    payment['fecha_cfdi'],
    #                     'amount':  payment['total_cfdi'],
    #                     'company_paid_date': ml['date'],
    #                     'state':   status,
    #                     'name':    'Pago Emitido el ' + str(payment['fecha_cfdi']) if payment['fecha_cfdi'] else 'SIN PAGO'
    #                 }
    #                 paymentid = opayment.create(pay_info)
    #                 paymentid.add_payment_lines(ml['move_id'])
    #
    #             paymentid.add_invoices_paid()
    #             cursor.execute(
    #                 self._get_sql_company_folios_paid(ml['move_id'], ml['date'].replace('-', ''), False, pagouuid if withuuid else False))
    #             invoices = cursor.fetchall()
    #
    #             for inv in invoices:
    #                 pendiente = inv['pendiente'] or (inv['importe'] - inv['imppagado'])
    #                 inv_info = {
    #                     'payment_id': paymentid.id,
    #                     'serie': inv['serie'],
    #                     'number': inv['foliofact'],
    #                     'uuid': inv['foliofiscal'],
    #                     'amount_paid': inv['pagado'] or inv['imppagado'],
    #                     'amount': inv['anterior'] or inv['importe'],
    #                     'amount_residual': pendiente,
    #                     'invoice_id': inv['invoice_id'] if inv['invoice_id'] > 0 else False
    #                 }
    #                 print('Serie: %s, FolioFact: %s, UUID: %s' % (str(inv['serie'].strip()),
    #                                                               str(inv['foliofact']),
    #                                                               str(inv['foliofiscal'])))
    #
    #                 invoice_id = paymentinvoice.create(inv_info)
    #                 ainvoices_.append(str(inv['serie'].strip()+str(inv['foliofact'])))
    #                 ainvuuids_.append(str(inv['foliofiscal']))
    #                 resinv.setdefault(inv['foliofiscal'], []).append([str(inv['serie']).strip(),
    #                                                                      str(inv['foliofact']).strip(),
    #                                                                      pendiente, invoice_id.id])
    #                 sumcredits += pendiente
    #
    #             creditosissued = 0
    #             if sumcredits > 0:
    #                 #creditos por devoluciones o registrados
    #                 cursor.execute(self._get_credits_from_company_payment(rfc, ainvoices_))
    #                 credits = cursor.fetchall()
    #                 rescredits = {}
    #                 for credit in credits:
    #                     if credit['credituuid'] in rescredits:
    #                         rescredits[credit['credituuid']][0][3] += credit['importe']
    #                         rescredits[credit['credituuid']][0][4].append(resinv[credit['fact_uuid']][0][3])
    #                     else:
    #                         ir_att = obj_iratt.search([('uuid', '=', credit['credituuid'])])
    #                         rescredits.setdefault(credit['credituuid'], []).append([credit['serie'].strip(),
    #                                                                                credit['folio'],
    #                                                                                ir_att.res_id or False,
    #                                                                                credit['importe'],
    #                                                                                [resinv[credit['fact_uuid']][0][3]]])
    #                     # creditid = False
    #                     # amtcredit = credit['importe'] or 0
    #                     # sserie = credit['serie'].strip()
    #                     # sfolio = credit['folio']
    #                     # ir_att = obj_iratt.search([('uuid', '=', credit['credituuid'])])
    #                     # creditid = ir_att.res_id or False
    #                     #
    #                     # inv_info = {
    #                     #     'payment_id': paymentid.id,
    #                     #     'serie': sserie,
    #                     #     'number': sfolio,
    #                     #     'inv_serie': credit['seriefact'],
    #                     #     'inv_number': credit['foliofact'],
    #                     #     'uuid': credit['credituuid'],
    #                     #     'amount': amtcredit,
    #                     #     'amount_credit': amtcredit,
    #                     #     'credit_id': creditid,
    #                     #     'invoices_applied': [(4, resinv[credit['fact_uuid']][0][3])]
    #                     # }
    #                     # creditinvoice.create(inv_info)
    #                     creditosissued += credit['importe']
    #
    #                 #creditos por diferencia en precio o problemas de catalogo
    #                 credits.execute(self._get_sql_for_credits_issued(rfc, datefrom, dateto))
    #                 for credit in credits:
    #                     invoicespaid = self._read_credits_from_xml(credit['xmlfile'].encode("UTF-8"), ainvuuids_)
    #                     if len(invoicespaid) > 0:
    #                         creditosissued += credit['importe']
    #                         if credit['credituuid'] in rescredits:
    #                             rescredits[credit['credituuid']][0][3] += credit['importe']
    #                         else:
    #                             ir_att = obj_iratt.search([('uuid', '=', credit['credituuid'])])
    #                             rescredits.setdefault(credit['credituuid'], []).append([credit['serie'].strip(),
    #                                                                                     credit['folio'],
    #                                                                                     ir_att.res_id or False,
    #                                                                                     credit['importe'],
    #                                                                                     []])
    #                     for inv in invoicespaid:
    #                         rescredits[credit['credituuid']][0][4].append(resinv[inv][0][3])
    #                         #amtcredit = resinv[inv][0][2]
    #                         # sserie = credit['serie']
    #                         # sfolio = credit['folio']
    #                         # ir_att = obj_iratt.search([('uuid', '=', inv)])
    #                         # creditid = ir_att.res_id or False
    #                         #
    #                         # inv_info = {
    #                         #     'payment_id': paymentid.id,
    #                         #     'serie': sserie,
    #                         #     'number': sfolio,
    #                         #     'inv_serie': resinv[inv][0][0],
    #                         #     'inv_number': resinv[inv][0][1],
    #                         #     'uuid': credit['foliofiscal'],
    #                         #     'amount': amtcredit,
    #                         #     'credit_id': creditid,
    #                         #     'amount_credit': credit['total'],
    #                         #     'invoices_applied': [(4, resinv[inv][0][3])]
    #                         # }
    #                         # creditinvoice.create(inv_info)
    #                         #sumcredits -= amtcredit
    #
    #                     if len(ainvoices_) <= len(invoicespaid):
    #                         break
    #
    #                 for k, v in rescredits.items():
    #                     inv_info = {
    #                         'payment_id': paymentid.id,
    #                         'serie': v[0][0],
    #                         'number': v[0][1],
    #                         'uuid': k,
    #                         'amount_credit': v[0][3],
    #                         'credit_id': v[0][2],
    #                         'invoices_applied': [(4, v[0][4])]
    #                     }
    #                     creditinvoice.create(inv_info)
    #
    #             if abs(sumcredits-creditosissued) <= 5 and status == 'process':
    #                 status = 'done'
    #                 paymentid.write({'state': status})
    #
    #     if cn:
    #         cn.close()
    #
    #     return True

    def _get_sql_company_payments(self):
        sql = """
            select aml.id, aml."date", aml."ref", aml."name", move_id, debit, credit
            from account_move_line aml inner join account_account aa on (aml.account_id = aa.id)
                    inner join account_period ap on (aml.period_id = ap.id)
            where not ap.special and aml.partner_id = %s and aml."date" between '%s' and '%s'
                and (aa.id in (2017,2022,2860) or aa."type" = 'liquidity')
            order by 2, 5;
        """ % (self.partner_id.id, self.date_from, self.date_to)

        return sql

    def _get_sql_company_folios_paid(self, moveid, datepaid, onlypayments=False, pagouuid=None):

        fields_ = ['aml."name"', 'ou.code']
        condition_ = ['', '']
        sql = ''
        for i in range(0, 2):
            sql = """
                select distinct %s
                from account_move_line aml inner join operating_unit ou on (aml.operating_unit_id = ou.id)
                    inner join account_account aa on (aml.account_id = aa.id)
                where aml.move_id = %s and aml.debit > 0 and aa."type" = 'payable';       
            """ % (fields_[i], moveid)
            self.env.cr.execute(sql)
            result = self.env.cr.fetchall()
            condition_[i] = str(tuple([int(x[0]) for x in result])).replace(',)', ')')

        swhereuuid = ''
        if onlypayments:
            sql = """
                select distinct pago.foliofiscal pagouuid, pago.serie seriepago, pago.folio foliopago,  
                        pago.fecha::date fecha_cfdi,
                       cpago.monto::numeric / 100 total_cfdi
            """
        else:
            sql = """
                select cfdi.emirfc, f.num_prov, f.num_suc, fg.folio, f.serie, f.foliofact, f.invoice_id, f.importe, 
                       cfdi.foliofiscal, pago.foliofiscal pagouuid, 
                       pago.serie seriepago, pago.folio foliopago,  pago.fecha::date fecha_cfdi,
                       cpago.monto::numeric / 100 total_cfdi,
                       dpago.imppagado / 100::numeric pagado, dpago.impsaldoinsoluto / 100::numeric pendiente,
                       dpago.impsaldoant / 100::numeric anterior, 
                       ROUND(importe-(saldo_notas+p_promocion+n_cargo+anticipo+saldo_desctos+devolucion+faltante),02) ImpPagado	
                """
            if pagouuid:
                swhereuuid = "pago.foliofiscal = '%s' and " % pagouuid

        sql += """from cxpfacturas f 
                    INNER JOIN cxpproveedores p ON f.num_prov = p.num_prov
                    INNER JOIN foliosgen fg ON (f.num_prov = fg.num_prov AND f.fec_venc = fg.fecha_ven )
                    inner join cat_sucursales suc on (f.num_suc=suc.num_suc)
                    left join cfdi_cfdcomprobanteproveedor cfdi 
                            on (f.foliofact=cfdi.folio and trim(f.serie)=trim(cfdi.serie) 
                                 and replace(trim(p.rfc),'-','') = cfdi.emirfc )
                    left join cfdi_cfdcomprobantepagodoctos dpago on (cfdi.foliofiscal = dpago.iddocumento)
                    left join cfdi_cfdcomprobanteproveedor pago on (dpago.foliofiscal = pago.foliofiscal)
                    left join cfdi_cfdcomprobantepago cpago on (cpago.foliofiscal = pago.foliofiscal)            
             where %s
                fg.folio in %s
                and f.num_suc in %s
                and f.fecha_pago = %s       
        """ % (swhereuuid, condition_[0], condition_[1], datepaid)

        return sql

    def _get_credits_from_company_payment(self, rfc, ainvoices):

        sql = """
            select kp.num_mov, kp.serie seriefact, kp.foliofact, fcfdi.foliofiscal fact_uuid, 
                    kp.seriedoc, kp.referencia, kp.importe, kp.fec_fact, 
                    cp.tipo_de_documento, cp.foliofiscal credituuid, cp.serie, cp.folio
            from cxpkardex kp 
                inner join cxpproveedores p on (kp.num_prov = p.num_prov)
                inner join cfdi_cfdcomprobanteproveedor  fcfdi on (fcfdi.folio = kp.foliofact and fcfdi.serie = kp.serie)
                left join cfdi_cfdcomprobanteproveedor cp 
                    on (cp.sucursal_carta = kp.num_suc and cp.folio_carta = kp.referencia
                        and (cp.tipo_de_documento  = 'E' or cp.tipo_de_documento is null))
            where trim(replace(p.rfc, '-', '')) = '%s'
                and   concat(trim(kp.serie), kp.foliofact) in %s   
                and (cp.emirfc = '%s' or cp.emirfc  is null)
                and kp.num_mov >= 600
                and cp.foliofiscal is not null;
        """ % (rfc, str(tuple(ainvoices)).replace(',)', ')'), rfc)

        return sql

    def _get_sql_for_credits_issued(self, rfc, datefrom, dateto):

        sql = """
        select folio, serie, foliofiscal credituuid, fecha, regexp_replace(xml, '[^\x20-\x7f\x0d\x1b]', ' ', 'g') xmlfile, 
                tipoxml, tipo_asociacion, subtotal / 100::numeric subtotal, 
                total / 100::numeric importe
        from cfdi_cfdcomprobanteproveedor scp 
        where trim(emirfc) = '%s' and 
        tipo_de_documento  = 'E' and fecha between '%s' and '%s'
        order by fecha;
        """ % (rfc, datefrom, dateto)

        return sql

    def _read_credits_from_xml(self, data, ainvuuids_):
        invoices = []
        root = ET.fromstring(data)
        einv = root.findall('cfdi:CfdiRelacionados/cfdi:CfdiRelacionado', root.nsmap)
        for e in einv:
            info = e.attrib['UUID']
            if info in ainvuuids_:
                invoices.append(info)
        return invoices

    def _read_from_xml(self, data):
        invoices = []
        root = ET.fromstring(data)
        einv = root.findall('cfdi:Complemento/pago10:Pagos/pago10:Pago/pago10:DoctoRelacionado', root.nsmap)
        for e in einv:
            info = e.attrib
            invoices.append([info['Serie'], info['Folio'], info['IdDocumento'].upper(),
                             float(info['ImpPagado']), float(info['ImpSaldoAnt']), float(info['ImpSaldoInsoluto'])
                             ])
        return invoices

    def _get_sql_cfdi_payments(self):
        sql = """
            select trim(sc.serie) serie, sc.folio::varchar folio, upper(sc.foliofiscal) foliofiscal, 
                    fecha::date fecha, scp.monto::numeric / 100 total,
                    regexp_replace(sc.xml, '[^\x20-\x7f\x0d\x1b]', ' ', 'g') xmlfile
            from cfdi_cfdcomprobanteproveedor sc inner join cfdi_cfdcomprobantepago scp on (scp.foliofiscal = sc.foliofiscal )
            where trim(emirfc) = '%s' and tipo_de_documento  = 'P' and
                fecha between '%s' and '%s'
            order by fecha;
        """ % (self.partner_id.vat[2:], self.date_from, self.date_to)
        return sql

    def _get_sql_payment_invoices(self, uuid):
        sql = """
            select trim(scf.serie) serie, scf.folio,
                upper(scpd.iddocumento) iddocumento, scpd.imppagado::numeric / 100 imppagado, 
                scpd.impsaldoant::numeric / 100 impsaldoant, 
                scpd.impsaldoinsoluto::numeric / 100 impsaldoinsoluto
            from cfdi_cfdcomprobantepagodoctos scpd 
                inner join cfdi_cfdcomprobanteproveedor scf on (scf.foliofiscal = scpd.iddocumento)
            where upper(scpd.foliofiscal) = '%s'
            order by scf.fecha::date, scf.serie, scf.folio;
        """ % uuid.upper()

        return sql

    def _get_sql_payment_credits(self, serie, foliofact):
        rfc = self.partner_id.vat[2:]
        sql = """
            select kp.num_mov, kp.serie, kp.foliofact, kp.seriedoc, kp.referencia, kp.importe, kp.fec_fact, 
                    cp.tipo_de_documento, cp.foliofiscal, cp.serie, cp.folio 
            from cxpkardex kp 
                inner join cxpproveedores p on (kp.num_prov = p.num_prov)
                left join cfdi_cfdcomprobanteproveedor cp 
                    on (cp.sucursal_carta = kp.num_suc and cp.folio_carta = kp.referencia
                        and (cp.tipo_de_documento  = 'E' or cp.tipo_de_documento is null))
            where trim(replace(p.rfc, '-', '')) = '%s'
                and    kp.foliofact = %s and kp.serie = '%s'   
                and (cp.emirfc = '%s' or cp.emirfc  is null)
                and kp.num_mov >= 600;""" % (rfc, foliofact, serie, rfc)

        return sql
