# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: David Alberto Pérez Payán <davidperez@dmesolucioes.com>
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
{
    'name': 'Complete Sales Margin',
    'version': '1.0',
    'license': 'AGPL-3',
    'author': "DME Soluciones",
    'website' : "",
    'category': 'sales',
    'description': """

 		Data for complete sales form with gross margin

		""",
    'depends': ['message_box'],
    'init_xml': [],
    'demo': [],
    'data': ['views/complete_sales_margin_view.xml'],
    'installable': True,
}
