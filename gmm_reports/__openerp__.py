# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2019 Grupo MORSA - http://www.morsa.com.mx
#    All Rights Reserved.
############################################################################
#    Coded by:
#       David Alberto Perez Payán (davidperez@dmesoluciones.com)
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
    'name': 'GMM Reports',
    'version': '1.0',
    'license': 'AGPL-3',
    'author': "DME ",
    'website' : "",
    'category': 'report',
    'description': """

        Reportes para GMM

        """,
    'depends': ['account', 'sync_gmm', 'account_balance_reporting', ],
    'init_xml': [],
    'demo': [],
    'data': ['views/bank_moves_report.xml',
             'views/employee_expenses_report.xml',
             'report/bank_moves_report.xml',
             'report/employee_expenses_report.xml',
              'report/res_partner_xlsx_report.xml',
             ],
    'installable': True,
    'active:': False,
}
