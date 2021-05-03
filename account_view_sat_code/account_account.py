# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2015 DME Soluciones - http://www.dmesoluciones.com
#    All Rights Reserved.
############################################################################
#    Coded by: Jorge Alfonso Medina Uriarte(jorge.medina@dmesoluciones.com)
############################################################################
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
#import logging
import time
#_logger = logging.getLogger(__name__)

class AccountAccount(orm.Model):
    _inherit = 'account.account'

    def _get_code_sat_group(self, cr, uid, invoice_id, name, args, context=None):
        res = {}
        for account in self.browse(cr, uid, invoice_id, context):
            res[account.id] = account.sat_group_id.code
        return res

    _columns = {
        'code_sat_group_function':fields.function(_get_code_sat_group,
            type='char',
            method=True,
            string='Code SAT Group'
            ),
    }
    _defaults = {
        'code_sat_group_function':'',
    }
