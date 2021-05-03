# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
############################################################################
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
    'name' : "Account Invoice Payment Term",
    'version' : "1.0",
    'author' : "DME Soluciones",
    'website' : "http://www.dmesoluciones.com/",
    'category' : "Accounting",
    'summary': 'Accounting, Invoice',
    'description': """
Accounting
==========
This module add a column in payment term for a date of expirition.

    """,
    'depends' : ["account"],
    'data' : ['views/payment_term_form.xml'],
    'installable': True,
    'auto_install': False,
}
