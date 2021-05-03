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
'name' : "Partner MORSA",
'version' : "1.0",
'depends' : ['base'],
'category' : "Partner",
'author' : "Jorge Alfonso Medina Uriarte",
'description' : """\
Agrega una pestaña con informacion extra al cliente para MORSA.
""",
'data' : ['views/res_partner.xml','views/clasificacion.xml'],
'installable': True,
'auto_install': False,
}
