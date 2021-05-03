# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2018 Grupo SACSA - http://www.gruposacsa.com.mx
#    All Rights Reserved.
############################################################################
#    Coded by:
#       Jorge Alfonso Medina Uriarte (desarrollo.sacsa@gruposacsa.com.mx)
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
    'name': 'Invoice Report',
    'version': '1.0',
    'license': 'AGPL-3',
    'author': "Grupo SACSA ",
    'website' : "",
    'category': 'report',
    'description': """

        Add Invoice Report

        """,
    'depends': ['account'],
    'init_xml': [],
    'demo': [],
    'data': ['views/invoice_report.xml',
             'report/invoice_report.xml',
             ],
    'installable': True,
    'active:': False,
}
