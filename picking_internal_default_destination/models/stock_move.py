# -*- encoding: utf-8 -*-

from openerp import fields, models


class stock_move(models.Model):
    _inherit = 'stock.move'

    def _default_location(self, cr, uid, type, context=None):
        sql  = '''Select sm.location_id, sm.location_dest_id
                    From stock_picking sp
                    Inner Join stock_move sm on sp.id = sm.picking_id
                    Where type = 'internal' Order By sp.create_date DESC limit 1;''';
        cr.execute(sql)

        res = cr.fetchone()
        pos = 0
        if type == 'destination':
           pos = 1 
        return (res and res[pos]) or False

    def _default_location_destination(self, cr, uid, context=None):
        picking_type = context.get('picking_type')
        location_id = False
        if picking_type == 'internal':
            #get lines
            move_lines = context.get('move_lines')
            if move_lines:
                #print 'move_lines',move_lines
                for line in move_lines:
                    location_id_destination = line[2]['location_dest_id']
            else:
                location_id_destination = self._default_location(cr, uid, 'destination', context)
            if location_id_destination == 0:
                location_id_destination = False
            location_id = location_id_destination
        else:
            location_id = super(stock_move, self)._default_location_source(cr, uid, context=context)

        return location_id

    def _default_location_source(self, cr, uid, context=None):
        picking_type = context.get('picking_type')
        location_id = False        
        if picking_type == 'internal':
            #get lines
            move_lines = context.get('move_lines')
            if move_lines:
                for line in move_lines:
                    location_id_source = line[2]['location_id']
            else:
                location_id_source = self._default_location(cr, uid, 'source', context)
            if location_id_source == 0:
                location_id_source = False
            location_id = location_id_source
        else:
            location_id = super(stock_move, self)._default_location_source(cr, uid, context=context)

        return location_id

    _defaults = {
        'location_id': _default_location_source,
        'location_dest_id': _default_location_destination,
    }
