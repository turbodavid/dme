# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: César Alfredo Sánchez Beltrán            cesar_sb@hotmail.com
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
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp 

class mrp_bom(orm.Model):
    _inherit = 'mrp.bom'

    _columns = {
        'location_src_id': fields.many2one('stock.location', 'Raw Materials Location', required=True,
            help="Location where the system will look for components."),
        'location_dest_id': fields.many2one('stock.location', 'Finished Products Location', required=True,
            help="Location where the system will stock the finished products."),
    }
