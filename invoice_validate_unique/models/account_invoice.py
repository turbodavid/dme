# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: Jorge Medina jorge.medina@dmesoluciones.com 
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

from openerp.osv import osv
from openerp.tools.translate import _


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

	# Allow to make a duplicate
    def copy(self, cr, uid, id, defaults, context=None):
		#get values
        previous_invoice_number = self.browse(cr, uid, id, context=context).supplier_invoice_number
        type = self.browse(cr, uid, id, context=context).type
        #if type is in_inovice then is supplier invoice
        if type == 'in_invoice':
			new_invoice_number = 'Copy of %s' % previous_invoice_number
			list = self.search(cr, uid, [('name', 'like', new_invoice_number)], context=context)
			if len(list) > 0:
				new_invoice_number = '%s (%s)' % (new_invoice_number, len(list) + 1)
			defaults['supplier_invoice_number'] = new_invoice_number
		#super
        return super(account_invoice, self).copy(cr, uid, id, defaults, context=context)
        
    def _check_account_invoice_number_unique(self, cr, uid, ids, context=None):
        """ Check that the partner and number is unique"""
        if context is None:
            context = {}
		#get values
        account_invoice_brw = self.browse(cr, uid, ids)        
        current_partner_id = account_invoice_brw[0].partner_id.id
        current_supplier_invoice_number = account_invoice_brw[0].supplier_invoice_number
        
        #if type is in_inovice then is supplier invoice
        if account_invoice_brw[0].type =='in_invoice':
			# Check in database
			duplicates = self.browse(cr, uid, self.search(
				cr, uid, [('partner_id', '=', current_partner_id),
				('supplier_invoice_number', '=', current_supplier_invoice_number),
                ('type', '=', 'in_invoice'),
				('id', '!=', account_invoice_brw[0].id)]))
			return not duplicates
        return True

    _constraints = [
        (_check_account_invoice_number_unique,
         _("Error ! Account Invoice must be with an unique value for Partner/Supplier Invoice Number"),
         ['partner_id', 'supplier_invoice_number']), ]
