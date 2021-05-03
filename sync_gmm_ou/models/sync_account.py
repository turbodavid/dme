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

import time

from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp
import psycopg2

ENTERPRISE = {'GMM':'contpaq_openerp_morsa_gmm', 'MOR':'contpaq_openerp_morsa_mor', 'VOH':'contpaq_openerp_morsa_voh'}

class account_analityc_account(osv.Model):
	_inherit = 'account.analytic.account'
	_columns={
		'sync_morsa_account_id': fields.related('account_analytic_id', 'sync_morsa_account_id', relation="sync.morsa.account", type='many2one', string="Sync Morsa Account Id")
	}

class sync_morsa_account(osv.Model):        
	_name = 'sync.morsa.account'
	
	def action_confirm(self, cr, uid, ids, context=None):
		res = {}
		for morsa_account in self.browse(cr, uid, ids, context=context):
			a_o = morsa_account.account_openerp.code
			if a_o:
				if (a_o.startswith('112-01') or a_o.startswith('112-04') or a_o.startswith('211-03-1') or a_o.startswith('211-03-2')) and not morsa_account.partner_id:
					raise osv.except_osv(
						_('Warning'),
						_('You need to select a partner when account openerp start with [112-01], [112-04], [211-03-1], [211-03-2]')
					)
				if a_o.startswith('6') and not morsa_account.account_analytic_id:
					raise osv.except_osv(
						_('Warning'),
						_('You need to select a account analytic when account openerp start with [6]')
					)
			res = self.write(cr, uid, ids, {'state':'done'}, context=context)
		return res

	def action_undo(self, cr, uid, ids, context=None):
		res = {}
		for morsa_account in self.browse(cr, uid, ids, context=context):
			a_o = morsa_account.account_openerp.code
			if a_o:
				res = self.write(cr, uid, ids, {'state':'draft'}, context=context)
		return res


	def action_save(self, cr, uid, ids, context=None):
		res = {}
		# Crea objeto Sync Morsa Account
		obj_sync = self.pool['sync.morsa.account'].browse(cr, uid, ids[0], context=context)
		# Datos a Grabar
		acc_contpaq = obj_sync.account_contpaq
		acc_contpaq_r = acc_contpaq.replace("-","")
		acc_openerp = obj_sync.account_openerp.code
		acc_nameerp = obj_sync.account_openerp.name
		acc_iderp = obj_sync.account_openerp.id
		id_ou = obj_sync.operating_unit_id.id
		id_company  = 0
		id_partner  = obj_sync.partner_id.id
		if not id_partner:
			id_partner = 0
		id_analytic = obj_sync.account_analytic_id.id
		account_analytic =  ''
		if id_analytic:
			ir_model_data_obj = self.pool.get('ir.model.data')
			ir_model_data_id = ir_model_data_obj.search(cr, uid, [('model', '=', 'account.analytic.account'), ('res_id', '=', id_analytic )])
			ir_model_data_id = ir_model_data_obj.browse(cr, uid, ir_model_data_id, context=context)
			account_analytic = ir_model_data_id.name
			account_analytic = account_analytic.replace("account_analytic_account_", "")
			#str.replace( ir_model_data_id.name, "account_analytic_account_", "" )

		id_partnerc = 0
		database = ENTERPRISE[obj_sync.enterprise]
		if acc_openerp:
			# Abre la Base de Datos
			conexion = self.pool.get('sync.morsa.conexion')._get_conexion("conexion_openerp.csv", database)
			cursor = conexion.cursor()
			statement = "SELECT nombre FROM sync_contpaq_openerp_rel WHERE replace(c_contpaq,'-','') = '" + acc_contpaq_r + "'"
			cursor.execute (statement)
			existe = cursor.fetchone()
			if existe:
				csql = "UPDATE sync_contpaq_openerp_rel SET c_openerp = '" + acc_openerp + "', " + \
						"nombre       = '" + acc_nameerp      + "', " + \
						"id_company   = "  + str(id_company)  + ", "  + \
						"id_partner   = "  + str(id_partner)  + ", " + \
						"id_ou 		  = "  + str(id_ou) + ", " + \
						"id_ou_new 	  = "  + str(id_ou) + ", " + \
						"id_open 	  = "  + str(acc_iderp) + ", "
				if id_analytic:
					csql = csql + "id_analytic  = '"  + account_analytic + "', id_anaold = " + str(id_analytic) + ", id_ananew = " + str(id_analytic) + ", "

				csql = csql + "id_partner_c = "  + str(id_partnerc) + " WHERE replace(c_contpaq,'-','') = '" + acc_contpaq_r + "'"

				#cursor.execute("UPDATE sync_contpaq_openerp_rel SET c_openerp = '" + acc_openerp + "', " + \
				#		"nombre       = '" + acc_nameerp      + "', " + \
				#		"id_company   = "  + str(id_company)  + ", "  + \
				#		"id_partner   = "  + str(id_partner)  + ", "  + \
				#		"id_analytic  = "  + str(id_analytic) + ", "  + \
				#		"id_partner_c = "  + str(id_partnerc) + "WHERE replace(c_contpaq,'-','') = '" + acc_contpaq_r + "'")
		                #raise osv.except_osv(_("Sync GMM"), _("Record updated... \n"))				
			else:
				csql = "INSERT INTO sync_contpaq_openerp_rel (c_contpaq, c_openerp, nombre, id_company, id_partner, id_ou, id_ou_new, id_open, "

				if id_analytic:
					csql = csql + "id_analytic, id_anaold, id_ananew, "

				csql = csql + "id_partner_c) "

				csql = csql +  "VALUES ('"  + acc_contpaq + "', '" + acc_openerp + "', '" + acc_nameerp + "', " + str(id_company) + ", " + \
					   str(id_partner) + ", " + str(id_ou) + ", " + str(id_ou) + ", " + str(acc_iderp) + ", "

				if id_analytic:
					csql = csql + "'" + account_analytic + "', " + str(id_analytic) + ", " + str(id_analytic) + ", "

				csql = csql +  str(id_partnerc) + ") RETURNING c_contpaq; "

				#cursor.execute("INSERT INTO sync_contpaq_openerp_rel (c_contpaq, c_openerp, nombre, id_company, " + \
				#		"id_partner, id_analytic, id_partner_c) " + \
				#		"VALUES ('" + acc_contpaq + "', '" + acc_openerp + "', '" + acc_nameerp + "', " + \
				#		str(id_company) + ", " + str(id_partner) + ", " + str(id_analytic) + ", " + \
				#		str(id_partnerc) + ") RETURNING c_contpaq; ")
		                #raise osv.except_osv(_("Sync GMM"), _("Record Saved... \n"))
			cursor.execute(csql)
			conexion.commit()
			conexion.close()

			#raise osv.except_osv(_("Sync GMM"), _("Record Saved... \n"))
		else:
			raise osv.except_osv(_("Sync GMM"), _("Data Incomplete! Can't save \n"))				

		return res

	_columns = {
		'account_contpaq'     : fields.char('Account Contpaq'),
		'account_openerp'     : fields.many2one('account.account', 'Account OpenERP Rel', ondelete='cascade', help='Example: XXX-XX-X-XX'),
		'name'                : fields.char('Name'),
		'partner_id'          : fields.many2one('res.partner', 'Partner'),
		'account_analytic_id' : fields.many2one('account.analytic.account', 'Account Analytic', ondelete='cascade'),
		'state'               : fields.selection([ ('draft', 'Draft'), ('done', 'Done')], 'Status'),
		'enterprise'          : fields.selection([('GMM', 'GMM'), ('MOR', 'MOR'), ('VOH', 'VOH')],'Enterprise', help='GMM: contpaq_openerp_morsa_gmm \nMOR: contpaq_openerp_morsa_mor \nVOH: contpaq_openerp_morsa_voh\n Example: GMM', required=True),
		'folio'               : fields.char('Folio'),
		'account_openerp_sync': fields.char('Account OpenERP'),
		'operating_unit_id'	  : fields.many2one('operating.unit', 'Operating Unit', ondelete='cascade', help='Example: 01, 01-610'),
	}
	
	_defaults = {
		'state': 'draft'
    }
