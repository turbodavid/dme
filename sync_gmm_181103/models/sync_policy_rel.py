# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 OpenERP s.a. (<http://openerp.com>).
#
#    DME SOLUCIONES
#    Jorge Medina <jorge.medina@dmesoluciones.com>
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

import time

from openerp import netsvc
from openerp.osv import fields, orm
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp

class sync_morsa_rel(orm.Model):
	_name = 'sync.morsa.rel'
	
	_columns = {
		'account_move_id': fields.integer('Account Move Id'),
		'folio': fields.char('Folio'),
		'account_move_line_id' : fields.integer('Account move line Id'),
		'sync_move_id' : fields.integer('Sync Move Id'),
	}
