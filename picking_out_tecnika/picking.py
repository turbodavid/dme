# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 OpenERP s.a. (<http://openerp.com>).
#
#	 Coded By:
#       Jesus Antonio Meza Espinoza <jesus.meza@dmsoluciones.com>
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

class stock_picking(orm.Model):
    _inherit = "stock.picking"
    
    _columns = {
        'user_authorized': fields.char('Authorized', size=255),
        'user_received': fields.char('Received', size=255),
        }

stock_picking()

class stock_picking_out(orm.Model):
    _inherit = "stock.picking.out"
    
    # Tanto en la clase base de Stock Picking como en el Stock Picking Out
    # se deben agregar las mismas columnas, debido a que si en el base no esta
    # podra guardar en los campos mas no se mostraran en la consulta
    _columns = {
        'user_authorized': fields.char('Authorized', size=255),
        'user_received': fields.char('Received', size=255),
        }

stock_picking_out()
