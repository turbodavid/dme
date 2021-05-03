# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 OpenERP s.a. (<http://openerp.com>).
#
#    DME SOLUCIONES
#    Jorge Medina <jorge.medina@dmesoluciones.com>
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

from openerp.osv import orm, fields
from datetime import datetime, timedelta
import openerp.netsvc
import time
import os
import psycopg2
from openerp.tools.translate import _

class sync_morsa_conexion(orm.TransientModel):
	_name ='sync.morsa.conexion'
	def _get_conexion(self, filename, dbname):
		# Se lee el archivo de conexcion (no incluido en el branch por cuestiones de seguridad
		BASE_PATH = reduce (lambda l,r: l + os.path.sep + r, os.path.dirname( os.path.realpath( __file__ ) ).split( os.path.sep )[:-1] )
		archi = open(BASE_PATH + '/data/' + filename,'rb')
		linea = archi.readline()
		archi.close()        
		parametros = linea.split(',')        
		print parametros
		if dbname =='':
			dbname = parametros[4]
		return psycopg2.connect("host='%s' port=%s dbname='%s' user='%s' password='%s'"%(parametros[0], parametros[1], dbname, parametros[2], parametros[3].strip())) 


