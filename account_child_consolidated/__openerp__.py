# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
############################################################################
#    Coded by: Yukie Ley (cindy.ley@dmesoluciones.com)
#    Coded by: Jorge Medina (jorge.medina@dmesoluciones.com)
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
    'name' : "Account Child Consolidated",
    'version' : "1.0",
    'author' : "DME Soluciones",
    'website' : "http://www.dmesoluciones.com/",
    'category' : "Accounting",
    'summary': 'Accounting, Consolidated',
    'description': """
Accounting
==========
Module for account consolidated very large, when chart of account has a many account consolidated, posgresql doesn't process the query, this throw a error : Memory exhausted, you can tune postgres but don't fix this error.

This module you can use when the option "Contabilidad/Planes Contables/Plan Contable" don't show the information to Corporative level.

	""",
	'depends' : ["account"],
	'data' : [],
    'installable': True,
    'auto_install': False,
}
