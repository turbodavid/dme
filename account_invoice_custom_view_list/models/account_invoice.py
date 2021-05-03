# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
#    Coded by: Jesus Meza (jesus.meza@dmesoluciones.com)
##############################################################################


from openerp.osv import osv, fields
from datetime import datetime, timedelta
from openerp.tools.translate import _

class account_invoice(osv.Model):
    _inherit = "account.invoice"
    
    def _get_parent_date_invoice(self, cr, uid, ids, field_name, arg, context = None):
        res = {}
        
        for account_invoice in self.browse(cr, uid, ids, context = context):
            if account_invoice.parent_id:
                res[account_invoice.id] = account_invoice.parent_id.date_invoice
            else:
                res[account_invoice.id] = None
        
        return res
    
    _columns = {
        'get_parent_date_invoice': fields.function(_get_parent_date_invoice,
                                            type = 'date',
                                            string = 'Parent date invoice',
                                            store = False,
                                            help = "This field indicate the Parent Date Invoice."),
    }

account_invoice()