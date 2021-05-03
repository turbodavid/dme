# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
class clasificacion(osv.Model):
	_name ="clasificacion"
	_columns = {
	'name': fields.char(string="Name", size=50),
	'active': fields.boolean(string="Active"),
	}
	_defaults = {
	'active': True,
	}
