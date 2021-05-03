# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
#    Jesus Meza (jesus.meza@dmesoluciones.com)
############################################################################
#    Coded by: Jesus Meza (jesus.meza@dmesoluciones.com)
#              Jorge Medina (jorge.medina@dmesoluciones.com)
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
    "name" : "Stock Picking Out Tecnika.",
    "version" : "1.1",
    "author" : "DME Soluciones",
    "category" : "Report",
    "sequence": 15,
    "description" : """This module is a custom report from Stock Picking Out and Electronic Invoice for Tecnika.
""",
    "website" : "http://www.dmesoluciones.com/",
    "license" : "AGPL-3",
    "depends" : ["stock", "l10n_mx_facturae", "report_webkit", "account",],
    "data" : ["views/reports.xml",
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/picking.xml",
        'data/l10n_mx_facturae_report.xml',],
    "test": [],
    "installable" : True,
    "auto_install": False,
}
