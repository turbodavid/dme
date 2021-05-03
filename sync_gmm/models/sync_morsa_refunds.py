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
JOURNALCODE = {'0': 'CMPNAC', '1': 'CMPNACUS', '2': 'CMPUS'}
TAXCODEPURCHASE = {'16': 53, '8': 69, '0': ''}
TAXCODESALE = {'16': 50, '8': 69, '0': ''}
CURRENCY_ID = {'0': 34, '1': 3}

class sync_morsa_refunds(models.Model):
    _name = 'sync.morsa.refunds'

    sync_morsa_purchases_id = fields.Many2one(
            'sync.morsa.purchases', 'Sync Purchase ID',
            ondelete='cascade', index=True,
        )

    sync_morsa_incomes_id = fields.Many2one(
        'sync.morsa.incomes', 'Sync Income ID',
        ondelete='cascade', index=True,
    )

    invoice_type = fields.Selection([
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Supplier Invoice'),
            ('in_payment', 'Customer Payment'),
            ('out_payment', 'Supplier Payment'),
            ], 'Type'
        )

    partner_id_internal = fields.Integer('ID Empresa Interno')
    partner_id_internal_socio = fields.Integer('ID Empresa Interno asociado')
    partner_vat = fields.Char(size=20, string="RFC")
    partner_id = fields.Many2one('res.partner', 'Empresa')
    operating_unit_id = fields.Many2one('operating.unit', 'Unidad')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
            ('posted', 'Posted'),
            ], 'Status'
        )

    invoice_id = fields.Integer('ID Factura')
    refund_id = fields.Integer('ID Pago/NC')
    invoice_uuid = fields.Char('UUID Factura')
    refund_uuid = fields.Char('UUID Pago/NC')
    date_refund = fields.Date('Fecha Pago/NC')

    amount_untaxed = fields.Float(digits_compute=dp.get_precision('Account'), string='SubTotal')
    amount_total = fields.Float(digits_compute=dp.get_precision('Account'), string='Total')
    amount_taxes = fields.Float(digits_compute=dp.get_precision('Account'), string='Impuestos')

    refund_ref = fields.Integer('ID Interno (putty) de Pago/NC')
    invoice_number = fields.Char('Número de Factura', size=64)
    invoice_number_serie = fields.Char('Serie de la Factura', size=20)
    refund_number = fields.Char('Número de Pago/NC', size=64)
    refund_number_serie = fields.Char('Serie de Pago/NC', size=20)
    num_mov = fields.Integer('Tipo de Movimiento')
    id_kardex = fields.Integer('ID en el Origen')
    xmlfile = fields.Text('XML del Documento')
    comment = fields.Text('Notas')
    acc_relative_partner_id = fields.Many2one('account.account', 'Cuenta Contable')
    currency_id = fields.Many2one('res.currency', default=34, string='Moneda')
    currency_rate = fields.Float(digits_compute=dp.get_precision('Currency Rate'), default=1.0, string='Tipo de Cambio')
    voucher_id = fields.Many2one('account.voucher', 'ID Pago')
    journal_id = fields.Many2one('account.journal', 'ID Diario Ingreso')
    folio_ingreso = fields.Char('Folio Ingreso', size=10)

    serie_invoice_number = fields.Char(compute='_get_invoice_number', string='Número de Factura')
    serie_refund_number = fields.Char(compute='_get_refund_number', string='Número de NC/Pago')

    @api.depends('invoice_number')
    def _get_invoice_number(self):
        serie = ''
        invnumber = ''
        for rec in self:
            serie = rec.invoice_number_serie
            serie = (serie.strip() + '-') if serie else ''
            invnumber = rec.invoice_number if rec.invoice_number else ''
            rec.serie_invoice_number = serie + invnumber

        return

    @api.depends('refund_number')
    def _get_refund_number(self):

        serie = ''
        refnumber = ''
        for rec in self:
            serie = rec.refund_number_serie
            serie = (serie.strip() + '-') if serie else ''
            refnumber = rec.refund_number if rec.refund_number else ''
            rec.serie_refund_number = serie + refnumber

        return

    def _get_refund_journal(self, refund, acc_id, fiscal=True):

        ou_name = refund.operating_unit_id.name
        journaltype = refund.invoice_type
        serie = refund.refund_number_serie
        tipomov = refund.num_mov
        journalcode = ''

        if journaltype == 'in_invoice':
            purchasecode = 'CMP'
            currencyid = ''
            cmsgadi = ''
            if refund.currency_id.id == CURRENCY_ID['1']:
                purchasecode = 'CUS'
                acc_id = ''
                currencyid = CURRENCY_ID['1']
                cmsgadi = 'US '

            if tipomov in (620, 720):
                ccode = 'DEV'
                cmsg = cmsgadi + 'Devoluciones'
            else:
                ccode = 'FAL'
                cmsg = cmsgadi + 'Faltantes'
            journalcode = 'NC' + ccode + purchasecode + ('' if fiscal else 'NF')
            datos = {
                'name': 'Notas Credito ' + cmsg + ('' if fiscal else '(NO Fiscal)'),
                'code': journalcode,
                'type': 'purchase_refund',
                'analytic_journal_id': self.env['account.analytic.journal'].search([('code', '=', 'purchase')]).id,
                'default_debit_account_id': acc_id,
                'default_credit_account_id': acc_id,
                'active': True,
                'update_posted': True,
                'currency': currencyid,
            }
        else:
            if fiscal:
                if not serie:
                    serie = ''
                if len(serie) >= 7:
                    journalcode = 'NC'
                else:
                    journalcode = 'NCVT'
                journalcode += serie
            else:
                journalcode = 'NCVTANF'

            datos = {
                'name': 'Nota Credito Ventas ' + ( '' if fiscal else 'No Fiscal ' ) + \
                        ou_name + ' ' + (serie if serie else ''),
                'code': journalcode,
                'type': 'sale_refund',
                'analytic_journal_id': self.env['account.analytic.journal'].search([('code', '=', 'sale')]).id,
                'default_debit_account_id': acc_id,
                'default_credit_account_id': acc_id,
                'active': True,
                'update_posted': True,
                }

        journal = self.env['account.journal'].search([('code', '=', journalcode)])
        if not journal:
            journal = journal.create(datos)

        return journal.id


    ##process refunds that are not processed yet
    @api.multi
    def create_refunds(self, invoicetype='in_invoice',
                       order='partner_id_internal, refund_uuid',
                       operating_unit_id=None,
                       plusdomain=[]
                       ):

        if invoicetype == 'in_invoice':
            domain = [('state', '=', 'draft'),
                      ('invoice_type', '=', invoicetype)]
        else:
            domain = [('state', '=', 'draft'), ('num_mov', '>=', 610),
                      ('invoice_type', '=', invoicetype)]

        if operating_unit_id:
            domain.append(('operating_unit_id', '=', operating_unit_id))

        for d in plusdomain:
            domain.append(tuple(d))

        refunds_to_create = self.search(domain, order=order)

        if len(refunds_to_create) == 0:
            return False

        invoice = ''
        invoice_line = self.env['account.invoice.line']
        obj_sales_log = self.env['sync.sales.log']
        ir_fe = self.env['ir.attachment.facturae.mx']
        uuid = ''
        partner = ''
        acc_line_id = ''
        acc_relative_partner = ''
        sql = False
        wronginvoice = ''
        errormsg = ''
        tipodoctomsg = ''
        taxid = ''
        refundref = 0
        cpartnerlabel = ''
        uuidexists = {}
        ref_to_record = ''
        amountuntaxed = 0

        for refund in refunds_to_create:

            if wronginvoice and refund.refund_uuid.strip() and wronginvoice == refund.refund_uuid.strip():
                continue

            if (refund.refund_uuid in uuidexists.keys()) or (not refund.refund_uuid and refund):
                continue

            #print "Generando: ", refund.refund_ref, refund.refund_uuid, refund.partner_id_internal
            if partner != refund.partner_id_internal or \
                ((not refund.refund_uuid or refund.refund_uuid.strip() == '') and refund.refund_ref != refundref) \
                    or (refund.refund_uuid and uuid != refund.refund_uuid.strip()):

                sql = True
                acc_relative_partner = ''
                wronginvoice = ''
                taxcode = str(int(round((refund.amount_taxes / refund.amount_untaxed) * 100, 0)))
                if taxcode not in ['16', '8', '0']:
                    taxcode = '16'
                if invoicetype == 'in_invoice':
                    cpartnerlabel = 'Proveedor'
                    acc_line_id = refund.sync_morsa_purchases_id.cuenta_inventario.id
                    tipodoctomsg = 'Nota Credito Compras'
                    taxid = TAXCODEPURCHASE[taxcode]
                else:
                    cpartnerlabel = 'Cliente'
                    acc_relative_partner = refund.acc_relative_partner_id.id
                    tipodoctomsg = 'Nota Credito Ventas'
                    taxid = TAXCODESALE[taxcode]
                    if refund.num_mov in [620, 720]:
                        acc_line_id = refund.sync_morsa_incomes_id.acc_refund_id.id
                    else:
                        acc_line_id = refund.sync_morsa_incomes_id.acc_benefit_id.id

                if partner and invoice:
                    if invoice_line:
                        invoice_line.write({'price_unit': amountuntaxed})
                    invoice.button_reset_taxes()
                    invoice.invoice_open()
                    self.env.cr.commit()

                partner = refund.partner_id_internal
                uuid = refund.refund_uuid.strip() if refund.refund_uuid else ''
                refundref = refund.refund_ref
                ref_to_record = refund.partner_vat + "[" + str(refund.partner_id_internal) + "-" + \
                                str(refund.partner_id_internal_socio) + "]"
                amountuntaxed = 0

                try:
                    ir_fe = ir_fe.search([('uuid', '=', uuid)])
                    if uuid and ir_fe:
                        values = [ir_fe.res_id, refund.partner_id_internal]
                        uuidexists.setdefault(uuid.encode('utf-8'), ir_fe.res_id)
                        continue
                    invoice, wronginvoice = self._create_refund_header(refund, acc_line_id)
                    errormsg = wronginvoice
                    if invoice:
                        datos = {
                            'name': invoice.operating_unit_id.code + '|' + ref_to_record,
                            'account_id': acc_line_id,
                            'quantity': 1,
                            'price_unit': 0,
                            'uos_id': 1,
                            'company_id': 1,
                            'invoice_line_tax_id': [(6, 0, [taxid]), ] if taxid else '',
                            'invoice_id': invoice.id,
                        }
                        # SE CREAN LAS LINEAS DE LA FACTURA
                        invoice_line = invoice_line.create(datos)

                except Exception as err:
                    wronginvoice = uuid or 'ERROR'
                    errormsg = err.message + "\n" + \
                               "UUID: %s. Factura: %s. %s: %s. Nota Credito: %s " \
                               % (uuid, refund.invoice_number_serie+refund.invoice_number,
                                  cpartnerlabel, refund.partner_id_internal, refund.refund_ref)
                    raise

                if wronginvoice:
                    sales_log = {
                        'tipo': tipodoctomsg,
                        'operating_unit': refund.operating_unit_id.name,
                        'message': errormsg,
                        'ip_addres': refund.operating_unit_id.ip_address,
                        'data_base': refund.operating_unit_id.data_base,
                    }
                    obj_sales_log.create(sales_log)
                    if wronginvoice == 'ERROR':
                        wronginvoice = ''
                        continue

            # """LINEAS DE LA NOTA DE CREDITO"""
            # ref_to_record = refund.invoice_uuid.strip() if refund.invoice_uuid else ''
            # ref_to_record += "[" + refund.invoice_number_serie.strip() + \
            #                  ("-" if refund.invoice_number_serie else '') + refund.invoice_number + "]"
            # datos = {
            #     'name': invoice.operating_unit_id.code + '|' + ref_to_record,
            #     'account_id': acc_line_id,
            #     'quantity': 1,
            #     'price_unit': refund.amount_untaxed,
            #     'uos_id': 1,
            #     'company_id': 1,
            #     'invoice_line_tax_id': [(6, 0, [taxid]),] if taxid else '',
            #     'invoice_id': invoice.id,
            # }
            # # SE CREAN LAS LINEAS DE LA FACTURA
            # invoice_line = invoice_line.create(datos)
            amountuntaxed += refund.amount_untaxed
            refund.write({'refund_id': invoice.id, 'state': 'open'})

        else:
            if invoice:
                if invoice_line:
                    invoice_line.write({'price_unit': amountuntaxed})
                invoice.button_reset_taxes()
                invoice.invoice_open()

        if invoicetype == 'in_invoice':
            return sql

        if len(uuidexists) > 0:
            self.fix_customers_refunds(uuidexists)

        #rectifica las ya validadas
        #k = uuid
        #v = [invoice_id, partner_internal]
        # av = self.env['account.voucher']
        # invoice = self.env['account.invoice']
        # for k, v in uuidexists.items():
        #     vouchers = self.search([('refund_uuid', '=', k), ('voucher_id', '!=', False)])
        #     refunds_to_create = self.search([('refund_uuid', '=', k), ('refund_id', '=', False)])
        #     invoice = invoice.search([('id', '=', v)])
        #     lines = []
        #     if invoice:
        #         internalpartner = invoice.name[invoice.name.find("[") + 1:]
        #         internalpartner = internalpartner[:internalpartner.find("-")]
        #
        #         voucherstoaffect = []
        #         vlines = []
        #         if vouchers:
        #             for ml in invoice.move_id.line_id:
        #                 if ml.account_id.id == invoice.account_id.id:
        #                     mlid = ml
        #                     break
        #
        #             for voucher in vouchers:
        #                 if voucher.voucher_id.state == 'posted':
        #                     voucherstoaffect.append(voucher.voucher_id)
        #                     voucher.voucher_id.cancel_voucher()
        #                     voucher.voucher_id.action_cancel_draft()
        #                 elif voucher.voucher_id.state == 'cancel':
        #                     continue
        #
        #                 for vl in voucher.voucher_id.line_dr_ids:
        #                     if vl.move_line_id == mlid:
        #                         vlines.append(vl)
        #
        #         if invoice.state == 'open':
        #             if invoice.move_id.state == 'posted':
        #                 moveid = invoice.move_id
        #                 moveid.button_cancel()
        #                 moveid.write({'state': 'draft'})
        #
        #             invoice.invoice_cancel()
        #             invoice.action_cancel_draft()
        #
        #         if invoice.state == 'draft':
        #             for refund in refunds_to_create:
        #                 taxcode = str(int(round((refund.amount_taxes / refund.amount_untaxed) * 100, 0)))
        #                 if taxcode not in ['16', '8', '0']:
        #                     taxcode = '16'
        #                 taxid = TAXCODESALE[taxcode]
        #                 if refund.num_mov in [620, 720]:
        #                     acc_line_id = refund.sync_morsa_incomes_id.acc_refund_id.id
        #                 else:
        #                     acc_line_id = refund.sync_morsa_incomes_id.acc_benefit_id.id
        #
        #                 ref_to_record = refund.invoice_uuid.strip() if refund.invoice_uuid else ''
        #                 ref_to_record += "[" + refund.invoice_number_serie.strip() + \
        #                                  ("-" if refund.invoice_number_serie else '') + refund.invoice_number + "]"
        #                 datos = {
        #                     'name': invoice.operating_unit_id.code + '|' + ref_to_record,
        #                     'account_id': acc_line_id,
        #                     'quantity': 1,
        #                     'price_unit': refund.amount_untaxed,
        #                     'uos_id': 1,
        #                     'company_id': 1,
        #                     'invoice_line_tax_id': [(6, 0, [taxid]), ] if taxid else '',
        #                     'invoice_id': invoice.id,
        #                 }
        #                 # SE CREAN LAS LINEAS DE LA FACTURA
        #                 invoice_line = invoice_line.create(datos)
        #                 refund.write({'refund_id': invoice.id, 'state': 'open'})
        #             invoice.button_reset_taxes()
        #             invoice.invoice_open()
        #
        #         if vlines:
        #             for ml in invoice.move_id.line_id:
        #                 if ml.account_id.id == invoice.account_id.id:
        #                     mlid = ml
        #                     break
        #
        #             for vl in vlines:
        #                 vl.write({'move_line_id': mlid.id, 'reconcile': False})
        #
        #             for voucher in voucherstoaffect:
        #                 voucher.proforma_voucher()
        return sql

    def _create_refund_header(self, refund, acc_line_id):

        invoice = self.env['account.invoice']
        ir_attach_fe = self.env['ir.attachment.facturae.mx']
        ir_attach = self.env['ir.attachment']
        obj_sales_log = self.env['sync.sales.log']
        numrefund = ''
        numinvoice = ''
        esfiscal = ''
        acc_relative_partner = refund.acc_relative_partner_id.id
        cmsgforerror = 'Proveedor'
        err = ''

        esfiscal = (refund.refund_uuid.strip() != '') if refund.refund_uuid else False
        numrefund = refund.refund_number_serie.strip()
        numrefund += ('-' if numrefund else '') + refund.refund_number
        journalnumber = numrefund

        currencyvalue = 1
        if refund.invoice_type == 'in_invoice':
            acc_payable_receivable = refund.partner_id.property_account_payable.id
            if refund.currency_id.id == CURRENCY_ID['1']:
                acc_payable_receivable = refund.sync_morsa_purchases_id.cuenta_prov_extranjeros.id
                currencyvalue = refund.currency_rate
                if refund.xmlfile and refund.xmlfile.strip() != 'None':
                    currencyvalue = ir_attach_fe.parse_data(refund.xmlfile, "TipoCambio")
            doctype = 'in_refund'
            numinvoice = refund.invoice_number_serie
            numinvoice += ('-' if numinvoice else '') + refund.invoice_number
            if not esfiscal:
                numrefund = ''
                journalnumber = ''
        else:
            cmsgforerror = 'Cliente'
            acc_payable_receivable = acc_relative_partner if acc_relative_partner \
                        else refund.partner_id.property_account_receivable.id
            doctype = 'out_refund'
            numinvoice = refund.refund_ref
            journalnumber = str(numinvoice) + "/" + numrefund

        datos = {
            'partner_id': refund.partner_id.id,
            'company_id': 1,
            'account_id': acc_payable_receivable,
            'journal_id': self._get_refund_journal(refund, acc_line_id, esfiscal),
            'operating_unit_id': refund.operating_unit_id.id,
            'type': doctype,
            'origin': numinvoice,
            'date_invoice': refund.date_refund,
            'number': journalnumber,
            'internal_number': journalnumber,
            'supplier_invoice_number': numrefund,
            'reference': refund.refund_ref,
            'name': refund.partner_vat + "[" + str(refund.partner_id_internal) + "-" + str(refund.partner_id_internal_socio) + "]",
            'comment': str(refund.num_mov) + '-' + refund.comment,
            'currency_id': refund.currency_id.id,
            'currency_rate': currencyvalue,
        }

        invoice = invoice.create(datos)

        if invoice and esfiscal and refund.xmlfile and refund.xmlfile.strip() != 'None':
            datos = {
                'name': refund.partner_vat + '_' + numrefund + '.xml',
                'type': 'binary',
                'datas': refund.xmlfile.encode('base64'),
                'res_name': 'NC ' + cmsgforerror + ' ' + str(refund.refund_ref) + "/" + numrefund,
                'res_model': 'account.invoice',
                'company_id': 1,
                'datas_fname': refund.partner_vat + '_' + numrefund + '.xml',
                'res_id': invoice.id,
            }
            try:
                ir_attach = ir_attach.create(datos)
            except Exception as e:
                err = repr(e)
                pass

        """LOGICA PARA ASIGNAR EL UUID A LA NC CREADA """
        if invoice and esfiscal and err == '':
            datos = {
                'name': refund.partner_vat + '_' + numrefund,
                'rfc_emisor': refund.partner_vat,
                'uuid': refund.refund_uuid.strip(),
                'state': 'done',
                'company_id': 1,
                'cfdi_type': 'outgoing',
                'file_xml_sign': ir_attach.id,
                'type_attachment': 'account.invoice',
                'res_id': invoice.id,
            }
            try:
                ir_attach_fe = ir_attach_fe.create(datos)
                if ir_attach_fe:
                    invoice.write({'cfdi_id': ir_attach_fe.id})
            except Exception as e:
                err = repr(e)

        return invoice, err

    def create_table_erpid(self, ou):

        sql = "SELECT 1 FROM  pg_tables WHERE  schemaname = 'public' AND tablename = 'erpid'"
        conexion = self.env['sync.morsa.conexion']._get_conexion_direct(ou.ip_address, ou.data_base)
        cursor = conexion.cursor()
        try:
            cursor.execute(sql)
            record = cursor.fetchall()
            if len(record) == 0:
                sql = """
                CREATE TABLE erpid (
                    id int4 NOT NULL,
                    erpid int4 NULL,
                    tabla varchar(40) NOT NULL,
                    tablaerp varchar(40) NULL,
                    CONSTRAINT erpid_pk PRIMARY KEY (id,tabla)
                );
                CREATE INDEX erpid_erpid_idx ON erpid (erpid,tablaerp);
                """
                cursor.execute(sql)
        except Exception as err:
            cursor.rollback()
            raise
        finally:
            conexion.commit()
            conexion.close()

        return

    @api.multi
    def fix_customers_refunds(self, smrids):

        where = str(tuple(smrids.keys())).replace(',)', ')')
        sql = """
            select distinct smr.refund_id, smr.operating_unit_id, 
                  concat(trim(smr.refund_number_serie),'-',trim(smr.refund_number)) notcre,
                  ou.ip_address, ou.data_base, smr.refund_uuid
            from sync_morsa_refunds smr 
                inner join operating_unit ou on (smr.operating_unit_id = ou.id)
            where smr.refund_id is not null and smr.refund_uuid in %s
            order by smr.operating_unit_id, smr.refund_id;
            """ % where

        self.env.cr.execute(sql)
        smrtofix = self.env.cr.fetchall()
        if len(smrtofix) == 0:
            return

        ou = ''
        cursor = ''
        conexion = ''
        con_branch = self.env['sync.morsa.conexion']
        invoice = self.env['account.invoice']
        for smr in smrtofix:

            sql = "select id_kar, seriedoc, numdocto, tipomov, importe, iva from cxckardex " \
                  "where concat(trim(serie),'-',referencia::varchar) = '%s' order by id_kar;" % smr[2]
            if ou != smr[1]:
                if ou:
                    conexion.close()
                ou = smr[1]
                conexion = con_branch._get_conexion_direct(smr[3], smr[4])
                cursor = conexion.cursor()

            cursor.execute(sql)
            refundsok = cursor.fetchall()

            res = {}
            for refund in refundsok:
                res.setdefault(refund[0], refund)

            tofix = self.search([('refund_uuid', '=', smr[5])], order="id_kardex")

            refunds_to_sum = 0
            amount_paid = 0
            for refund in tofix:

                serie = res[refund.id_kardex][1].strip()
                factura = str(res[refund.id_kardex][2])
                total = res[refund.id_kardex][4]
                subtotal = round(res[refund.id_kardex][4]/(1+(res[refund.id_kardex][5]/100)), 2)
                taxes = total - subtotal
                uuid = ''
                invoiceid = ''
                invoice = invoice.search([('number', '=', serie + '-' + factura)])
                if invoice:
                    uuid = invoice.cfdi_id.uuid
                    invoiceid = invoice.id

                toupdate = {'num_mov': res[refund.id_kardex][3],
                            'refund_id': smr[0],
                            'invoice_number': factura,
                            'invoice_number_serie': serie,
                            'amount_total': total,
                            'amount_taxes': taxes,
                            'amount_untaxed': subtotal,
                            'invoice_uuid': uuid,
                            'invoice_id': invoiceid
                        }

                if refund.state == 'draft':
                    toupdate.update({'state': 'open'})

                refund.write(toupdate)

                refunds_to_sum += subtotal
                amount_paid += total if refund.voucher_id else 0

            invoice = invoice.search([('id', '=', smr[0])])
            if invoice and invoice.amount_untaxed != refunds_to_sum:
                count = 0
                for il in invoice.invoice_line:
                    if count == 0:
                        iltokeep = il
                        count = 1
                        continue
                    il.unlink()

                total = refunds_to_sum
                iltokeep.write({'price_unit': total})
                invoice.button_reset_taxes()
                invoice.write({'residual': invoice.amount_total - amount_paid})

        return
    
    # @api.multi
    # def fix_customers_refunds(self, smrids):
    #
    #
    #     fromself = (smrids.keys()[0] != 'lang')
    #     if not fromself:
    #         sql = """
    #             with wrongnc as
    #             (
    #                 select  smr.refund_id, smr.refund_uuid, smr.id_kardex
    #                 from sync_morsa_refunds smr inner join operating_unit ou on (smr.operating_unit_id = ou.id)
    #                 where invoice_type = 'out_invoice' and  invoice_number = refund_number and trim(invoice_number_serie) = ''
    #             )
    #             select distinct wrongnc.refund_id, smr.operating_unit_id,
    #                   concat(trim(smr.refund_number_serie),'-',trim(smr.refund_number)) notcre,
    #                   ou.ip_address, ou.data_base
    #             from sync_morsa_refunds smr inner join wrongnc on (smr.refund_uuid = wrongnc.refund_uuid)
    #                 inner join operating_unit ou on (smr.operating_unit_id = ou.id)
    #             where smr.id_kardex != wrongnc.id_kardex
    #             order by smr.operating_unit_id, wrongnc.refund_id;
    #             """
    #     else:
    #         sql = """
    #             select distinct smr.refund_id, smr.operating_unit_id,
    #                   concat(trim(smr.refund_number_serie),'-',trim(smr.refund_number)) notcre,
    #                   ou.ip_address, ou.data_base, smr.refund_uuid
    #             from sync_morsa_refunds smr
    #                 inner join operating_unit ou on (smr.operating_unit_id = ou.id)
    #             where smr.refund_id is not null and smr.refund_uuid in %s
    #             order by smr.operating_unit_id, smr.refund_id;
    #             """ % smrids.keys()
    #
    #     self.env.cr.execute(sql)
    #     smrtofix = self.env.cr.fetchall()
    #     if len(smrtofix) == 0:
    #         UserWarning("No existen Notas de Crédito por Corregir")
    #         return
    #
    #     ou = ''
    #     cursor = ''
    #     conexion = ''
    #     con_branch = self.env['sync.morsa.conexion']
    #     for smr in smrtofix:
    #
    #         sql = "select id_kar, seriedoc, numdocto, tipomov, importe, iva from cxckardex " \
    #               "where concat(trim(serie),'-',referencia::varchar) = '%s';" % smr[2]
    #         if ou != smr[1]:
    #             if ou:
    #                 conexion.close()
    #             ou = smr[1]
    #             conexion = con_branch._get_conexion_direct(smr[3], smr[4])
    #             cursor = conexion.cursor()
    #
    #         cursor.execute(sql)
    #         refundsok = cursor.fetchall()
    #
    #         res = {}
    #         for refund in refundsok:
    #             res.setdefault(refund[0], refund)
    #
    #         if fromself:
    #             tofix = self.search([('refund_uuid', '=', smr[5])], order="id_kardex")
    #         else:
    #             tofix = self.search([('refund_id', '=', smr[0])], order="id_kardex")
    #
    #         invoice = self.env['account.invoice']
    #         refunds_to_sum = 0
    #         amount_paid = 0
    #         for refund in tofix:
    #
    #             serie = res[refund.id_kardex][1].strip()
    #             factura = str(res[refund.id_kardex][2])
    #             total = res[refund.id_kardex][4]
    #             subtotal = round(res[refund.id_kardex][4]/(1+(res[refund.id_kardex][5]/100)), 2)
    #             taxes = total - subtotal
    #             uuid = ''
    #             invoiceid = ''
    #             invoice = invoice.search([('number', '=', serie + '-' + factura)])
    #             if invoice:
    #                 uuid = invoice.cfdi_id.uuid
    #                 invoiceid = invoice.id
    #
    #             refund.write(
    #                 {'num_mov': res[refund.id_kardex][3],
    #                  'refund_id': smr[0],
    #                  'invoice_number':  factura,
    #                  'invoice_number_serie': serie,
    #                  'amount_total': total,
    #                  'amount_taxes': taxes,
    #                  'amount_untaxed': subtotal,
    #                  'invoice_uuid': uuid,
    #                  'invoice_id': invoiceid
    #                 })
    #
    #             refunds_to_sum += subtotal
    #             amount_paid += total if refund.voucher_id else 0
    #
    #         invoice = invoice.search([('id', '=', smr[0])])
    #         if invoice and invoice.amount_untaxed != refunds_to_sum:
    #             count = 0
    #             for il in invoice.invoice_line:
    #                 if count == 0:
    #                     iltokeep = il
    #                     count = 1
    #                     continue
    #                 il.unlink()
    #
    #             total = refunds_to_sum
    #             iltokeep.write({'price_unit': total})
    #             invoice.button_reset_taxes()
    #             invoice.write({'residual': invoice.amount_total - amount_paid})


##class sync_morsa_refunds

class DuplicateCFDIError(Exception):
    message = 'Folio Fiscal (UUID) duplicado.'
    pass


