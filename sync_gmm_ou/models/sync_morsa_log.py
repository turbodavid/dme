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

from openerp.osv import orm, fields
from datetime import datetime, timedelta
import openerp.netsvc
import time
from openerp.tools.translate import _

class sync_morsa_log(orm.Model):
    _name ='sync.morsa.log'
    _columns = {
        'period': fields.char('Period'),
        'folio': fields.char('Folio'),
        'message': fields.char('Message'),
        'account_contpaq': fields.char('Account Contpaq'),
        'db': fields.char('db'),
    }

class sync_morsa_log_generic(orm.Model):
    _name ='sync.morsa.log.generic'
    _columns = {
        'morsa_code': fields.char('Morsa Code'),
        'openerp_code': fields.char('OpenERP Code'),
        'name': fields.char('name'),
        'message': fields.char('Message')
    }