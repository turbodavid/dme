# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
#
#    Jorge Alfonso Medina Uriarte (jorge.medina@dmesoluciones.com)
#	 Cindy Yukie Ley (yukieley6@gmail.com)
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
	'name' : "POS Invoice",
	'category' : "Point Of Sale",
	'version' : "1.0",
	'depends' : ["point_of_sale"],
	'author' : "DME Soluciones",
	'description' : """Poder crear facturas a los pedidos de venta múltiple de punto de venta""",
    'summary': 'POS Order Create Invoice',
	'data' : ['views/point_of_sale_view.xml','security/ir.model.access.csv',],
}
