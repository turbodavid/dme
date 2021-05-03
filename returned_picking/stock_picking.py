# -*- encoding: utf-8 -*-
############################################################################
#
#    Coded by: Cindy Yukie Ley cindy.ley@dmesoluciones.com
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

from openerp.osv import fields, osv
class stock_picking_out(osv.Model):
	_inherit = 'stock.picking.out'

	def on_changed_location(self,cr, uid, ids, id_location, context=None):
		result = {}
		resultids = []		
		if context is None:
			context = {}
		obj_move = self.pool['stock.move']
		obj_stock = self.pool['stock.picking'].browse(cr, uid, ids[0], context=context)
		for line in obj_stock.move_lines:
			#line.location_dest_id = id_location
			resultids.append(line.id)
			obj_move.write(cr, uid, line.id,{'location_dest_id':id_location}, context=context)

		result = {'value': {'move_lines': resultids}}
		return result

	_columns = {
		'location_dest_id_change':  fields.many2one('stock.location', 'Destination Location',  select=True, help="Location where the system will stock the finished products."),
	}

#states={'done': [('readonly', True)]}
