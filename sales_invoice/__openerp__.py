# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
#    Jesus Meza (jesus.meza@dmesoluciones.com)
############################################################################
#    Coded by: César Alfredo Sánchez Beltrán    
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
    "name" : "Sales Invoice",
    "version" : "1.0",
    "author" : "DME Soluciones",
    "category" : "base", "sale"
    "description" : """	This module add the sales team to the invoice for each salesman """,
    "website" : "http://www.dmesoluciones.com/",
    "license" : "AGPL-3",
    "depends" : ["base", "sale"],
    "data": ["views/sale_invoice.xml"],
    "test": [],
    "installable" : True,
}
