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
    "name" : "Assing Package",
    "version" : "1.0",
    "author" : "DME Soluciones",
    "category" : "Report",
    "sequence": 16,
    "description" : """This module allows to link a partner with their packages.
			Menu : Almacen->Trazabilidad->Assign Packs""",
    "website" : "http://www.dmesoluciones.com/",
    "license" : "AGPL-3",
    "depends" : ["sale","stock","l10n_mx_invoice_amount_to_text",],
    "data" : ["views/assign_packs_view.xml", 
		"assign_packs_report.xml",
		"report/assign_packs.rml",
		"assign_packs_sequence.xml",
		"security/groups.xml", "security/ir.model.access.csv",],
    "test": [],
    "installable" : True,
    "application": True,
    "active" : False,
}
