# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2018 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: David Perez davidperez@dmesoluciones.com
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
from openerp import api, models, fields

TAXCODESALE = {'16': 50, '8': 69}

class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    voucher_operating_unit_id = fields.Many2one(
                    'operating.unit',
                    'Operating Unit',
                    required=False,
                    help='Unidad Operativa (sucursal)')

    @api.multi
    def proforma_voucher(self):

        super(AccountVoucher, self).proforma_voucher()
        if self.type == 'receipt':
            self._add_taxes_to_journalentry()

    @api.multi
    def proforma_voucher_tmp(self):
        self.proforma_voucher()

    @api.multi
    def probando(self):
        return "Tengo el valor de: %s " % self.id

    @api.multi
    def cancel_voucher(self):
        move = self.move_id
        if move.state == 'posted':
            move.button_cancel()
            move.write({'state': 'draft'})
        super(AccountVoucher, self).cancel_voucher()
        #self.action_cancel_draft()

        return self.state

    def _add_taxes_to_journalentry(self):

        query = """ """
        query = "select sum(amount_taxes) amount_taxes  \
                 from sync_morsa_refunds  \
                 where voucher_id =  %s and \
                 (invoice_id = 0 or invoice_type != 'in_payment' );" % self.id

        self.env.cr.execute(query)
        res = self.env.cr.dictfetchone()
        taxes = res.get('amount_taxes') or 0

        for vl in self.line_cr_ids:
            if vl.move_line_id.journal_id.code == 'VTANF':
                taxes += round((vl.amount - (vl.amount/1.16)), 2)

        if taxes <= 0:
            return

        tax = self.env['account.tax'].search([('id', '=', TAXCODESALE['16'])])
        aml = self.env['account.move.line']

        aml_ = [tax.account_collected_id.id,
                tax.account_reconcile_id.id]

        for i in range(2):
            header = {
                'partner_id': self.partner_id.id,
                'name': self.number + "/" + self.name,
                'journal_id': self.journal_id.id,
                'account_id': aml_[i],
                'debit': taxes if i == 0 else 0,
                'credit': taxes if i == 1 else 0,
                'operating_unit_id': self.voucher_operating_unit_id.id,
                'company_id': 1,
                'period_id': self.period_id.id,
                'move_id': self.move_id.id,
            }
            aml = aml.create(header)

        return