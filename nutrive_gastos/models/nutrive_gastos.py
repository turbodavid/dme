# -*- encoding: utf-8 -*-
# -*- coding: 850 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: Jesus Alfonso Moreno Valdez (alfonso.moreno@pcsystems.mx)
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
import base64
import csv
from openerp import fields, models
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import datetime, time
import openerp.addons.decimal_precision as dp 
from openerp import tools
import os
from lxml import etree
#account.group_account_manager
#account_voucher.view_voucher_form
class nutrive_gastos(orm.Model):
	_name = 'nutrive.gastos'
	_description = 'Nutrive Gastos'
	_defaults = {
		'date_ini'    : lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
		'date_fin'    : lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
	}
	
	def create(self, cr, uid, vals, context):
		print vals
		return super(nutrive_gastos, self).create(cr, uid, vals, context)
	_columns ={
			'company_id'  : fields.many2one('res.company', 'Company', required=True),
			'period_id'   : fields.many2one('account.period', 'Period', required=True),
			'journal_id'  : fields.many2many('account.journal', string= 'Diario'),
			'period_name'   : fields.char('Nombre Periodo'),
			'uni_prod'	    : fields.float('Unidades producidas'),
			'cto_adicional' : fields.float('Costo adicional'),
			'gasto_sin_imp' : fields.float('gasto'),
			'date_ini'   : fields.date('Fecha inicial', required = True),
			'date_fin'	 : fields.date('Fecha final', required = True),
		}
	def default_get(self, cr, uid, fields, context=None):
	 	res = super(nutrive_gastos, self).default_get(cr, uid, fields, context=context)
	 	res['company_id'] = 3
	 	res['period_id']  = 14
	 	return res

	def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
		if context is None:
			context = {}
		res = super(nutrive_gastos, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
		if view_type == 'form':
		    for field in res['fields']:
		        if field == 'journal_id':
		           	res['fields'][field]['domain'] = [('code', 'ilike', 'GTO')]
		doc = etree.XML(res['arch'])            
		res['arch'] = etree.tostring(doc)        
		return res

	def execute_query(self, cr, uid, ids, context=None):

		obj_expense = self.pool['nutrive.gastos'].browse(cr, uid, ids[0], context=context)

		company_id = obj_expense.company_id.id
		period_id  = obj_expense.period_id.id
		journal_id = obj_expense.journal_id

		fecha_fin =  obj_expense.period_id.date_stop
		fecha_ini =  obj_expense.period_id.date_start
		print "Las fechas son:", fecha_fin, fecha_ini
#		fecha_fin =  obj_expense.date_fin
#		fecha_ini =  obj_expense.date_ini

		journal_select = [0]
		for journal in journal_id:
			journal_select.append(journal.id)

		where = ""
		if len(journal_select) > 1:
			where = "AND aj.id IN " + str(tuple(journal_select))
		else:
		 	obj_ids_default = self.pool['account.journal'].search(cr, uid, [('code', 'ilike', 'GTO')])
		 	where = "AND aj.id IN " + str(tuple(obj_ids_default))
		 	
		strquery_1 = (""" SELECT *, (T.gasto_sin_impuesto/T.UniProd) ctoadicuni
							from
							(
								SELECT ap.id, ap.name periodo, sum(ai.amount_untaxed) gasto_sin_impuesto,
									(select sum(mrp.product_qty) suma_productos
									from mrp_production mrp 
									WHERE --mrp.date_start between ap.date_start and ap.date_stop
										--AND 
										mrp.date_finished between ap.date_start and ap.date_stop
										AND state = 'done'
									)uniprod
								FROM account_invoice ai
								INNER JOIN account_journal aj ON (ai.journal_id = aj.id)
								INNER JOIN account_period ap ON (ai.period_id = ap.id) 
								WHERE ai.period_id = '%s' AND aj.company_id = '%s' %s
								GROUP BY ap.id, ap.name, ap.date_start, ap.date_stop
							)as T """ %(period_id, company_id, where))

		strquery = ''
		strquery = strquery_1
		#columnas = 3
		#encabezado = "%s,%s,%s,%s,%s" % ( _('Diario'), _('Periodo'),_('GastoTotal'),_('Unidades producidas'), _('Costo adicional'))
		cr.execute(strquery)
		registros = cr.fetchall()
		print registros, '+++++++++++++++++'
		for move in registros:
			update ={
				'period_id'	   : move[0],
				'period_name'  : move[1],
				'gasto_sin_imp': move[2],
				'uni_prod'	   : move[3],
				'cto_adicional': move[4],
				'date_ini'	   : fecha_ini,
				'date_fin'	   : fecha_fin
				}
			obj_query = self.pool.get('nutrive.gastos').create(cr, uid, update, context = context)
		#obj_gastos = self.pool['nutrive.gastos'].browse(cr, uid, ids[0], context = context)
		#obj_product = self.pool['production.product'].browse(cr, uid, ids[0], context = context)
		product_obj = self.pool['production.product']
		query_product = ("""
							SELECT mp.product_id,  mp.product_qty, pt.name
							FROM mrp_production mp
							INNER JOIN product_product pp ON (mp.product_id = pp.id)
							INNER JOIN product_template pt ON (pp.product_tmpl_id = pt.id)
							WHERE mp.date_finished BETWEEN '%s' AND '%s'
							AND mp.state = 'done' """ %(fecha_ini, fecha_fin))
		strquery_3 = ""
		strquery_3 = query_product
		cr.execute(strquery_3)
		reg_prod = cr.fetchall()
		for move in reg_prod:
		 	update = {
		 			'product_id' : move[0],
		 			'product_qty': move[1],
		 			'product_name': move[2],
		 			'id_gasto': obj_query
		 	}
		 	obj_prod = self.pool.get('production.product').create(cr, uid, update, context = context)

		query_journal = ("""
							SELECT aj.name, ap.id id_periodo, ap.name nombre_periodo, sum(ai.amount_untaxed) gasto_detallado
							FROM account_invoice ai
							INNER JOIN account_period ap ON (ai.period_id = ap.id)
							INNER JOIN account_journal aj ON (ai.journal_id = aj.id)
							WHERE  ai.company_id = 3 %s
							AND ai.state IN ('paid', 'open') AND ai.period_id = '%s'
							group by aj.name, ap.id, ap.name """%(where, period_id))
		strquery_journal = ""
		strquery_journal = query_journal
		cr.execute(strquery_journal)
		reg_journal = cr.fetchall()
		for move in reg_journal:
			update_journal = {
							'journal_name' : move[0],
							'id_periodo'    : move[1],
							'period_name'  : move[2],
							'gasto_detallado' : move[3],
							'id_gasto'     : obj_query

						}
			obj_journal_details = self.pool.get('journal.details').create(cr, uid, update_journal, context = context)
		#print"WWWWWWWWWWWW",reg_prod
		#print"UPDATEEEEE", update

		# # Tabla grande
		# nutrive_gastos_obj = self.pool.get('nutrive.gastos')
		# nutrive_gastos = nutrive_gastos_obj.search(cr,uid, [])
		# #nutrive_gastos_obj_v2 = nutrive_gastos_obj.browse(cr, uid, nutrive_gastos)
		# #print"WWWWWWWWWWWWW",nutrive_gastos_obj_v2.ids
		# #ids_nutrive_gastos = 0
		# #print"TTTTTTTTTTTTTTTT", ids_nutrive_gastos
		# obj_product_search = product_obj.search(cr, uid, [])
		# # diccionarto = {}
		# for obj_product_cto in product_obj.browse(cr, uid, obj_product_search):
		#  	#cto_adi = 0
		# 	print"PRODUCT_ID", obj_product_cto.id
		#  	for nutrive_gasto in nutrive_gastos_obj.browse(cr, uid, nutrive_gastos):
		# # 		#cto_adi += obj_product_cto.product_qty * nutrive_gasto.cto_adicional
		#  		ids_nut_gastos = nutrive_gasto.id
		# # 		#print"GGGGGGGGGGGGGGG", ids_nut_gastos
		#  		product_obj.write(cr, uid, obj_product_cto.id, {'gasto_id': ids_nut_gastos}) #'cto_adi_producto': cto_adi,







nutrive_gastos()
