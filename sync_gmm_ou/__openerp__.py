# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: Jorge Medina jorge.medina@dmesoluciones.com 
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
    "name" : "Sync MORSA",
    "version" : "1.0",
    "author" : "DME Soluciones",
    "category" : "Sync Info MORSA",
    "description" : """This module sync information of BD MORSA to OPENERP.
    Note: You Need to configure this files in server, ask to administrator
        -conexion.csv : Sync Partner/Product
        -conexion_openerp.csv: Sync Policy
""",
    "website" : "http://dmesoluciones.com/",
    "license" : "AGPL-3",
    "depends" : ['account', 'analytic', 'operating_unit'],
    "data" : ["views/sync_view.xml", "views/account_move.xml", "views/account_move_line.xml", "views/operating_unit.xml",
			"security/groups.xml", "security/ir.model.access.csv"],
    "installable" : True,
    "active" : False,
}
