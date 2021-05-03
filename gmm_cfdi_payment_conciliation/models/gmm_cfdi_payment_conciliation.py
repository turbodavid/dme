# -*- coding: utf-8 -*-
# © 2009 Pexego/Comunitea
# © 2016 Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from lxml import etree as ET
import psycopg2
import psycopg2.extras
from datetime import datetime
from openerp import api, fields, models, _
import logging
import openerp.addons.decimal_precision as dp

BANK_JOURNAL = 262
MASS_DISCOUNT = 2184
SERVER = 'culiacan.morsa.com.mx'
DB = 'culiacan'


class CFDISupplierPayment(models.Model):
    _name = "gmm.cfdi.supplier.payment"
    _description = (
        "It stores the payments made and the CFDIs issuedd by the Supplier "
        "on a period of time")

    READONLY_STATES = {'process': [('readonly', True)],
                       'done': [('readonly', True)],
                       'draft': [('readonly', True)]}

    name = fields.Char(string='Notes', help='Comments about this payment', required=True, index=True)
    partner_id = fields.Many2one(
        'res.partner', string='Supplier', help='Payments done by this Supplier',
        domain=[('supplier', '=', True)], states=READONLY_STATES)

    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('process', 'Processed'),
                   ('done', 'Done'),
                   ('canceled', 'Canceled')],
        string='State', default='draft')

    serie = fields.Char(string="Serie", help='Payment Serie')
    number = fields.Char(string='Number', help='Payment Number')
    uuid = fields.Char(string='UUID', help='CFDI UUID', index=True)
    date = fields.Date(string='Payment Date')
    company_paid_date = fields.Date(string='Company Paid Date')
    amount = fields.Float(digits_compute=dp.get_precision('Account'), string='Payment Amount')
    payment_number = fields.Char(compute='_get_payment_number', string='Number')
    payment_residual = fields.Float(digits_compute=dp.get_precision('Account'),
                                    compute='_sum_totals', string='Sum of Invoices Balance')
    credits_issued = fields.Float(digits_compute=dp.get_precision('Account'),
                                  compute='_sum_totals', string='Sum of Credits Issued by Supplier')
    residual = fields.Float(digits_compute=dp.get_precision('Account'),
                            compute='_sum_totals', string='Balance Difference', help='Difference: Balance - Credits')

    payment_line_ids = fields.One2many(
        'gmm.cfdi.supplier.payment.line', 'payment_id', 'ERP Moves Payments related',
        states=READONLY_STATES)

    payment_ids = fields.One2many(
        'gmm.cfdi.supplier.payment.line', 'payment_id', 'Payment registered',
        domain=[('type', '=', 'payment')], context={'default_type': 'payment'},
        states=READONLY_STATES
    )

    credit_ids = fields.One2many(
        'gmm.cfdi.supplier.payment.line', 'payment_id', 'Credits Used',
        domain=[('type', '=', 'credit')], context={'default_type': 'credit'},
        states=READONLY_STATES
    )

    payment_line_invoices = fields.One2many(
        'gmm.cfdi.supplier.payment.invoices', 'payment_id', 'Invoices Paid in this CFDI',
        states=READONLY_STATES)

    payment_line_credits = fields.One2many(
        'gmm.cfdi.supplier.payment.credits', 'payment_id', 'Credits Used for this Payment',
        states=READONLY_STATES)

    payment_line_credits_nr = fields.One2many(
        'gmm.cfdi.supplier.payment.credits.notrel', 'payment_id', 'Not Related Credits Used for this Payment',
        states=READONLY_STATES)

    # @api.multi
    # def fields_view_get(self):
    #     #, view_id=None, view_type='form', toolbar=False, submenu=False):
    #
    #     res = super(CFDISupplierPayment, self).fields_view_get(self)
    #     #, view_id, view_type, toolbar, submenu)
    #     return res
    @api.multi
    def name_get(self):
        name = []
        for rec in self:
            rec_name = rec.payment_number + '(' + str(rec.date) + ')'
            name.append((rec.id, rec_name))

        return name

    @api.multi
    @api.depends('payment_number')
    def _get_payment_number(self):

        for rec in self:
            serie = rec.serie
            serie = (serie.strip() + '-') if serie else ''
            paynumber = rec.number if rec.number else ''
            rec.payment_number = serie + paynumber

        return

    @api.multi
    @api.depends('payment_residual', 'credits_issued', 'residual')
    def _sum_totals(self):

        for rec in self:
            credits = 0
            residual = 0
            for credit in rec.payment_line_credits:
                credits += credit.amount_credit
            for credit in rec.payment_line_credits_nr:
                credits += credit.amount
            for invoice in rec.payment_line_invoices:
                residual += invoice.amount_residual
            rec.credits_issued = credits
            rec.payment_residual = residual
            rec.residual = round(residual - credits, 2)
        return


    @api.multi
    def action_calculate(self):
        """Called when the user presses the Calculate button.
        It will look for invoices paid and credits applied."""
        for payment in self:
            # Clear the report data (unlink the lines of detail)
            #payment.payment_line_ids.unlink()
            if not payment.company_paid_date:
                payment.write({'company_paid_date': payment.payment_ids[0].date})

            payment.add_invoices_paid()
            payment.add_credits_used()
            #if self._create_pay_line():
            #    payment.write({'state': 'process'})

        return True

    @api.multi
    def action_confirm(self):
        """Called when the user clicks the confirm button."""
        if self.state == 'process' and abs(self.residual) < 5:
            self.write({'state': 'done'})
        return True

    @api.multi
    def action_cancel(self):
        """Called when the user clicks the cancel button."""
        self.write({'state': 'canceled'})
        return True

    @api.multi
    def action_recover(self):
        """Called when the user clicks the draft button to create
        a new workflow instance."""
        self.write({'state': 'draft'})
        return True

    @api.multi
    def add_payment_lines(self, ml):

        line_obj = self.env['gmm.cfdi.supplier.payment.line']
        move_obj = self.env['account.move.line']
        aml = move_obj.search([('id', '=', ml)])
        # liga el movimiento del pago en el ERP
        pay_info = {
            'payment_id': self.id,
            'move_line_id': aml.id,
            'type': 'payment',
            'concilied': True
        }
        line_obj.create(pay_info)

        # liga el movimiento de credito en el ERP
        aml = move_obj.search([('move_id', '=', aml.move_id.id),
                               ('account_id', '=', MASS_DISCOUNT)])
        if aml:
            pay_info = {
                'payment_id': self.id,
                'move_line_id': aml.id,
                'type': 'credit',
                'concilied': False
            }
            line_obj.create(pay_info)

    @api.multi
    def add_invoices_paid(self, cn=None, invoices_=None, calledfrompayments=False, invlines=False):

        paymentinvoice = self.env['gmm.cfdi.supplier.payment.invoices']
        ldesconecta = False

        invlines = False
        if not invoices_:
            invlines = self.payment_line_invoices

        if not invlines:
            if not cn:
                cn = self.env['sync.morsa.conexion'].get_direct_connection(SERVER, DB)
                ldesconecta = True

            cursor = cn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            ml = self.payment_ids[0].move_line_id
            if not calledfrompayments:
                cursor.execute(
                    self._get_sql_company_folios_paid(ml.move_id.id, ml.date.replace('-', ''), False,
                                                      self.uuid if self.name != 'SIN PAGO' else False))
                invoices = cursor.fetchall()
            else:
                invoices = invoices_

            for inv in invoices:
                pendiente = inv['pendiente'] or (inv['importe'] - inv['imppagado'])
                inv_info = {
                    'payment_id': self.id,
                    'serie': inv['serie'].strip(),
                    'number': inv['foliofact'],
                    'uuid': inv['foliofiscal'].strip().upper(),
                    'amount_paid': inv['pagado'] or inv['imppagado'],
                    'amount': inv['importe'] or inv['anterior'],
                    'amount_residual': pendiente,
                    'invoice_id': inv['invoice_id'] if inv['invoice_id'] > 0 else False
                }
                paymentinvoice.create(inv_info)
        else:
            invlines = False


        if ldesconecta and cn:
            cn.close()

        return

    @api.multi
    def add_credits_used(self, cn=None, datefrom=None, dateto=None, callledfrompayments=False):

        creditinvoice = self.env['gmm.cfdi.supplier.payment.credits']
        ldesconecta = False
        if not cn:
            ldesconecta = True
            cn = self.env['sync.morsa.conexion'].get_direct_connection(SERVER, DB)

        cursor = cn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(self._get_credits_from_company_payment(self.partner_id.vat[2:]))
        credits = cursor.fetchall()

        resinv = {}
        for inv in self.payment_line_invoices:
            resinv.update({inv.uuid: inv.id})
        rescredits = {}
        obj_iratt = self.env['ir.attachment.facturae.mx']

        #creditos reconocidos
        for credit in credits:

            print "Credito: %s " % credit['credituuid']
            if credit['credituuid'] and credit['credituuid'] in rescredits:
                rescredits[credit['credituuid']][0][3] += credit['importe']
                rescredits[credit['credituuid']][0][4].append(resinv[credit['fact_uuid']])
                #rescredits[credit['credituuid']][0][4].append(resinv[credit['fact_uuid']][0][3])
            else:
                ir_att = obj_iratt.search([('uuid', '=', credit['credituuid'])])
                rescredits.setdefault(credit['credituuid'], []).append([credit['serie'].strip(),
                                                                        credit['folio'],
                                                                        ir_att.res_id or False,
                                                                        credit['importe'],
                                                                        [resinv[credit['fact_uuid']] or False]])
        if not callledfrompayments:
            cursor.execute(self._get_sql_for_credits_issued(datefrom, dateto))
            credits = cursor.fetchall()
            for credit in credits:
                invoicespaid, lhasdoctosrel = self._read_credits_from_xml(credit['xmlfile'].encode("UTF-8"), resinv)
                if len(invoicespaid) > 0:
                    if credit['credituuid'] in rescredits:
                        rescredits[credit['credituuid']][0][3] += credit['importe']
                    else:
                        rescredits.setdefault(credit['credituuid'], []).append([credit['serie'].strip(),
                                                                                credit['folio'],
                                                                                False,
                                                                                credit['importe'],
                                                                                []])
                    for inv in invoicespaid:
                        rescredits[credit['credituuid']][0][4].append(resinv[inv])

                if not lhasdoctosrel:
                    info = {
                        'partner_id': self.partner_id.id,
                        'serie': credit['serie'].strip(),
                        'number': credit['folio'],
                        'uuid': credit['credituuid'],
                        'amount': credit['importe'],
                        'date': credit['fecha']
                    }
                    self.env['gmm.cfdi.supplier.payment.credits.notrel'].create(info)

        for k, v in rescredits.items():
            inv_info = {
                'payment_id': self.id,
                'serie': v[0][0],
                'number': v[0][1],
                'uuid': k,
                'amount_credit': v[0][3],
                'credit_id': v[0][2],
                'invoices_applied': [(4, v[0][4])]
            }
            creditinvoice.create(inv_info)

        if ldesconecta and cn:
            cn.close()

        return

    def _get_credits_from_company_payment(self, rfc, ainvoices=None):

        crlines = self.payment_line_credits
        invlines = self.payment_line_invoices
        uuids = ''
        serieinv = ''
        if len(crlines) > 0:
            for cr in crlines:
                uuids = 'cp.foliofiscal not in %s and ' % str(tuple([str(x['uuid']) for x in crlines])).replace(',)', ')')

        if not ainvoices:
            ainvoices = [str(x['serie'].strip()) + str(x['number']) for x in invlines]

        sql = """
            select kp.num_mov, kp.serie seriefact, kp.foliofact, upper(fcfdi.foliofiscal) fact_uuid, 
                    kp.seriedoc, kp.referencia, kp.importe, kp.fec_fact, 
                    cp.tipo_de_documento, upper(cp.foliofiscal) credituuid, cp.serie, cp.folio
            from cxpkardex kp 
                inner join cxpproveedores p on (kp.num_prov = p.num_prov)
                inner join swpr_cfdcomprobanteproveedor  fcfdi on (fcfdi.folio = kp.foliofact 
                                                                    and fcfdi.serie = kp.serie
                                                                    and trim(replace(fcfdi.emirfc, '-', '')) = '%s'
                                                                  )
                left join swpr_cfdcomprobanteproveedor cp 
                    on (cp.sucursal_carta = kp.num_suc and cp.folio_carta = kp.referencia
                        and (cp.tipo_de_documento  = 'E' or cp.tipo_de_documento is null))
            where %s trim(replace(p.rfc, '-', '')) = '%s'
                and   concat(trim(kp.serie), kp.foliofact) in %s   
                and (cp.emirfc = '%s' or cp.emirfc  is null)
                and kp.num_mov >= 600
                and cp.foliofiscal is not null;
        """ % (rfc, uuids, rfc, str(tuple(ainvoices)).replace(',)', ')'), rfc)

        return sql

    def _get_sql_for_credits_issued(self, datefrom=None, dateto=None):

        sql = """
            select iafm.uuid
            from account_invoice ai inner join ir_attachment_facturae_mx iafm 
                    on (ai.cfdi_id = iafm.id)
            where ai.partner_id = %s and ai."type" = 'in_refund'
            union
            select gcspc.uuid
            from gmm_cfdi_supplier_payment_credits gcspc inner join gmm_cfdi_supplier_payment gcsp 
                    on (gcspc.payment_id = gcsp.id)
            where gcsp.partner_id = %s
            union
            select notrel.uuid
            from gmm_cfdi_supplier_payment_credits_notrel notrel
            where notrel.partner_id = %s;
        """ % (self.partner_id.id, self.partner_id.id, self.partner_id.id)
        self.env.cr.execute(sql)
        uuids = self.env.cr.fetchall()
        luuids = [str(x[0]) for x in uuids]
        whereuuids = ''
        if len(luuids) > 0:
            whereuuids = "foliofiscal not in ('%s') and " % "','".join(map(str, luuids))

        rfc = self.partner_id.vat[2:]
        if not datefrom:
            datefrom = self.company_paid_date or self.payment_ids[0].date

        wheredate = "'%s' and " % datefrom
        if dateto:
            wheredate += "'%s' " % dateto
        else:
            wheredate += "'%s'::date + interval '3 MONTHS' "

        sql = """
         select folio, serie, foliofiscal credituuid, fecha, regexp_replace(xml, '[^\x20-\x7f\x0d\x1b]', ' ', 'g') xmlfile, 
                 tipoxml, tipo_asociacion, subtotal / 100::numeric subtotal, 
                 total / 100::numeric importe
         from swpr_cfdcomprobanteproveedor scp 
         where %s 
                trim(emirfc) = '%s' 
                and tipo_de_documento = 'E'
                and fecha between %s 
         order by fecha;
         """ % (whereuuids, rfc, wheredate)

        return sql

    def _read_credits_from_xml(self, data, ainvuuids_):
        lhasdoctorel = False
        invoices = []
        root = ET.fromstring(data)
        einv = root.findall('cfdi:CfdiRelacionados/cfdi:CfdiRelacionado', root.nsmap)
        for e in einv:
            lhasdoctorel = True
            info = e.attrib['UUID']
            if info in ainvuuids_:
                invoices.append(info)
        return invoices, lhasdoctorel

    def _create_pay_line(self):
        lfound = False
        line_obj = self.env['gmm.cfdi.supplier.payment.line']
        move_obj = self.env['account.move.line']

        domain = [('partner_id', '=', self.partner_id.id),
                               ('date', '<=', self.date),
                               ('journal_id', '=', BANK_JOURNAL),
                               ('account_id.type', 'in', ['liquidity', 'payable']),
                               ('credit', '=', self.amount)
                  ]

        for i in range(0, 2):
            amls = move_obj.search(domain)
            for aml in amls:
                moveid = aml.move_id.id
                lfound = True
                res_pl = {
                    'payment_id': self.id,
                    'move_line_id': aml.id,
                    'type': 'payment',
                    'concilied': True
                }
                line_obj.create(res_pl)
                amldiscount = move_obj.search([('move_id', '=', moveid), ('account_id', '=', MASS_DISCOUNT)])
                if amldiscount:
                    res_pl = {
                        'payment_id': self.id,
                        'move_line_id': amldiscount.id,
                        'type': 'credit',
                        'concilied': False
                    }
                    line_obj.create(res_pl)
            if lfound:
                break
            domain = self._get_aml_by_paymentdone()

            if len(domain) == 0:
                break

        return lfound

    def _get_aml_by_paymentdone(self):
        domain = []
        uuids = "','".join(map(str, [x[0]['uuid'].rstrip() for x in self.payment_line_invoices]))
        sql = """
            select distinct fg.fecha_ven, fg.folio::varchar, 
                to_date(f.fecha_pago::varchar, 'YYYYMMDD')::text, 
                lpad(suc.num_suc::varchar, 2, '0') num_suc 
            from cxpfacturas f 
                inner join swpr_cfdcomprobanteproveedor sc on (trim(sc.serie) = trim(f.serie) and sc.folio = f.foliofact)
                inner join foliosgen fg on (fg.fecha_ven = f.fec_venc and fg.num_prov = f.num_prov)
                inner join cat_sucursales suc on (suc.num_suc = f.num_suc )
            where sc.foliofiscal in ('%s')
        """ % uuids
        cn = self.env['sync.morsa.conexion'].get_direct_connection(SERVER, DB)
        crsinv = cn.cursor()
        crsinv.execute(sql)

        if crsinv.rowcount > 0:
            name_ = []
            date_ = []
            ou_ = []
            for inv in crsinv:
                name_.append(inv[1])
                date_.append(inv[2])
                ou_.append(inv[3])

            domain = [('partner_id', '=', self.partner_id.id),
                      ('name', 'in', name_),
                      ('operating_unit_id.code', 'in', ou_),
                      ('date', 'in', date_)
                      ]
            result = self.env['account.move.line'].read_group(domain, fields=['move_id'], groupby=['move_id'])
            domain = [('move_id', 'in', [x['move_id'][0] for x in result]),
                      ('account_id.type', 'in', ['liquidity', 'payable']),
                      ('credit', '>', 0.0)
                      ]
        return domain

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
                    left join swpr_cfdcomprobanteproveedor cfdi 
                            on (f.foliofact=cfdi.folio and trim(f.serie)=trim(cfdi.serie) 
                                 and replace(trim(p.rfc),'-','') = cfdi.emirfc )
                    left join swpr_cfdcomprobantepagodoctos dpago on (cfdi.foliofiscal = dpago.iddocumento)
                    left join swpr_cfdcomprobanteproveedor pago on (dpago.foliofiscal = pago.foliofiscal)
                    left join swpr_cfdcomprobantepago cpago on (cpago.foliofiscal = pago.foliofiscal)            
             where %s
                fg.folio in %s
                and f.num_suc in %s
                and f.fecha_pago = %s       
        """ % (swhereuuid, condition_[0], condition_[1], datepaid)

        return sql

#end class CFDISupplierPayment


class CFDISupplierPaymentInvoices(models.Model):
    _name = "gmm.cfdi.supplier.payment.invoices"
    _order = "serie, number"
    _description = (
        "Detailed Invoices paid by the CFDI Issued.")

    payment_id = fields.Many2one(
        'gmm.cfdi.supplier.payment', string='Payment',
        ondelete='cascade')

    invoice_id = fields.Many2one(
        'account.invoice', string='Invoice', help='Purchase Invoice Number', ondelete='cascade'
    )

    credits_applied = fields.Many2many(
        'gmm.cfdi.supplier.payment.credits',
        'gmm_cfdi_supplier_payment_invoice_credits_rel',
        'payment_invoice_id',  'payment_credit_id', 'Credits')

    #date = fields.Date(string='Date', help='Invoice Date')
    date = fields.Date(related='invoice_id.date_invoice', string='Date')
    operating_unit_id = fields.Many2one('operating.unit', related='invoice_id.operating_unit_id', string='Unit')
    serie = fields.Char(string='Serie', help='Invoice Serie')
    number = fields.Integer(string='Number', help='Invoice Number')
    uuid = fields.Char(string='UUID', help='Invoice UUID', index=True)
    amount = fields.Float(string='Amount', help='Invoice Total')
    amount_paid = fields.Float(string='Paid', help='Amount Paid')
    amount_residual = fields.Float(string='Residual', help='Residual Amount')
    invoice_number = fields.Char(compute='_get_invoice_number', string='Invoice')
    name = fields.Char(compute='_get_invoice_number', string='Invoice')

    @api.depends('invoice_number', 'name')
    def _get_invoice_number(self):
        for rec in self:
            serie = rec.serie or ''
            serie = (serie.strip() + '-') if serie else ''
            invnumber = str(rec.number) if rec.number else ''
            rec.invoice_number = serie + invnumber
            rec.name = serie + invnumber
        return

    def sum_residual(self, context=None):
        residual = 0
        for rec in self.browse(context):
            residual += rec.amount_residual
        return residual

# END CLASS CFDISupplierPaymentInvoices

class CFDISupplierPaymentCredits(models.Model):
    _name = "gmm.cfdi.supplier.payment.credits"
    _order = "serie, number"
    _description = (
        "Detailed Credits Used by this Payment.")

    payment_id = fields.Many2one(
        'gmm.cfdi.supplier.payment', string='Payment',
        ondelete='cascade')

    credit_id = fields.Many2one(
        'account.invoice', string='Invoice', help='Credit Note Number', ondelete='cascade'
    )

    invoices_applied = fields.Many2many(
        'gmm.cfdi.supplier.payment.invoices',
        'gmm_cfdi_supplier_payment_invoice_credits_rel',
        'payment_credit_id',  'payment_invoice_id', 'Invoices')

    serie = fields.Char(string='Serie', help='Credit Serie')
    number = fields.Integer(string='Number', help='Credit Number')
    uuid = fields.Char(string='UUID', help='Credit UUID')
    amount_credit = fields.Float(string='Credit Amt', help='Credit Total Amount')
    credit_number = fields.Char(compute='_get_invoice_number', string='Credit')

    #@api.depends('invoice_number', 'credit_number', 'amount_invoice',
    #             'amt_inv_residual', 'amt_inv_residual_creditapplied')
    @api.depends('credit_number')
    def _get_invoice_number(self):
        for rec in self:
            serie = rec.serie or '' #if rec.serie.strip() else ''
            serie = (serie.strip() + '-') if serie else ''
            invnumber = str(rec.number) if rec.number else ''
            rec.credit_number = serie + invnumber

        return

    def sum_credits(self, context=None):
        credits = 0
        for rec in self.browse(context):
            credits += rec.amount

        return credits



# END CLASS CFDISupplierPaymentCredits


class CFDINoDoctoRel(models.Model):
    _name = "gmm.cfdi.supplier.payment.credits.notrel"
    _order = "serie, number"
    _description = (
        "Credits Issued wihtout Related Documents")

    partner_id = fields.Many2one(
        'res.partner', string='Supplier', index=True, help='Credits Issued by this Supplier',
        domain=[('supplier', '=', True)])
    payment_id = fields.Many2one(
        'gmm.cfdi.supplier.payment',
        index=True,
        string='Supplier Payment',
        help='Payment where this Credit is applied'
    )

    serie = fields.Char(string='Serie', help='Credit Serie')
    number = fields.Integer(string='Number', help='Credit Number')
    date = fields.Date(string='Date Issued', help='Date issued by Supplier')
    uuid = fields.Char(string='UUID', help='Credit UUID')
    amount = fields.Float(string='Credit Amount', help='Credit Amount Issued')
    name = fields.Char(compute='_get_name', string='Credit Name')

    @api.depends('name')
    def _get_name(self):
        for rec in self:
            serie = rec.serie or ''
            serie = (serie.strip() + '-') if serie else ''
            name = str(rec.number) if rec.number else ''
            rec.name = serie + name
        return

    @api.multi
    @api.onchange('payment_id')
    def onchange_payment_id(self):
        self.payment_id.action_confirm()

    #def onchange_paypment_id(self):
    #     partner_obj = self.pool.get('res.partner')
    #     payment_term_obj = self.pool.get('account.payment.term')
    #     journal_obj = self.pool.get('account.journal')
    #     fiscal_pos_obj = self.pool.get('account.fiscal.position')
    #     val = {}
    #     val['date_maturity'] = False
    #
    #     if not partner_id:
    #         return {'value': val}
    #     if not date:
    #         date = fields.date.context_today(self, cr, uid, context=context)
    #     jt = False
    #     if journal:
    #         jt = journal_obj.browse(cr, uid, journal, context=context).type
    #     part = partner_obj.browse(cr, uid, partner_id, context=context)
    #
    #     payment_term_id = False
    #     if jt and jt in ('purchase', 'purchase_refund') and part.property_supplier_payment_term:
    #         payment_term_id = part.property_supplier_payment_term.id
    #     elif jt and part.property_payment_term:
    #         payment_term_id = part.property_payment_term.id
    #     if payment_term_id:
    #         res = payment_term_obj.compute(cr, uid, payment_term_id, 100, date)
    #         if res:
    #             val['date_maturity'] = res[0][0]
    #     if not account_id:
    #         id1 = part.property_account_payable.id
    #         id2 = part.property_account_receivable.id
    #         if jt:
    #             if jt in ('sale', 'purchase_refund'):
    #                 val['account_id'] = fiscal_pos_obj.map_account(cr, uid, part and part.property_account_position or False, id2)
    #             elif jt in ('purchase', 'sale_refund'):
    #                 val['account_id'] = fiscal_pos_obj.map_account(cr, uid, part and part.property_account_position or False, id1)
    #             elif jt in ('general', 'bank', 'cash'):
    #                 if part.customer:
    #                     val['account_id'] = fiscal_pos_obj.map_account(cr, uid, part and part.property_account_position or False, id2)
    #                 elif part.supplier:
    #                     val['account_id'] = fiscal_pos_obj.map_account(cr, uid, part and part.property_account_position or False, id1)
    #             if val.get('account_id', False):
    #                 d = self.onchange_account_id(cr, uid, ids, account_id=val['account_id'], partner_id=part.id, context=context)
    #                 val.update(d['value'])
    #     return {'value': val}

# END CLASS CFDINoDoctoRel


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    payment_line_invoices = fields.One2many(
        'gmm.cfdi.supplier.payment.invoices',
        'invoice_id', 'Invoice Payments related')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    payments_line_ids = fields.One2many(
        'gmm.cfdi.supplier.payment.line',
        'move_line_id', 'ERP Moves Payments related')


class CFDISupplierPaymentLine(models.Model):
    _name = "gmm.cfdi.supplier.payment.line"
    _order = "move_line_id"
    _description = (
        "Payments done by date. Each linea is payment that its included "
        "in the CFDI Issued by the Supplier.")

    payment_id = fields.Many2one(
        'gmm.cfdi.supplier.payment', string='Payment',
        ondelete='cascade')

    move_line_id = fields.Many2one(
        'account.move.line', string='Journal Entry'
    )

    type = fields.Selection(
        selection=[('payment', 'Payment'),
                   ('credit', 'Credit'),
                   ],
        string='Move Type', default='payment')

    concilied = fields.Boolean('Matched', default=False)
    date = fields.Date(related='move_line_id.date', string='Date')
    amount = fields.Float(related='move_line_id.credit', string='Amount')
    move_name = fields.Char(related='move_line_id.move_id.name', string="Ref")

    # @api.model
    # def _get_move_line_action_window(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'tree,form',
    #         'name': _('Journal Items'),
    #         'res_model': 'account.move.line',
    #         'target': 'current',
    #     }
    #
    # @api.multi
    # def show_move_lines_current(self):
    #     self.ensure_one()
    #     res = self._get_move_line_action_window()
    #     res['domain'] = [('id', 'in', self.current_move_line_ids.ids)]
    #     return res
    #
    # @api.multi
    # def show_move_lines_previous(self):
    #     self.ensure_one()
    #     res = self._get_move_line_action_window()
    #     res['domain'] = [('id', 'in', self.previous_move_line_ids.ids)]
    #     return res

