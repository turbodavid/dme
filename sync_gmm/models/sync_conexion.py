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

from openerp.addons.web.controllers.main import Session
from openerp.osv import orm, fields
from datetime import datetime, timedelta
import openerp.netsvc
import time
import os
import psycopg2
import psycopg2.extras
from openerp.tools.translate import _

ENTERPRISE = {'GMM':'culiacan', 'MOR':'mayoreo', 'VOH':'vohcom', 'desarrollo':'contpaq_morsa_desarrollo'}

class sync_morsa_conexion(orm.TransientModel):
	_name ='sync.morsa.conexion'

	def _get_enterprise_used(self):
		sesion = Session()
		informacion = sesion.get_session_info()
		bd = informacion.get('db')

		return bd[0:3]

	def _get_conexion(self, filename='conexion_openerp_expense.csv', dbname=None):
		# Se lee el archivo de conexcion (no incluido en el branch por cuestiones de seguridad

		if not dbname:
			dbname = ENTERPRISE[self._get_enterprise_used()]

		BASE_PATH = reduce (lambda l,r: l + os.path.sep + r, os.path.dirname( os.path.realpath( __file__ ) ).split( os.path.sep )[:-1] )
		archi = open(BASE_PATH + '/data/' + filename,'rb')
		linea = archi.readline()
		archi.close()        
		parametros = linea.split(',')        
		#print parametros
		if dbname == '':
			dbname = parametros[4]

		return psycopg2.connect("host='%s' port=%s dbname='%s' user='%s' password='%s'"%(parametros[0], parametros[1], dbname, parametros[2], parametros[3].strip()))

	def _get_conexion_direct(self, host, dbname, port=5432, user='kerberox', password='204N1tN3L@V19'):
		return psycopg2.connect("host='%s' port=%s dbname='%s' user='%s' password='%s'" % (
						host, port, dbname, user, password))

	def get_direct_connection(self, host, dbname, port=5432, user='kerberox', password='204N1tN3L@V19'):
		return self._get_conexion_direct(host, dbname, port, user, password)

	def get_dict_cursor(self):
		cn = self._get_conexion()
		return cn.cursor(cursor_factory=psycopg2.extras.DictCursor)