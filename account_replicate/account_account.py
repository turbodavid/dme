# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
############################################################################
#    Coded by: Jorge Medina (jorge.medina@dmesoluciones.com)
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

from openerp.osv import fields, orm
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

#Constants
UID_ADMIN = 1
COMPANY_ID_MAIN = None # For company that create the account
PARENT_ID_MAIN = None # For company that create the account
REPLICATE_MAIN = False

class account_account(orm.Model):
    _inherit = 'account.account'
    _columns = {
        'replicate': fields.boolean('Replicate', help='Replicate the account for all companies.'),
    }

    def write(self, cr, uid, ids, vals, context=None):
        if not 'no_update' in vals:
            #copy vals
            account_account_obj_list = self.pool.get('account.account').browse(cr, UID_ADMIN, ids, context=context)            
            vals_copy = vals
            parent_id = False
            account_account_obj = None
            for account_account_obj in account_account_obj_list:
                if not 'replicate' in vals:
                    REPLICATE_MAIN = account_account_obj.replicate
                else:
                    REPLICATE_MAIN = vals["replicate"]
                COMPANY_ID_MAIN = account_account_obj.id #Use "Id" from account in COMPANY_ID_MAIN            
            if REPLICATE_MAIN:
                #Get parent id from account to replicate
                if 'parent_id' in vals:
                    parent_id = vals["parent_id"]
                    PARENT_ID_MAIN =  vals["parent_id"]
                else:
                    PARENT_ID_MAIN = None
                if parent_id:
                    account_account_obj_principal = self.pool.get('account.account').browse(cr, UID_ADMIN, parent_id, context=context)
                #Get Ids accounts
                ids_account_account = self.pool.get('account.account').search(cr, uid, [("code", "=", account_account_obj.code)])
                #for all accounts
                for id_account_account in ids_account_account:
                    print 'iterando', id_account_account
                    if id_account_account != COMPANY_ID_MAIN:
                        vals_copy.update(no_update = "1")#para la recursividad
                        #Id account account
                        ids = [id_account_account]
                        #get parent id                         
                        if parent_id:
                            #get account in iteration for get the company_id field
                            account_account_child = self.pool.get('account.account').browse(cr, UID_ADMIN, ids, context=context)
                            if len(account_account_child)>0:                            
                                parent_id_account_account = self.pool.get('account.account').search(cr, uid, [("code", "=", account_account_obj_principal.code), ("company_id","=",account_account_child[0].company_id.id)])
                                #set parent id
                                if len(parent_id_account_account)>0:
                                    vals_copy["parent_id"] = parent_id_account_account[0]
                                else:
                                    vals_copy["parent_id"]  = None
                        #Create account
                        account_account_id = self.pool.get('account.account').write(cr, UID_ADMIN, ids, vals_copy, context=context)
                #Update chart account
                if parent_id:
                    parent_id_account_template = self.pool.get('account.account.template').search(cr, uid, [("code", "=", account_account_obj_principal.code)])
                    if len(parent_id_account_template)>0:
                        vals_copy.update(parent_id = parent_id_account_template[0])
                    else:
                        vals_copy.update(parent_id = None)
                        
                ids_account_account_template = self.pool.get('account.account.template').search(cr, UID_ADMIN, [("code", "=", account_account_obj.code)])
                account_account_template_id = self.pool.get('account.account.template').write(cr, UID_ADMIN, ids_account_account_template, vals_copy, context=context)
                
                #Update account principal with company id main.
                ids = [COMPANY_ID_MAIN]      
                if parent_id:          
                    vals.update(parent_id = str(PARENT_ID_MAIN))
        return super(account_account, self).write(cr, uid, ids, vals, context)

    def create(self, cr, uid, vals, context=None):
        if not 'no_create' in vals:
            #copy vals
            vals_copy = vals
            COMPANY_ID_MAIN = vals["company_id"]
            PARENT_ID_MAIN =  vals["parent_id"]
            REPLICATE_MAIN = False
            #Get res_company
            res_company_obj = self.pool.get('res.company').browse(cr, UID_ADMIN, COMPANY_ID_MAIN, context=context)
            if not res_company_obj.chart_template_id:
                raise orm.except_orm(
                        _('Error'),
                        _(u"Company without chart template. \nGo to Configuración->Compañias->Compañias (TAB Configuración-Contabilidad-Chart Template)")
                    )
            if 'replicate' in vals:
                REPLICATE_MAIN = vals["replicate"]
            if REPLICATE_MAIN:
                #Get parent id from account to replicate
                parent_id = vals["parent_id"]
                if parent_id:
                    account_account_obj = self.pool.get('account.account').browse(cr, UID_ADMIN, parent_id, context=context)
                #Get Ids res company
                ids_res_company = self.pool.get('res.company').search(cr, uid, [])
                #for all companies
                for id_res_company in ids_res_company:
                    if id_res_company != COMPANY_ID_MAIN:
                        #change company_id field
                        vals_copy.update(company_id = str(id_res_company))
                        vals_copy.update(no_create = "1") #para la recursividad
                        #get parent id                         
                        if parent_id:
                            parent_id_account_account = self.pool.get('account.account').search(cr, uid, [("code", "=", account_account_obj.code), ("company_id","=",id_res_company)])                        
                            #set parent id
                            if len(parent_id_account_account)>0:
                                vals_copy["parent_id"] = parent_id_account_account[0]
                            else:
                                vals_copy["parent_id"]  = None
                        #Create account
                        account_account_id = self.pool.get('account.account').create(cr, UID_ADMIN, vals_copy, context=context)
                #Update account template
                vals_copy.update(chart_template_id = res_company_obj.chart_template_id.id)
                #get parent id template
                if parent_id:
                    parent_id_account_template = self.pool.get('account.account.template').search(cr, uid, [("code", "=", account_account_obj.code)])
                    if len(parent_id_account_template)>0:
                        vals_copy.update(parent_id = parent_id_account_template[0])
                    else:
                        vals_copy.update(parent_id = None)
                #Create 
                account_account_template_id = self.pool.get('account.account.template').create(cr, UID_ADMIN, vals_copy, context=context)
                #Update account principal with company id main.
                vals.update(company_id = str(COMPANY_ID_MAIN))
                vals.update(parent_id = str(PARENT_ID_MAIN))
        return super(account_account, self).create(cr, uid, vals, context)
