# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2018 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: David Perez davidperez@dmesoluciones.com
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
from openerp import api, models, fields
from openerp.addons.web.controllers.main import Session

class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    ip_address = fields.Char('IP Address',help='IP Address that holds the database on the branch')

    data_base = fields.Char(
        'Base de Datos',
        help='Poner nombre de la base de datos de donde se sincronizaran las ventas')

    zone = fields.Selection(
        [
            ('occidente', 'Occidente'),
            ('noroeste', 'Noroeste'),
            ('sureste', 'Sureste'),
            ('diesel', 'División Diesel'),
            ('cslthsur', 'CS LTH Sureste'),
            ('cslthnor', 'CS LTH Noroeste/Dgo.'),
        ], 'Zona/División',
            help='Indica la Zona o División a la que pertenece la Sucursal (Uniidad Operativa), dejar en blanco si Corporativo Nacional',
        )

    corporate_ou = fields.Boolean("Es Corporativo?", default=False,
                                help="Indica si la Uidad es un Corporativo Nacional o Regional")

