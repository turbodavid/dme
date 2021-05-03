# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
############################################################################
#    Coded by:
#	Jorge Medina (jorge.medina@dmesoluciones.com)
#	Jesus Meza   (jesus.meza@dmesoluciones.com)
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
    "name" : "SACSA Reports",
    "version" : "1.0",
    "author" : "DME Soluciones",
    "category" : "Report",
    "sequence": 15,
    "description" : """This module add custom reports for SACSA.""",
    "website" : "http://www.dmesoluciones.com/",
    "license" : "AGPL-3",
    "depends" : ["l10n_mx_facturae", "report_webkit", "account", "account_voucher", "account_check_writing"],
    "data" : ['data/l10n_mx_facturae_report.xml','data/res_partner_mod.xml', 'data/mod97.xml', 
			'views/reports.xml', 'views/account_journal.xml', 'security/ir.model.access.csv', 
			'report/check_print_sacsa_report.xml', 
			'views/account_voucher.xml', 
			'views/account_voucher_view.xml',
			'views/account_voucher_wizard.xml',
			'report/account_print_invoice.xml'],
    "test": [],
    "installable" : True,
    "auto_install": False,
}
