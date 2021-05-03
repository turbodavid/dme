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
import psycopg2
import xmlrpclib
from openerp.tools.translate import _
import os
#log
import logging
_logger = logging.getLogger(__name__)

COMPANY_ID_MOR = 1
ENTERPRISE = {'GMM':'contpaq_openerp_morsa_gmm', 'MOR':'contpaq_openerp_morsa_mor', 'VOH':'contpaq_openerp_morsa_voh', 'desarrollo':'contpaq_morsa_desarrollo'}
import sync_conexion

class sync_morsa_policy(orm.Model):
	_name = "sync.morsa.policy"     
	#_inherit ='sync.morsa'
	_defaults = {
		'records'	: '0',
	}
	_columns = {
	'period': fields.char('Period', size=6, help='mmaaaa'),
	'enterprise':fields.char('Enterprise', help='Write the code for enterprise \nGMM: contpaq_openerp_morsa_gmm \nMOR: contpaq_openerp_morsa_mor \nVOH: contpaq_openerp_morsa_voh\n Example: GMM'),
	'records':fields.integer('#Registros', help='Número de registros a procesar. 0 para todos')
    }

	dbname = ''
	conexion = None
	period_id = 0
	cursorUpdate = None

	def action_sync_policy(self, cr, uid, ids, context=None):
		#Mbdname = ''
		#Mperiod = ''
		nrows = 0
		#get values
		for record in self.browse(cr,uid,ids,context=context):
			self.dbname = record.enterprise.upper()
			period = record.period
			period = period[:2] + "/" + period[2:]
			nrows = record.records


		_logger.debug("DB: %s" % self.dbname)
		if self.dbname not in ENTERPRISE:
		     raise osv.except_osv(_("Sym GMM"), _("write a enterprise correct."))
		#get db
		self.dbname = ENTERPRISE[self.dbname]
		#get conexion
		#conexion = self._get_conexion("conexion_openerp.csv", dbname)
		self.conexion = self.pool.get('sync.morsa.conexion')._get_conexion("conexion_openerp.csv", self.dbname)
		cursor = self.conexion.cursor()
		
		records_to_process = ''
		if nrows > 0:
			records_to_process = "LIMIT %s" %str(nrows)
			
		#Query datos Polizas
		query = ("Select P.folio, P.fecha, P.concepto, P.tipopol, P.cargos, P.abonos, P.Id, P.Guid, fn_get_journal_id(p.id) "
		         "From SyncPolizas P "
		         "Where (right(('00' || cast(periodo as varchar)),2) || '/' || ejercicio) = '%s' "
				 "  AND paso_erp = cast(0 as bit) "
				 "  AND EXISTS( SELECT idPoliza FROM syncmovimientospoliza WHERE idPoliza = p.id) " 
		         "order by P.Id %s;" % (str(period), records_to_process))
		nrows = cursor.execute(query)
		nrows = cursor.rowcount
		print "query qeudo: ", query
		print "Rows: ", nrows
		self.cursorUpdate = self.conexion.cursor()

		sync_morsa_log_obj = self.pool.get('sync.morsa.log')

		#Delete log for period and db
		sync_morsa_log_ids = sync_morsa_log_obj.search(cr, uid, [('period','=', period),('db','=',self.dbname)])
		sync_morsa_log_obj.unlink(cr, uid, sync_morsa_log_ids, context=None)

		account_period_obj = self.pool.get('account.period')
		self.period_id = account_period_obj.search(cr, uid, [('company_id', '=', COMPANY_ID_MOR), ("code", '=', period)])[0]

		ncount = 0
		#while ncount <= nrows:

		self.moves = cursor.fetchall()
		#if self.moves == None:
		#	break
		#ncount = ncount + 1
		#print "Trabajando en el bloque: ", ncount

		if nrows > 0:
			self.crea_polizas_open( cr, uid, ids, period, context)

		return

	def crea_polizas_open(self,cr, uid, ids, period, context=None):

		#objects
		account_move_obj = self.pool.get('account.move')
		account_move_line_obj = self.pool.get('account.move.line')
		account_journal_obj = self.pool.get('account.journal')
		account_account_obj = self.pool.get('account.account')
		sync_morsa_log_obj = self.pool.get('sync.morsa.log')
		account_analytic_line_obj = self.pool.get('account.analytic.line')
		account_analytic_account_obj = self.pool.get('account.analytic.account')
		res_partner_obj = self.pool.get('res.partner')
		ir_model_data_obj = self.pool.get('ir.model.data')
		account_move_uuid_obj = self.pool.get('account.move.uuid')

		# lines
		lines = []
		lines_fail = []
		dict_lines_cfdis = {}
		# lines_cfdis = []

		# for each polizas
		for move in self.moves:
			print "Folio: %s" % move[0]
			# _logger.debug("Folio: %s" % move[0])
			# 24-Mar-2017, el diario esta establecido en la funcion fn_get_journal_id()
			# [3] tipopol
			# filter_journal = []
			# if move[3] == 1: # 1 : Ingresos
			#	#codigo_dia = LEFT(folio,4) + 1 - >
			#	filter_journal = [('company_id', '=', COMPANY_ID_MOR), ('code','=','VEN')]
			# elif move[3] == 2: # 2 : Egresos
			#	#codigo_dia = left(folio,4) + tipo +
			#	filter_journal = [('company_id', '=', COMPANY_ID_MOR), ('code','=','COMPR')]
			# else: #
			#	filter_journal = [('company_id', '=', COMPANY_ID_MOR), ('code','=','Vario')]
			# get journal id
			# journal_id = account_journal_obj.search(cr, uid, filter_journal)#[0]
			# journal_id = account_journal_obj.browse(cr, uid, journal_id)
			# journal_id = journal_id[0]

			# create object Header
			header = {
				'journal_id': move[8],  # journal_id.id,
				'ref': move[0],  # [0]Folio
				'period_id': self.period_id,
				'date': move[1],  # [1]Fecha
				'company_id': COMPANY_ID_MOR,
				'narration': move[2],  # [2]Concepto
				'guid': move[7]  # 7 : Guid
			}

			# lines
			query = ("Select C.Codigo, C.codigo || '-' || C.Nombre, R.Id_Company, "
					 "       Coalesce(R.Id_Partner,0) as Id_Partner, "
					 "       M.Folio, M.fecha, "
					 "       case when (Cast(M.tipomovto as bit) = Cast(0 as bit)) Then "
					 "           case when M.importe < 0 Then 0 Else M.Importe End "
					 "       else "
					 "           case when M.importe < 0 Then Abs(M.Importe) Else 0 End "
					 "       End as cargo, "
					 "       case when (Cast(M.tipomovto as bit) = Cast(1 as bit)) Then "
					 "           case when M.importe < 0 Then 0 Else Abs(M.Importe) End "
					 "       Else "
					 "           case when M.importe < 0 Then Abs(M.Importe) Else 0 End "
					 "       End as abono, "
					 "   Coalesce(R.c_openerp, 'No Definido en Relación') as c_openerp, "
					 "   Coalesce(R.id_analytic, '') as id_analytic, "
					 "   case when M.importe < 0 Then 1 Else 0 End as negative, M.Importe, M.Id, M.Guid, "
					 "   CoalEsce(R.id_ou_new, 1 ) as id_ou_new, CoalEsce(R.id_ananew,0) AS id_ananew, R.id_open "
					 "From SyncMovimientosPoliza M "
					 "Inner Join SyncCuentas C on M.IdCuenta = C.Id "
					 "Left Join Sync_Contpaq_Openerp_Rel R on replace(c_contpaq,'-','') = C.Codigo "
					 "Where M.IdPoliza = %s and M.importe <> 0 order by M.nummovto;" % move[6]);
			cursor_lines = self.conexion.cursor()
			cursor_lines.execute(query)
			move_lines = cursor_lines.fetchall()
			insert_policy = True
			# Get UUID from Header
			query = ("Select uuid, guidref "
					 "From SyncAsocCFDIs "
					 "Where guidref = '%s';" % move[7]);  # 7 guid
			cursor_uuid_header = self.conexion.cursor()
			cursor_uuid_header.execute(query)
			uuid_header = cursor_uuid_header.fetchall()

			# clear lists
			# lines from policy
			lines[:] = []
			# cfdis lists
			# lines_cfdis[:] = []
			# dict_lines_cfdis.clear()
			# List for errors
			lines_fail[:] = []
			# for lines
			for move_line in move_lines:
				# Get UUID from LINES
				query = ("Select uuid, guidref "
						 "From SyncAsocCFDIs "
						 "Where guidref = '%s';" % move_line[13]);  # 13 : Guid
				cursor_uuid_lines = self.conexion.cursor()
				cursor_uuid_lines.execute(query)
				uuid_lines = cursor_uuid_lines.fetchall()
				# set initial values
				negative = move_line[10]  # 10:Negative
				analytic_account_id = move_line[9]  # Analytic Id
				partner_id = 0
				if move_line[13] > 0:
					partner_id = move_line[3]
				# search partner id
				#Mif partner_id > 0:  # partner_id
					# check partner in res_partner
					#Mpartner_id = res_partner_obj.search(cr, uid, [('id', '=', partner_id)])
					#Mif len(partner_id) == 0:
					#M	insert_policy = False
					#M	lines_fail.append(
					#M		{
					#M			'period': period,
					#M			'folio': move[0],  # folio header
					#M			'message': 'Partner Id:' + str(move_line[3]),  # partner_id
					#M			'account_contpaq': str(move_line[0]),  # account contpaq
					#M			'db': self.dbname,
					#M		}
					#M	)
					#Melse:
					# get partner id
					#M	partner_id = partner_id[0]
				#Melse:
				#M	partner_id = 0
				# search analityc account
				if analytic_account_id <> '':  # analytic_id
					analytic_account_id = move_line[15]
					# analytic_account_id = account_analytic_account_obj.search(cr, uid, [('id', '=', analytic_account_id)])
					#Mmodel_data_id = ir_model_data_obj.search(cr, uid, [('model', '=', 'account.analytic.account'), (
					#M'name', '=', 'account_analytic_account_' + str(analytic_account_id))])
					# if len(analytic_account_id) == 0:
					#Mif len(model_data_id) == 0:
					#M	insert_policy = False
					#M	lines_fail.append(
					#M		{
					#M			'period': period,
					#M			'folio': move[0],  # folio header
					#M			'message': 'Analytic Account Id:' + str(move_line[9]),  # Analytic Id
					#M			'account_contpaq': str(move_line[0]),  # account contpaq
					#M			'db': self.dbname,
					#M		}
					#M	)
					#Melse:
					#M	model_data_id = ir_model_data_obj.browse(cr, uid, model_data_id)
					#M	model_data_id = model_data_id[0]
					#M	analytic_account_id = model_data_id.res_id
				else:
					analytic_account_id = 0
				# if amount is negative, save a record in log but we can create the policy
				if negative == 1:
					lines_fail.append(
						{
							'period': period,
							'folio': move[0],  # folio header
							'message': 'Negative:' + str(move_line[11]),
							'account_contpaq': str(move_line[0]),  # account contpaq
							'db': self.dbname,
						}
					)
				# Get account [8] c_openerp
				#Maccount_id = account_account_obj.search(cr, uid, [('company_id', '=', COMPANY_ID_MOR),
				#M												  ("code", '=', move_line[8])])
				account_id = move_line[16]
				if account_id > 0:
					# Nif account_id > 0:
					#Maccount_id = account_id[0]
					# get analityc account
					# analytic_account_id = move_line[9]
					# clean ids
					if partner_id == 0:
						partner_id = None
					if analytic_account_id == 0:
						analytic_account_id = None
					# line of policy
					lines.append(
						{
							'name': move_line[1],  # [1] nombre
							'partner_id': partner_id,  # [3] partner_id
							'account_id': account_id,
							'date_maturity': move_line[5],  # [5] fecha
							'date': move_line[5],  # [5] fecha
							'debit': move_line[6],  # [6] cargo
							'credit': move_line[7],  # [7] abono
							'journal_id': move[8],  # journal_id.id,
							'period_id': self.period_id,
							'move_id': move_line[12],
						# temporal Sync_MovimientosPolizas id, later we will assign account_move_id
							'analytic_account_id': analytic_account_id,
							'guid': move_line[13],  # 13 : Guid,
							'operating_unit_id': move_line[14]
						}
					)
					lines_cfdis = []
					lines_cfdis[:] = []
					for uuid_l in uuid_lines:
						lines_cfdis.append(
							{
								'uuid': uuid_l[0],  # 0 : uuid
								'guidref': move_line[13]  # 1 : guidref
							}
						)
					dict_lines_cfdis[move_line[13]] = lines_cfdis
				else:
					insert_policy = False
					lines_fail.append(
						{
							'period': period,
							'folio': move[0],  # folio header
							'message': "Account OpenERP (code):" + move_line[8],  # account
							'account_contpaq': str(move_line[0]),  # account contpaq
							'db': self.dbname,
						}
					)
					# Create account that not exists in relation table.
					sync_morsa_account = {
						'folio': move[0],  # Folio header
						'account_contpaq': str(move_line[0]),  # cuenta contpaq
						'name': move_line[1],  # nombre cuenta contpaq
						'account_openerp_sync': move_line[8],  # account openerp
					}
					sync_morsa_account_id = self.pool.get('sync.morsa.account').create(cr, uid, sync_morsa_account, context=context)

			# without details
			if len(lines) == 0:
				insert_policy = False
				lines_fail.append(
					{
						'period': period,
						'folio': header['ref'],  # folio header
						'message': "Without details",
						'account_contpaq': '',  # without
						'db': self.dbname,
					}
				)
			else:  # checks account type view or consolidation
				for line in lines:
					account = self.pool.get('account.account').browse(cr, uid, [line["account_id"]], context)
					if account[0].type in ('view', 'consolidation'):
						insert_policy = False
						lines_fail.append(
							{
								'period': period,
								'folio': header['ref'],  # folio header
								'message': "account of type view or consolidation (id: %s , code: %s )" % (
								line["account_id"], account[0].code),
								'account_contpaq': '',
								'db': self.dbname,
							}
						)
			# *********************************************************************************************************************
			# S E C T I O N   F O R   S A V E   H E A D E R
			# *********************************************************************************************************************
			if insert_policy:
				try:
					# create HEADER
					account_move_id = account_move_obj.create(cr, uid, header, context=context)
					# create UUID
					for uuid in uuid_header:
						account_move_uuid_id = account_move_uuid_obj.create(cr, uid, {
							'uuid': uuid[0],  # UUID
							'guid_ref': uuid[1],  # GUID REF
							'account_move_id': account_move_id
						}, context=context)
					# mark policy from db origin
					queryUpdate = "Update SyncPolizas Set paso_erp = cast(1 as bit) Where Id = %s" % move[6]
					self.cursorUpdate.execute(queryUpdate)
					# Commit
					self.conexion.commit()
				# M_logger.debug('Encabezado guardado correctamente')
				except Exception, e:
					insert_policy = False
					lines_fail.append(
						{
							'period': period,
							'folio': header['ref'],  # folio header
							'message': "Error Update SyncPolizas Paso_ERP:" + str(e),
							'account_contpaq': '',
							'db': self.dbname,
						}
					)
				# *********************************************************************************************************************
				# S E C T I O N   F O R   S A V E   D E T A I L S
				# set id of header and create line if was created the header
				# *********************************************************************************************************************
				if insert_policy:
					for line in lines:
						# get id of sync_movimietos_polizas
						sync_move_id = line['move_id']
						# set id of account_move
						line['move_id'] = account_move_id
						try:
							# create LINE
							account_move_line_id = self.pool.get('account.move.line').create(cr, uid, line, context=context)
							# create UUID
							for dlc in dict_lines_cfdis[line['guid']]:
								account_move_uuid_id = account_move_uuid_obj.create(cr, uid, {
									'uuid': dlc["uuid"],  # UUID
									'guid_ref': dlc["guidref"],  # GUID REF
									'account_move_line_id': account_move_line_id
								}, context=context)
							# Create rel between syncpolizasmovimiento and account_move_line
							sync_policy_rel = {
								'account_move_id': account_move_id,
								'folio': header['ref'],
								'account_move_line_id': account_move_line_id,
								'sync_move_id': sync_move_id
							}
							sync_policy_rel_id = self.pool.get('sync.morsa.rel').create(cr, uid, sync_policy_rel, context=context)
						# M_logger.debug('Detalle guardado correctamente')
						except Exception, e:
							account = self.pool.get('account.account').browse(cr, uid, [line["account_id"]], context)
							lines_fail.append(
								{
									'period': period,
									'folio': header["ref"],  # folio header
									'message': "Error Sync Policy Rel (account_id: %s, folio: %s) - (%s)" % (
								  	 line["move_id"], account[0].code, repr(e)),
									'account_contpaq': '',
									'db': self.dbname,
								}
							)
				# save negative
				for line_fail in lines_fail:
					sync_morsa_log_id = sync_morsa_log_obj.create(cr, uid, line_fail, context=context)
			else:  # save log with fail
				# Create fails
				for line_fail in lines_fail:
					sync_morsa_log_id = sync_morsa_log_obj.create(cr, uid, line_fail, context=context)

		return
