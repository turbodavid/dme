# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 DME Soluciones - http://www.dmesoluciones.com/
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
    'name' : "Account Replicate",
    'version' : "1.0",
    'author' : "DME Soluciones",
    'website' : "http://www.dmesoluciones.com/",
    'category' : "Accounting",
    'summary': 'Accounting, Replicate',
    'description': """
Accounting
==========
Module for replicate account, when an account is check how replicate, the module will replicate the fields for all companies.
    """,
    'depends' : ["account"],
    'data' : ['view/account_account_view.xml','view/res_company.xml'],
    'installable': True,
    'auto_install': False,
}
