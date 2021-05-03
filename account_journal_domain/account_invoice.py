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

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):        
        if context is None:
            context = {}
        res = super(account_invoice, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        #When is form, gets journals with other domain
        if view_type == 'form':
            type = context.get('journal_type', False)
            for field in res['fields']:
                if field == 'journal_id' and type:
                    journal_select = res['fields'][field]['selection']
                    #user
                    res_user_obj = self.pool.get('res.users').browse(cr, uid, [uid], context)
                    #No tiene asignado no muestra nada
                    if res_user_obj[0].branch is False:
                        journal_select[:] = [] # vacia la lista
                    elif res_user_obj[0].branch <> "999":
                        #for in list
                        for journal in journal_select[:]:
                            #if are diferent
                            if res_user_obj[0].branch <> journal[1].split('-')[0]:
                                journal_select.remove(journal)
                    res['fields'][field]['selection'] = journal_select
        doc = etree.XML(res['arch'])            
        res['arch'] = etree.tostring(doc)        
        return res

    def onchange_company_id(self, cr, uid, ids, company_id, part_id, type, invoice_line, currency_id, context = None):
        type2journal = {'out_invoice': 'sale', 'in_invoice': 'purchase', 'out_refund': 'sale_refund', 'in_refund': 'purchase_refund'}
        
        #Funcion Normal
        res = super(account_invoice, self).onchange_company_id(cr, uid, ids, company_id, part_id, type, invoice_line, currency_id)
        #Usuario logueado       
        res_user_obj = self.pool.get('res.users').browse(cr, uid, [uid], context)
        #filtro
        filter= []
        filter.append(('type', '=', type2journal.get(type)))
        if res_user_obj[0].branch is False:
            filter.append(('name', 'ilike', 'False'))
        else:
            #si tiene el branch 999 regresa todo
            if res_user_obj[0].branch in "999":
                return res
            else:
                filter.append(('name', 'ilike', res_user_obj[0].branch))
        #Diarios cargados
        journal_default = []
        for journal in res["domain"]["journal_id"]:
            journal_default = journal[2]
        #Filtro diarios de usuario
        journal_obj = self.pool.get('account.journal')        
        journal_select = journal_obj._name_search(cr, uid, '', filter, context=context, limit=None, name_get_uid=1)
        #Diarios asignados
        journal=[]
        for sel in journal_select:
            journal.append(sel[0])
        #List to Tuple    
        tuple1 = tuple(journal_default)
        tuple2 = tuple(journal)
        #revisa a cuales tiene permiso
        journal = []
        for t in tuple1:
            if t in tuple2:
                journal.append(t)
        #resultado final
        val = {}
        if (len(journal)):
            val['journal_id'] =  journal[0]
        else:
            val['journal_id'] = None
        dom = {'journal_id':  [('id', 'in', journal)]}
        return {'value': val, 'domain': dom}
