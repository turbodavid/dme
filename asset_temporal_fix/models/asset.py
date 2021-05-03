# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#    Jorge Medina jorge.medina@dmesoluciones.com
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
from datetime import datetime, timedelta
from openerp.tools.translate import _
#import netsvc
import time

class account_asset_fix(osv.TransientModel):
    _name = 'account.asset.fix'
    
    def action_compute_draft(self, cr, uid, ids, context=None):
        # Crea objeto de compra
        account_asset_obj = self.pool.get('account.asset.asset')
        # Obtiene las Compras borrador de la empresa del usuario actual
        asset_ids = account_asset_obj.search(cr, uid, [('state','=','draft'), ('depreciation_next_month', '=', True)])
        #compute board
        res = account_asset_obj.compute_depreciation_board(cr, uid, asset_ids, context=context)
        #validate asset
        account_asset_obj.validate(cr, uid, asset_ids, context=context)
        return True
