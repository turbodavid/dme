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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round
#from openerp.exceptions import UserError
import time

class partner_account_status_report(osv.osv_memory):

    _name = 'partner.account.status.report'
    _columns = {
        #'date_close'    : fields.date('Close date', required=True),
        'date_ini'    : fields.date('Initial date', required=True),
        'date_fin'    : fields.date('Finish date', required=True),
        'company_id'  : fields.many2one('res.company', 'Company', required=True),
        'partner_id'  : fields.many2one('res.partner', 'Partner', required=True),
        'chk_insoluto': fields.boolean('Saldos Insolutos?'),
    }
    _defaults = {
                #'date_close'    : lambda *a: time.strftime('%Y-%m-%d'),
                'date_ini'    : lambda *a: time.strftime('%Y-%m-%d'),
                'date_fin'    : lambda *a: time.strftime('%Y-%m-%d'),
                'chk_insoluto'    : True,
               }
    

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_ini', 'date_fin', 'company_id', 'partner_id', 'chk_insoluto'], context=context)
        res = res and res[0] or {}
        company_obj = self.pool.get('res.company')
        company = company_obj.browse(cr, uid, res['company_id'][0])
        res['logo'] = company[0].logo
        datas['form'] = res
        datas['model'] = 'partner.account.status.report'
        return {
                   'type': 'ir.actions.report.xml',
                   'report_name': 'partner_account_status_report',
                   'datas': datas,
            }   
partner_account_status_report()
