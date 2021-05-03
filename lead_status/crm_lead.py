# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#
#	 Coded By:
#	 	Cindy Yukie Ley Garcia yukieley6@gmail.com
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
import openerp.netsvc
import time
from openerp.tools.translate import _

class crm_lead(orm.Model):
	_inherit = 'crm.lead'

	_columns = {
		'contract_type': fields.selection([('1', 'FMV Full Pay Out'),('2', 'Préstamo'),('3', 'Arrendamiento de Valor de Mercado'),('4', 'Sucripción')],'Contract Type',select=True),
		'status_sales': fields.selection([('1', 'Oportunidad Standard'),('2', 'Oportunidad No Standard'),('3', 'Cotización Enviada'),('4', 'Cotización Especial'),('5', 'Revision de Cotización'),('6','Cotización Aceptada')],'Status Sales',select=True),
		'status_credit': fields.selection([('1', 'Solicitud de Expediente'),('2', 'Expediente Incompleto'),('3', 'Expediente Completo'),('4', 'Expediente en Crédito'),('5', 'Línea Rechazada'),('6','Requiere Aval'),('7',' Línea Autorizada')],'Status Credit',select=True),
		'status_operation': fields.selection([('1', 'Propuesta Standard Cargada'),('2', 'Propuesta No Standard Cargada'),('3', 'Propuesta Aprobada por Crédito'),('4', 'Propuesta Aprobada por Ventas'),('5', 'Contrato Generado'),('6','Contrato en Firma'),('7','Contrato en Tránsito'),('8','Contrato Recibido Incorrecto'),('9',' Contrato Recibido Correcto'),('10','VAL Liberado'),('11','Contrato Facturado'),('12','Contrato Fondeado'),('13','Contrato Pagado')],'Status Operation',select=True),
		'currency_lead': fields.many2one('res.currency','Currency'),
	}
