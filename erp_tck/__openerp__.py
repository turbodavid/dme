# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
############################################################################
#    Coded by: Jorge Alfonso Medina Uriarte(jorge.medina@dmesoluciones.com)
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
    'name' : "ERP TCK",
    'version' : "1.0",
    'author' : "DME Soluciones",
    'website' : "http://www.dmesoluciones.com/",
    'category' : "Sale",
    'summary': 'Sales Orders, Invoices, Warehouses, Leads',
    'description': """
Module personalizado para TECNIKA (ERP Web)
===========================================

* This module add new features for the process of TECNIKA's Company.

    """,
    'depends' : ["account","sale", "mrp", "sale_margin","stock"],
    'data' : ["views/erp_view.xml", "views/account_invoice_with_shipped.xml", "report/l10n_mx_facturae_report.xml","report/l10n_mx_facturae_report_header.xml"],
    'installable': True,
    'auto_install': False,
}
