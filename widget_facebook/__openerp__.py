# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#	
#	Coded by:
#	    Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com
#		Cindy Yukie Ley Garcia yukieley6@gmail.com
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
    'name': "WidgetFacebook",
	'author': "DME Soluciones",
    'description': 'Es un modulo donde se crea un widget, donde en un campo se agrega la opcion de darle 		like o compartir desde facebook, para agregar el widget, tenemos que crear en el modulo donde se agregara, un campo en el xml de esta forma : <field name= "share" string= "Share it... :" widget= "WidgetFacebook"/> donde WidgetFacebook es el nombre de nuestro widget a agregar, y en la clase .py se agrega un campo tipo char: "share": fields.char(string="Share"), los nombres de los campos deben coincidir',
    'category': 'Hidden',
    'depends': ['web'],
    'js': ['static/src/js/widget_facebook.js'],
	'qweb':['static/src/xml/template_facebook.xml'],
}
