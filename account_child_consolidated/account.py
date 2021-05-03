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

class account_account(osv.osv):
    _inherit = 'account.account'
    
    def _get_children_and_consol(self, cr, uid, ids, context=None):
        #region 
        #Separate in 1000 for account consolidated very large
        split_args = []
        if isinstance(ids, list):        
            split_size = 1000
            for i in range(len(ids)/split_size+1):
                split_args.append(ids[:])
                split_args[i] = ids[split_size*i:split_size*(i+1)]

        ids2 = []
        if split_args:
            results = []
            for arg in split_args:
                results.extend(self.search(cr, uid, [('parent_id', 'child_of', arg)], context=context))
            ids2 = list(results)
        else:
            ids2 = self.search(cr, uid, [('parent_id', 'child_of', ids)], context=context)                                                
        #endregion         
        #this function search for all the children and all consolidated children (recursively) of the given account ids
        #ids2 = self.search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        ids3 = []
        for rec in self.browse(cr, uid, ids2, context=context):
            for child in rec.child_consol_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_consol(cr, uid, ids3, context)
        return ids2 + ids3
