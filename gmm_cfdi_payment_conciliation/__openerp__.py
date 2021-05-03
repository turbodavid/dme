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
    'name': 'GMM CFDI Payment Conciliation',
    'version': '1.0',
    'license': 'AGPL-3',
    'author': "PC Systems",
    'website' : "",
    'category': 'GMM',
    'description': """

        GMM CFDI Payment Conciiation

        """,
    'depends': ['account'],
    'init_xml': [],
    'demo': [],
    'data': [	'views/gmm_cfdi_payment_conciliation_view.xml',
                 'views/gmm_cfdi_payment_conciliation_menu.xml',
                 'wizard/gmm_cfdi_payment_conciliation_wizard.xml',
                 'security/ir.model.access.csv'
	],
    'installable': True,
    'active:': False,
}
