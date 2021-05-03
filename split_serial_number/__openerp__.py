# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#    Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com
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
    'name' : "Split Serial Number File",
    'category' : "Stock",
    'version' : "1.0",
    'depends' : ['base','stock'],
    'author' : "DME Soluciones",
    'website' : "http://www.dmesoluciones.com/",
    'description' : """\
    Módulo encargado de subir un archivo con los seriales para separar los productos en las entradas
    """,
    'data' : ['views/stock_view_split_in_lots_inherits.xml','security/ir.model.access.csv'],
    'installable': True,
    'auto_install': False,
}
