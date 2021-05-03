# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
############################################################################
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
    "name" : "Tree View Account Code SAT Group",
    "version" : "1.0",
    "author" : "DME Soluciones",
    "category" : "account_account",
    "description" : """This module add column 'Code SAT' in tree view from accounts.""",
    "website" : "http://www.dmesoluciones.com/",
    "license" : "AGPL-3",
    "depends" : ["account"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["views/account_account_code_sat.xml"],
    "test": [],
    "installable" : True,
    "active" : False,
}
