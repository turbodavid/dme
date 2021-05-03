# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Coded by: Jorge Alfonso Medina Uriarte <jorge.medina@dmesoluciones.com>
#	       Jesus Antonio Meza Espinoza <jesus.meza@dmesoluciones.com>
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
    "name": "Plantilla Plan Contable -CONyMAT-",
    "version": "1.0",
    "author": "DME Soluciones",
    "website" : "http://www.dmesoluciones.com/",
    "category": "Localization/Account Charts",
    "description": """
Template account chart for CONyMAT

This Chart of account is a template for CONyMAT company.

This modules and its content will update frequently

    """,
    "depends": [      
        "l10n_mx"
    ],
    "demo_xml": [],
    "data": [
	"data/account_type_conymat.xml",
        "data/account_template_conymat.xml",
        "data/account_tax_conymat.xml",
    ],
    "active": False,
    "installable": True,
    "certificate": False,
}
