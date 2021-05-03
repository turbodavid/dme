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
    "name" : "Asset Fix",
    "version" : "1.0",
    "author" : "DME Soluciones",
    "category" : "asset",
    "description" : """This module get all assets in draft and depreciation_next_month = True
        compute the assets and confirm.""",
    "website" : "http://dmesoluciones.com/",
    "license" : "AGPL-3",
    "depends" : ["account_asset", "asset_compute_board"],
    "data" : ["views/asset_fix_view.xml"],
    "installable" : True,
    "active" : False,
}
