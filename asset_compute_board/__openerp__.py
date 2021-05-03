# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
#    Coded by: Jorge Alfonso Medina Uriarte (jorge.medina@dmesoluciones.com)
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
    "name" : "Asset Compute Board",
    "version" : "1.0",
    "author" : "DME Soluciones",
    "category" : "asset",
    "sequence": 16,
    "description" : """This module change compute from base module. When porrata is false:
        override: compute_depreciation_board , its the same code, only a modification in date depreciation: 01-01-purchase year for next month of purchase date.
        
        add function: add_months        
    """,
    "website" : "http://www.dmesoluciones.com/",
    "license" : "AGPL-3",
    "depends" : ["account_asset"],
    "data" : ['views/asset_form.xml'],
    "test": [],
    "installable" : True,
    "application": True,
    "active" : False,
}
