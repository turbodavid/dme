# -*- encoding: utf-8 -*-
# -*- coding: 850 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: Jesus Alfonso Moreno Valdez (alfonso.moreno@pcsystems.mx)
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
import base64
import csv
from openerp import fields, models
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import datetime, time
import openerp.addons.decimal_precision as dp 
from openerp import tools
import os

class journal_expenses(orm.Model):
	_name = 'journal.details'

	_columns = {
				'journal_name' : fields.char('Nombre diario'),
				'id_periodo'   : fields.integer('id periodo'),
				'period_name'  : fields.char('Nombre periodo'),
				'gasto_detallado' : fields.float('Gasto sin impuesto'),
				'id_gasto'     : fields.integer('ID gasto')

			}
