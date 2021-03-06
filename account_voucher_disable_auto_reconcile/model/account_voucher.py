# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2013 credativ Ltd (<http://credativ.co.uk>).
#    All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class account_voucher(orm.Model):
    _inherit = 'account.voucher'

    def onchange_auto_reconcile(
        self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, 
        date, payment_rate_currency_id, company_id, auto_reconcile, context=None
    ):
        if not journal_id:
            return {}
        if context is None:
            context = {}
        context = context.copy()
        context.update({'auto_reconcile': auto_reconcile })
        res = super(account_voucher, self).onchange_amount(
            cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, 
            date, payment_rate_currency_id, company_id,
            context=context
        )
        return res

    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        '''Default recompute voucher lines over ride to disable auto reconcile feature'''
        default = super(account_voucher,self).recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=context)        
        auto_reconcile = context.get('auto_reconcile')
        if auto_reconcile == None or auto_reconcile == False:
			#Check for invoice and credit lines and avoid disable reconcile if making payment from invoice
			if (ttype == 'receipt' or ttype == 'payment')  and context.get('active_model',False) != 'account.invoice':
				for lines in (default['value']['line_cr_ids'] + default['value']['line_dr_ids']):
					lines['amount'] = 0.0
					lines['reconcile'] = False
				default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)
        return default

    _columns = {
        'auto_reconcile': fields.boolean('Auto Reconcile', help='Reconcile all moves automaticly'),
    }
 
account_voucher()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
