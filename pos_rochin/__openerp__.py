# -*- coding: utf-8 -*-
{
    'name': 'POS Rochin',
    'version': '1.0.0',
    'category': 'Point Of Sale',
    'sequence': 1,
    'author': 'Jorge Alfonso Medina Uriarte, Cindy Yukie Ley',
    'summary': 'POS modifications code ean',
    'description': """
Numerous modifications of the Point Of Sale :
=============================================

    - Al leer el código de barras con pistola laser y agregar la cantidad automático.

    """,
    'depends': ["base", "account", "point_of_sale"],
    'data': [],
    'qweb': [],
    'js': ['static/src/js/pos_rochin.js'
		],
    'css':[],
    'installable': True,
    'application': False,
    'auto_install': False,
}
