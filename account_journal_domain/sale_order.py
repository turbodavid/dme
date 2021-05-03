# -*- coding: utf-8 -*-
##############################################################################
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://www.dmesoluciones.com/
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

class sale_order(osv.osv):
    _inherit = 'sale.order'

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):        
        if context is None:
            context = {}
        res = super(sale_order, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        #When is form, gets journals with other domain
        if view_type == 'form':
            for field in res['fields']:
                if field == 'shop_id':
                    #user
                    res_user_obj = self.pool.get('res.users').browse(cr, uid, [uid], context)
                    print res_user_obj[0].branch
                    #No tiene asignado no muestra nada
                    if res_user_obj[0].branch is False:
                        res['fields'][field]['domain'] = [('name','=','False')]
                    #    journal_select[:] = [] # vacia la lista
                    elif res_user_obj[0].branch <> "999":
                        res['fields'][field]['domain'] = [('name', 'ilike', res_user_obj[0].branch)]  
                        #for in list
                    #    for journal in sale_shop_select[:]:
                            #if are diferent
                    #        if res_user_obj[0].branch <> journal[1].split('-')[0]:
                    #            sale_shop_select.remove(journal)
                    #res['fields'][field]['selection'] = sale_shop_select
        doc = etree.XML(res['arch'])            
        res['arch'] = etree.tostring(doc)        
        return res
