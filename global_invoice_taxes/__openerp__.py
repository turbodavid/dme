# -*- coding: utf-8 -*-
# Copyright 2018 PC systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Global Invoice Taxes',
    'description': """
        Global invoice for daily group by taxes for daily sales""",
    'version': '1.0.0',
    'category': 'Point Of Sale',
    'license': 'AGPL-3',
    'author': 'PC systems',
    'depends': [
        'pos_invoice_posted',
    ],
    'data': [
        'views/create_invoice.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
