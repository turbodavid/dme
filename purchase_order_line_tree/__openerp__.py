# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
#    Jesus Meza (jesus.meza@dmesoluciones.com)
############################################################################
#    Coded by: Jesus Meza (jesus.meza@dmesoluciones.com)
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
    "name" : "Purchase Order Line Tree",
    "version" : "1.0",
    "author" : "DME Soluciones",
    "category" : "base", "purchase"
    "description" : """

	This module add price subtotal to purchase order line tree in view.
	The first time it is executed may take about 15 minutes to show the report.

""",
    "website" : "http://www.dmesoluciones.com/",
    "license" : "AGPL-3",
    "depends" : ["base", "purchase"],
    "init_xml" : [],
    "demo_xml" : [],
    "data": ["views/purchase_order_line_tree.xml"],
    "test": [],
    "installable" : True,
}
