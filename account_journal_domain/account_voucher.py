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
from lxml import etree

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(account_voucher, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            #type = context.get('journal_type', False)
            for field in res['fields']:
                if field == 'journal_id':
                    #journal_select = res['fields'][field]['selection']
                    ##user
                    res_user_obj = self.pool.get('res.users').browse(cr, uid, [uid], context)                    
                    #No tiene asignado no muestra nada
                    if res_user_obj[0].branch is False:
                        res['fields'][field]['domain'] = [('type','in',['none'])]
                        #journal_select[:] = [] # vacia la lista
                    elif res_user_obj[0].branch <> "999":
                        res['fields'][field]['domain'] = [('type','in',['bank', 'cash']), ('name', 'ilike', res_user_obj[0].branch)]  
                        #for in list
                        #for journal in journal_select[:]:
                            ##if are diferent
                            #if res_user_obj[0].branch <> journal[1].split('-')[0]:
                                #journal_select.remove(journal)
                    else:
                        res['fields'][field]['domain'] = [('type','in',['bank', 'cash'])]  
                    #res['fields'][field]['selection'] = journal_select
        doc = etree.XML(res['arch'])            
        res['arch'] = etree.tostring(doc)
        return res
