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
#from openerp import models, fields, api, exceptions, tools 
from datetime import datetime, timedelta
from StringIO import StringIO
import openerp.netsvc
import glob
import os.path
import time
import psycopg2
import xmlrpclib
from openerp.tools.translate import _
import os
#log
import logging
import base64
import zipfile
_logger = logging.getLogger(__name__)

COMPANY_ID_MOR = 1
ENTERPRISE = {'GMM':'contpaq_openerp_morsa_gmm', 'MOR':'contpaq_openerp_morsa_mor', 'VOH':'contpaq_openerp_morsa_voh', 'desarrollo':'contpaq_morsa_desarrollo'}
import sync_conexion
class sync_morsa_hr(orm.Model):
	_name = "sync.morsa.hr"
	_columns = {
	'period': fields.char('Period', size=6, help='mmaaaa'),
	'enterprise':fields.char('Enterprise', help='Write the code for enterprise \nGMM: contpaq_openerp_morsa_gmm \nMOR: contpaq_openerp_morsa_mor \nVOH: contpaq_openerp_morsa_voh\n Example: GMM'),
	'file_zip': fields.binary('File Zip'),
	'checkbox': fields.boolean('SUA')	
	}

	def action_sync_hr(self, cr, uid, ids, context=None):
		obj_hr = self.pool['sync.morsa.hr'].browse(cr, uid, ids[0], context=context)
		bdname = ''
		period = ''
		#get values
		for record in self.browse(cr,uid,ids,context=context):
		    dbname = record.enterprise.upper()
		    period = record.period
		    period = period[:2] + "/" + period[2:]
		_logger.debug("DB: %s" % dbname)
		if dbname not in ENTERPRISE:
		     raise osv.except_osv(_("Sym GMM"), _("write a enterprise correct."))
		#get db
		dbname = ENTERPRISE[dbname]
		#get conexion
		#conexion = self._get_conexion("conexion_openerp.csv", dbname)
		conexion = self.pool.get('sync.morsa.conexion')._get_conexion("conexion_openerp.csv", dbname)
		cursor = conexion.cursor()
		"""
		@save_path = ruta donde se guardara el archivo leido desde el campo binario en la aplicacion ODOO
		@extracth_path = ruta donde se van a extraer los archivos de la ruta @save_path ya que se genera un archivo .zip
						 en esta ultima ruta, la variable @extracth_path se utilizara tambien para cuando
						 acabe el proceso de lectura de los archivos, al final borre los archivos del
						 directorio establecido en esta variable
		"""
		save_path = '/home/morsadmin/nomina_txt.zip'
		#save_path = '/home/administrador/Documents/nomina_morsa_txt.zip'
		extract_path = '/home/morsadmin/archivos_extraidos'
		#extract_path = '/home/administrador/Documents/archivos_extraidos'
		file = obj_hr.file_zip
		decoding_file = base64.decodestring(file)
		archive = open(save_path, 'wb')
		archive.write(decoding_file)
		archive.close()
		zip_ref = zipfile.ZipFile(save_path, 'r')
		zip_ref.extractall(extract_path)
		zip_ref.close()
		"""
		@path donde se leeran todos los archivos TXT sacados del archivo .zip que se guarda en la variable
		@save_path
		"""
		path = '/home/morsadmin/archivos_extraidos/*.txt'
		#path = '/home/administrador/Documents/archivos_extraidos/*.txt'
		"""Se usa el modulo glob para poder leer todos los archivos TXT 
		   en una carpeta, para poder utilizar esta libreria se tiene que instalar el modulo glob en la instancia virtual
		   y despues importarla en la clase como se muestra arriba
		   La funcion glob inserta la ruta completa con el nombre de cada archivo al final en un arreglo
		   cada ruta es un elemento en el arreglo
		   @files_txt = variable que se le asigna el arreglo de los archivos recorridos en la ruta establecida
		"""
		files_txt = glob.glob(path)
		if files_txt:
			pass
		else:
			#path = '/home/administrador/Documents/archivos_extraidos/*.TXT'
			path = '/home/morsadmin/archivos_extraidos/*.TXT'
			files_txt = glob.glob(path)
		"""
			Se declaran las instancias de los objetos que utilizaremos
		"""
	 	account_move_obj = self.pool.get('account.move')
	 	account_move_line_obj = self.pool.get('account.move.line')
	 	account_period_obj = self.pool.get('account.period')
	 	for file in files_txt:
	 		#print"Archivo leido: ", file
	 		with open (file, 'r') as archivo:
	 			for linea in archivo.readlines():
	 				if linea.strip():
	 					if 'P' in linea[0:1]:
							query_2 = ("select fn_get_journal_id_hr('%s','%s')"%(linea[13:21], linea[11:12]))
							cursor.execute(query_2)
							reg_1 = cursor.fetchall()
							date = linea[2:6] + '/' + linea[6:8] + '/' + linea[8:10].strip()
							period_id = account_period_obj.search(cr, uid, [('company_id', '=', COMPANY_ID_MOR), ("code",'=', period)])[0]
							header = {
							    'date':date,
							    'journal_id':reg_1[0][0],
							    'ref':linea[13:21],
							    'company_id': COMPANY_ID_MOR,
							    'period_id':period_id
							}
							obj_policy = account_move_obj.create(cr, uid, header, context = context)
						elif 'M' in linea[0:1]:
							cuenta = linea[2:5] + '-' + linea[5:7] + '-' + linea[7:10] + '-' + linea[10:12].strip()
							query_3 = ("select s.c_contpaq,s.id_partner,s.id_ou,s.id_open,s.id_ananew from sync_contpaq_openerp_rel s where s.c_contpaq = '%s'"% (cuenta))
							cursor.execute(query_3)
							reg_2 = cursor.fetchall()
							if '1' in linea[34:35]:
								debit = float(linea[44:52])
								credit = 0
								#si debito viene negativo es un credito
								if debit < 0:
									credit = debit * -1
									debit = 0
								update_detalle={
									'name': linea[2:11]+'-'+linea[73:89].strip(),
									'partner_id':reg_2[0][1],
									'account_id':reg_2[0][3],
									'analytic_account_id': reg_2[0][4],
									'operating_unit_id':reg_2[0][2],
									'debit':debit,
									'credit':credit,
									'move_id': obj_policy
								}
								obj_line = account_move_line_obj.create(cr, uid, update_detalle, context=context)
							elif '2' in linea[34:35]:
								#Si credito viene en negativo es un debito
								credit = float(linea[44:52])
								debit = 0
								if credit < 0:
									debit = credit * -1
									credit = 0
								update_detalle={
									'name': linea[2:11]+'-'+linea[73:89].strip(),
									'partner_id':reg_2[0][1],
									'account_id':reg_2[0][3],
									'analytic_account_id': reg_2[0][4],
									'operating_unit_id':reg_2[0][2],
									'debit':debit,
									'credit':credit,
									'move_id': obj_policy
								}
								obj_line = account_move_line_obj.create(cr, uid, update_detalle, context=context)
	 	"""
	 	Proceso de borrado de los archivos que se guardaron en la ruta establecida de la variable @extracth_path
	 	para que no cause conflictos con los nuevos archivos que se generaran cada vez que se corra el proceso
	 	"""
	 	file_list = os.listdir(extract_path)
	 	for item in file_list:
	 		os.remove(os.path.join(extract_path, item))
	 #Metodo que aplica la logica para los archivos de nomina SUA de MORSA
	def action_sync_hr_usus(self, cr, uid, ids, context=None):
	 	obj_hr = self.pool['sync.morsa.hr'].browse(cr, uid, ids[0], context=context)
	 	bdname = ''
	 	period = ''
	 	#get values
	 	for record in self.browse(cr,uid,ids,context=context):
	 	    dbname = record.enterprise.upper()
	 	    period = record.period
	 	    period = period[:2] + "/" + period[2:]
	 	_logger.debug("DB: %s" % dbname)
	 	if dbname not in ENTERPRISE:
	 	     raise osv.except_osv(_("Sym GMM"), _("write a enterprise correct."))
	 	#get db
	 	dbname = ENTERPRISE[dbname]
	 	#get conexion
	 	#conexion = self._get_conexion("conexion_openerp.csv", dbname)
	 	conexion = self.pool.get('sync.morsa.conexion')._get_conexion("conexion_openerp.csv", dbname)
	 	cursor = conexion.cursor()
	 	"""
	 	@save_path = ruta donde se guardara el archivo leido desde el campo binario en la aplicacion ODOO
	 	@extracth_path = ruta donde se van a extraer los archivos de la ruta @save_path ya que se genera un archivo .zip
	 					 en esta ultima ruta, la variable @extracth_path se utilizara tambien para cuando
	 					 acabe el proceso de lectura de los archivos, al final borre los archivos del
	 					 directorio establecido en esta variable
	 	"""
	 	#save_path = '/home/administrador/Documents/nomina_txt.zip'
	 	save_path = '/home/morsadmin/nomina_txt_sua.zip'
	 	#extract_path = '/home/administrador/Documents/archivos_extraidos'
	 	extract_path = '/home/morsadmin/archivos_extraidos'
	 	file = obj_hr.file_zip
	 	decoding_file = base64.decodestring(file)
	 	archive = open(save_path, 'wb')
	 	archive.write(decoding_file)
	 	archive.close()
	 	zip_ref = zipfile.ZipFile(save_path, 'r')
	 	zip_ref.extractall(extract_path)
	 	zip_ref.close()
	 	"""
	 	@path donde se leeran todos los archivos TXT sacados del archivo .zip que se guarda en la variable
	 	@save_path
	 	"""
	 	#path = '/home/administrador/Documents/archivos_extraidos/*.txt'
	 	path = '/home/administrador/Documents/*.txt'
	 	"""Se usa el modulo glob para poder leer todos los archivos TXT 
	 	   en una carpeta, para poder utilizar esta libreria se tiene que instalar el modulo glob en la instancia virtual
	 	   y despues importarla en la clase como se muestra arriba
	 	   La funcion glob inserta la ruta completa con el nombre de cada archivo al final en un arreglo
	 	   cada ruta es un elemento en el arreglo
	 	   @files_txt = variable que se le asigna el arreglo de los archivos recorridos en la ruta establecida
	 	"""
	 	files_txt = glob.glob(path)
	 	if files_txt:
			pass
		else:
			#path = '/home/administrador/Documents/archivos_extraidos/*.TXT'
			path = '/home/administrador/Documents/*.TXT'
			files_txt = glob.glob(path)
	 	"""
	 		Se declaran las instancias de los objetos que utilizaremos
	 	"""
	 	account_move_obj = self.pool.get('account.move')
	 	account_move_line_obj = self.pool.get('account.move.line')
	 	account_period_obj = self.pool.get('account.period')
	 	for file in files_txt:
	 	    with open (file, 'r') as archivo:
	 	        for linea in archivo.readlines():
	 		        if linea.strip():
	 		            if 'P' in linea[0:1]:
	 		            	query_2 = ("select fn_get_journal_id_hr('%s','%s')"%(linea[13:21], linea[11:12]))
	 		            	cursor.execute(query_2)
	 		            	reg_1 = cursor.fetchall()
	 		                date = linea[2:6] + '/' + linea[6:8] + '/' + linea[8:10].strip()
	 		                period_id = account_period_obj.search(cr, uid, [('company_id', '=', COMPANY_ID_MOR), ("code",'=', period)])[0]
	 		                header = {
	 		                    'date':date,
	 		                    'journal_id':reg_1[0][0],
	 		                    'ref':linea[13:21],
	 		                    'company_id': COMPANY_ID_MOR,
	 		                    'period_id':period_id
	 		                }
	 		                obj_policy = account_move_obj.create(cr, uid, header, context = context)
	 		            elif 'M' in linea[0:1]:
	 		            	cuenta = linea[2:5] + '-' + linea[5:7] + '-' + linea[7:10] + '-' + linea[10:12].strip()
	 		            	if '6' in linea[2:3]:
	 		              		query_3 = ("select s.id_ou from sync_contpaq_openerp_rel s where s.c_contpaq = '%s'"% (cuenta))
	 		               	 	cursor.execute(query_3)
	 		               	 	reg_2 = cursor.fetchall()
	 		               	 	operating_unit = reg_2[0][0]
	 		               	query_4 = ("select s.c_contpaq,s.id_partner,s.id_ou,s.id_open,s.id_ananew from sync_contpaq_openerp_rel s where s.c_contpaq = '%s'"% (cuenta))
	 		               	cursor.execute(query_4)
	 		               	reg_3 = cursor.fetchall()
	 		               	if '1' in linea[34:35]:
	 		               	 	debit = float(linea[44:52])
	 		               	 	credit = 0
	 		               	 	#Si debito viene en negativo es un credito
	 		               	 	if debit < 0:
	 		               	 		credit = debit * -1
	 		               	 		debit = 0
	 		               	  	update_detalle={
	 		               	  		'name': linea[2:12]+'-'+linea[73:89].strip(),
	 		               	  		'partner_id':reg_3[0][1],
	 		               	  		'account_id':reg_3[0][3],
	 		               	  		'analytic_account_id': reg_3[0][4],
	 		               	  		'operating_unit_id':operating_unit,
	 		               	  		'debit':debit,
	 		               	  		'credit':credit,
	 		               	  		'move_id': obj_policy
	 		               	  		}
	 		               	  	obj_line = account_move_line_obj.create(cr, uid, update_detalle, context=context)
	 		               	elif '2' in linea[34:35]:
	 		               	  	credit = float(linea[44:52])
	 		               	  	debit = 0
	 		               	  	#Si credito viene en negativo es un debito
	 		               	  	if credit < 0:
	 		               	  		debit = credit * -1
	 		               	  		credit = 0
	 		               	  	update_detalle={
	 		               	  		'name': linea[2:11]+'-'+linea[73:89].strip(),
	 		               	  		'partner_id':reg_3[0][1],
	 		               	  		'account_id':reg_3[0][3],
	 		               	  		'analytic_account_id': reg_3[0][4],
	 		               	  		'operating_unit_id':operating_unit,
	 		               	  		'debit':debit,
	 		               	  		'credit':credit,
	 		               	  		'move_id': obj_policy
	 		               	  		}
	 		               		obj_line = account_move_line_obj.create(cr, uid, update_detalle, context=context)
	 	"""
	 	Proceso de borrado de los archivos que se guardaron en la ruta establecida de la variable @extracth_path
	 	para que no cause conflictos con los nuevos archivos que se generaran cada vez que se corra el proceso
	 	"""
		file_list = os.listdir(extract_path)
		for item in file_list:
			os.remove(os.path.join(extract_path, item))