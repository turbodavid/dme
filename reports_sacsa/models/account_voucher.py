# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 OpenERP s.a. (<http://openerp.com>).
#
#    Coded By:
#       Jorge Alfonso Medina Uriarte (jorge.medina@dmesoluciones.com)
#		Jesus Antonio Meza Espinoza (jesus.meza@dmesoulciones.com)
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

from openerp.osv import osv,fields
from openerp.tools.translate import _
from openerp.tools.amount_to_text_en import amount_to_text
from lxml import etree

class account_voucher(osv.osv):
	_inherit = 'account.voucher'

	_columns={
		'account_bank_statement_id':fields.many2one('account.bank.statement', 'Bank Statement',readonly=True, states={'draft':[('readonly',False)]}),
        'print_legend_policy': fields.boolean(string = "Print Legend in Policy",
                                              help=_("Determine if shows the legend \'Amount to pay the beneficiary\' only in policy.")
                                            )
	}
	_defaults = {
        'print_legend_policy': lambda *a: False,
    }
	
	def onchange_payment_beneficiary(self, cr, uid, ids, payment_beneficiary, context=None):
		if not payment_beneficiary:
			return {
        		'value': {
            		'print_legend_policy':False
				}
			}
		else:
			return True
		
	#overwrite method
	def proforma_voucher(self, cr, uid, ids, context=None):
		for voucher in self.browse(cr, uid, ids, context=context):
			#if dont select an account_bank statement, follows the normal way
			if not voucher.account_bank_statement_id:
				self.action_move_line_create(cr, uid, ids, context=context)
			else:
				#if true, get a sequence and posted the voucher
				# we select the context to use accordingly if it's a multicurrency case or not
				if context is None:
					context = {}
				context = self._sel_context(cr, uid, voucher.id, context)
				#get the move without create
				move = self.account_move_get(cr, uid, voucher.id, context=context)
				# We post the voucher.
				self.write(cr, uid, [voucher.id], {
					'state': 'posted',
					'number': move['name'],
				})
		return True
	
	def print_check(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		return {
			'name' : _('Account Voucher Check Print'),
			'type': 'ir.actions.act_window',
			'res_model': 'account.voucher.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [(False, 'form')],
			#'res_id': ids[0],
			'target': 'new',
			'context':  context,
			#'nodestroy':True,
		 }

	#we use bottom for check print
	def print_wizard_check(self, cr, uid, ids, context=None):
		if not ids:
			return  {}
		return {
			'type': 'ir.actions.report.xml', 
			'report_name': 'account.print.check.bottom',
			'datas': {
					'model':'account.voucher',
					'id': ids and ids[0] or False,
					'ids': ids and ids or [],
					'report_type': 'pdf'
				},
			'nodestroy': True
			}    
            
	#we use top for payment print
	def print_payment(self, cr, uid, ids, context=None):
		if not ids:
			return  {}
		return {
			'type': 'ir.actions.report.xml', 
			'report_name': 'account.print.check.top',
			'datas': {
					'model':'account.voucher',
					'id': ids and ids[0] or False,
					'ids': ids and ids or [],
					'report_type': 'pdf'
				},
			'nodestroy': True
			}   

	def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
		"""
			Add domain 'allow_check_writting = True' on journal_id field and remove 'widget = selection' on the same
			field because the dynamic domain is not allowed on such widget
		"""
		if not context: context = {}
		res = super(account_voucher, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		nodes = doc.xpath("//field[@name='journal_id']")
		
		if context.get('write_check', False) :
			for node in nodes:
				node.set('domain', "[('type', '=', 'bank'), ('allow_check_writing','=',True)]")
				node.set('widget', '')
			res['arch'] = etree.tostring(doc)
		else: #remove widget supplier, client payment
			for node in nodes:
				node.set('widget', '')
			res['arch'] = etree.tostring(doc)
		return res


class account_voucher_wizard(osv.TransientModel):
	_name = 'account.voucher.wizard'

	def default_get(self, cr, uid, fields, context=None):
		res = {}
		#get active id
		active_id = context and context.get('active_id')
		#get record
		account_voucher = self.pool.get('account.voucher').browse(cr, uid, [active_id], context=context)
		#update default
		res.update({'name': account_voucher[0].partner_id.name })
		return res

	def print_wizard_check(self, cr, uid, ids, context=None):
		#get active id for send id of voucher and not of wizard
		ids = context and context.get('active_ids')		
		#send to print check
		return self.pool.get('account.voucher').print_wizard_check(cr, uid, ids, context=context)
	
	_columns={
		'name':fields.char('Beneficiary Name', size=255),
	}
