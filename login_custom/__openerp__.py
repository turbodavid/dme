# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#	 Coded by:
#			Cindy Yukie Ley Garcia yukieley6@gmail.com
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
	'name' : "Inicio Personalizado",
	'category' : "Test",
	'version' : "1.0",
	'depends' : ['base'],
	'author' : "DME Soluciones",
	'description' : """Personalizacion del Inicio, se toma la imagen de cada empresa de la base de datos y se coloca en el inicio del login """,
 	'qweb': ['static/src/xml/custom.xml'],
	'css' : ['static/src/css/oe_login.css'],
}

