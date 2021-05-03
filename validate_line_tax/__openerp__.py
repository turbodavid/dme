# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Coded by: Jorge Alfonso Medina Uriarte <jesus.meza@dmesoluciones.com>
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
    "name": "Validate line tax",
    "version": "1.0",
    "author": "DME Soluciones",
    "website" : "http://www.dmesoluciones.com/",
    "category": "accounting, purchase, sale",
    "description": """
    This modules validate the taxes in 'sales, purchases, invoices', you must add tax in the lines.
    """,
    "depends": [      
        "sale", "purchase", "account"
    ],
    "demo_xml": [],
    "data": [],
    "active": False,
    "installable": True,
    "certificate": False,
}
