# -*- encoding: utf-8 -*-
# -*- coding: 850 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: César Alfredo Sánchez Beltrán (cesar_sb@hotmail.com)
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
from openerp import api, fields, models
import base64
import csv
from openerp.tools.translate import _
from openerp import tools
from openerp.exceptions import Warning as UserError
from openerp.addons import decimal_precision as dp
from datetime import datetime, timedelta
import os

class ValidationBitam(models.TransientModel):
	_name = 'validation.bitam'

	report_type = fields.Selection(
							[('detail', 'Detallado por Cuenta Contable'),
							('accumulated', 'Acumulado por Informe Financiero')],
							default = 'detail',
							string = 'Tipo de Reporte',
							required = True
							#help='',
						)

	fiscal_year = fields.Many2one('account.fiscalyear','Ejercicio Fiscal', required = True)

	financial_report = fields.Many2one(
						'account.financial.report',
						'Reporte Financiero',
						domain = "[('name', 'ilike', 'IF')]"
						)
	period_id = fields.Many2one('account.period',
								'Periodo',
								domain = "[('fiscalyear_id','=', fiscal_year)]"
								)

	filename = fields.Char('File name', size=255, readonly=True)

	data = fields.Binary('File', readonly=True)

	def _eSg(self, cadena=None):
		nueva_cadena = ''
		if cadena > '':
			for l in cadena:
				x = l
				if x == u'\xd1':
					x = ''
				elif x == u'\xd3':
					x = ''
				elif x == u'\xed':
					x = ''
				elif x == u'\xf3':
					x = ''
				elif x == u'\xc1':
					x = ''
				elif x == u'\xfa':
					x = ''
				elif x == u'\xe9':
					x = ''
				elif x == u'\xe1':
					x = ''
				elif x == u'\xf1':
					x = ''
				elif x == u'\xfc':
					x = ''
				elif x == u'\xa6':
					x = ''
				elif x == u'\xcd':
					x = ''
				nueva_cadena = nueva_cadena + x
		if nueva_cadena == '':
			nueva_cadena = str(cadena)
		return nueva_cadena
	@api.multi
	def execute_query(self):

		fiscal_year = self.fiscal_year
		financial_report = self.financial_report
		period = self.period_id

		where = ""
		reporte_id = ""
		report_financial =""
		report_if = ""
		if period:
			where = "and repper.periodo = '%s' "%(period.code)
		if financial_report:
			report_financial = "where afr.id = '%s'"%financial_report.id
			reporte_id = "and afr.id = '%s'"%financial_report.id
		else:
			report_if = "where left(afr.name,2) = 'IF'"
		""""un solo reporte, detallado por cuenta(s)  y todos los periodos del ejercicio"""
		reporte_detallado = ("""select afr."name", repper.* from  account_financial_report afr
								inner join  getfinancialreport_per(afr.id,'%s') repper on (repper.freport_id = afr.id)
								where left(afr.name,2) = 'IF' %s %s """%(self.fiscal_year.code,reporte_id,where))
		"""Reporte Validacion Bitam acumulado por Año Fiscal o Periodo"""
		reporte_acumulado = ("""select afr.name, repper.periodo, sum(inicial) inicial, sum(cargos) cargos, sum(abonos) abonos, sum(final) final
						from account_financial_report afr inner join getfinancialreport_per(afr.id,'%s') repper on (repper.freport_id = afr.id)
						%s %s %s
						group by afr.name, repper.periodo
						order by afr.name, repper.periodo;""" %(self.fiscal_year.code,report_financial,report_if,where))

		#"""Reporte Validacion Bitam Acumulado por periodo y todos los reportes"""
		#reporte_acumulado_periodo_todos_reportes = ("""select afr.name, repper.periodo, sum(inicial) inicial, sum(cargos) cargos, sum(abonos) abonos, sum(final) final
		#				from account_financial_report afr inner join getfinancialreport_per(afr.id,'%s') repper on (repper.freport_id = afr.id)
		#				where left(afr.name,2) = 'IF' and repper.periodo = '%s'
		#				group by afr.name, repper.periodo
		#				order by afr.name, repper.periodo;""" %(fiscal_year.code,period.code))

		output = ''
		result = {}
		encabezado = ''
		columnas = 0
		if self.report_type == 'detail':
			columnas = 9
			strquery = reporte_detallado
			encabezado = "%s,%s,%s,%s,%s,%s,%s,%s,%s" % ( _('Nombre Cuenta'), _('ID del reporte'),_('Cuenta'),_('Nombre'),_('Periodo'),_('Inicial'),_('Cargos'),_('Abonos'),_('Final'))
		elif self.report_type == 'accumulated':
			columnas = 6
			strquery = reporte_acumulado
			encabezado = "%s,%s,%s,%s,%s,%s" % ( _('Nombre Cuenta'), _('Periodo'),_('Inicial'),_('Cargos'),_('Abonos'),_('Final'))
		self.env.cr.execute(strquery)
		registros = self.env.cr.fetchall()
		filename = ''
		if registros:
			#asign name of file
			#filepath = "%s" % ('/home/jorge-medina/pyerp7/parts/extras/dme/complete_sales/data/')
			filepath = '%s/%s/' % (os.path.dirname(os.path.abspath('')),'local_modules/validacion_bitam/data')
			filename = "%s.%s" % ('reporte_' + self.report_type,'csv')
			filefull = "%s" % (filepath + filename)
			#Header
			output = encabezado
			output += "\n"
			#Abre archivo de salida CSV
 			csvsalida = open(filefull, 'w')
			#iterate move lines
			for move in registros:
				# Genera la linea de salida
				#line = "%s, %s, ..." % (move[0].decode('UTF-8'), move[1].decode('UTF-8'), ...)
				line = ''
				x=0
				while x<columnas:
					dato = self._eSg(move[x])
					print"DATO", dato
					if move[x] != '':
						dato = '"' + dato + '"'
						line += dato
					else:
						line += ','
					if x<=18:
						line += ','
					x = x + 1
				#line = self._eSg(line)
				csvsalida.write(line + '\n')
				output += line + '\n'
			csvsalida.close()
			#encode base64
			out = base64.encodestring(output)
			#save in data base
			self.write({'data':out, 'filename':filename})
			dummy, view_id = self.env['ir.model.data'].get_object_reference('validacion_bitam', 'validacion_bitam_view_data')
			return {'name': _("Reporte Validacion Bitam"),
                'res_model':"validation.bitam",
                'src_model':"validation.bitam",
                'view_mode':"form",
                'target':"new",
                'key2':"client_action_multi",
                'multi':"True",
                'res_id':self.id,
                'view_id':view_id,
                'type': 'ir.actions.act_window',
			}
		else:
			raise UserError(
					_("No se encontro informacion en los parametros seleccionados"))