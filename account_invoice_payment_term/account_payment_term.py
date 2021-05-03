# -*- coding: utf-8 -*-
##############################################################################
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
############################################################################
#   Coded By:
#       Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com
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
from openerp.osv import osv, fields
from openerp.tools.translate import _

class account_payment_term(osv.osv):
    _inherit = 'account.payment.term'

    def compute(self, cr, uid, id, value, date_ref=False, context=None):
        pt = self.browse(cr, uid, id, context=context)
        res = super(account_payment_term,self).compute(cr, uid, id, value, date_ref, context=context)
        if pt.expiration_date:
            result = []
            for r in res:
                t = (pt.expiration_date, r[1])
                result.append(t)
            return result
        else:
            return res

    _columns = {
        'expiration_date': fields.date(string="Expiration Date"),
    }
