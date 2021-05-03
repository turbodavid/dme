# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Coded by: David Alberto Pérez Payán <david.perez@tecnika.com.mx>
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
    "name": "Plantilla Plan Contable -VEPINSA-",
    "version": "1.0",
    "author": "TNK Erp",
    "website" : "http://www.tecnika.mx/",
    "category": "Localization/Account Charts",
    "description": """
Template account chart for VEPINSA

This Chart of account is a template for VEPINSA company.

This modules and its content will update frequently

    """,
    "depends": [      
        "l10n_mx"
    ],
    "demo_xml": [],
    "data": [
	"data/account_type_vepinsa.xml",
        "data/account_template_vepinsa.xml",
        "data/account_tax_vepinsa.xml",
    ],
    "active": False,
    "installable": True,
    "certificate": False,
}
