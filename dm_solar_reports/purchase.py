# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#
#	 Coded By:
#	 	Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com
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
from openerp.osv import osv, fields
from openerp.tools.translate import _
class purchase_order(osv.Model):
    _inherit = 'purchase.order'
    
    def on_change_city(self, cr, uid, ids, city_id, context=None):
        result = {}
        if context is None:        
            context = {}
        if city_id:
            obj_city = self.pool['res.country.state.city'].browse(cr, uid, city_id, context=context)
            result = {'value': {'state_id_site': obj_city.state_id.id if obj_city.state_id else False}}
        return result

    def _lang_get(self, cr, uid, context=None):
        lang_pool = self.pool.get('res.lang')
        ids = lang_pool.search(cr, uid, [], context=context)
        res = lang_pool.read(cr, uid, ids, ['code', 'name'], context)
        return [(r['code'], r['name']) for r in res]

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        values = super(purchase_order, self).onchange_partner_id(cr, uid, ids, partner_id)
        context = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            values['value'].update({'lang':partner.lang or None, 'type_picking': None})
        return values

    def onchange_warehouse_id(self, cr, uid, ids, warehouse_id):
        values = super(purchase_order, self).onchange_warehouse_id(cr, uid, ids, warehouse_id)
        if warehouse_id:
            values['value'].update({'type_picking': None})
        return values

    def onchange_type_picking(self, cr, uid, ids, collection_type_id, partner_id, warehouse_id, context=None):
        result = {}
        if context is None:        
            context = {}
        colony_site = ''
        number_site = ''
        state_id_site = False
        street_site = ''
        city_id_site = False
        zip_site = ''
        phone_site = ''

        if collection_type_id:
            obj_collection_type = self.pool['collection.type'].browse(cr, uid, collection_type_id, context=context)            
            if (obj_collection_type.supplier_data==True):
                #Object Partner
                obj_partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
                #Assign datas
                colony_site = obj_partner.street2
                number_site = (obj_partner.l10n_mx_street3 + " " if obj_partner.l10n_mx_street3 else "") + (obj_partner.l10n_mx_street4 or "")
                state_id_site = obj_partner.state_id.id if obj_partner.state_id else False
                street_site = obj_partner.street
                city_id_site = obj_partner.city_id.id if obj_partner.city_id else False
                zip_site = obj_partner.zip
                phone_site = obj_partner.phone                            
            elif obj_collection_type.pack_data == False and obj_collection_type.supplier_data == False:
                #Object Warehouse
                obj_warehouse = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id, context=context)
                #Assign datas
                colony_site = obj_warehouse.partner_id.street2
                number_site = (obj_warehouse.partner_id.l10n_mx_street3 + " " if obj_warehouse.partner_id.l10n_mx_street3 else "") + (obj_warehouse.partner_id.l10n_mx_street4 or "")
                state_id_site = obj_warehouse.partner_id.state_id.id if obj_warehouse.partner_id.state_id else False
                street_site = obj_warehouse.partner_id.street
                city_id_site = obj_warehouse.partner_id.city_id.id if obj_warehouse.partner_id.city_id else False
                zip_site = obj_warehouse.partner_id.zip
                phone_site = obj_warehouse.partner_id.phone

        #result
        result = {'value': {'place_site': '',
                                'colony_site': colony_site,
                                'number_site': number_site,
                                'state_id_site': state_id_site,
                                'street_site': street_site,
                                'city_id_site': city_id_site,
                                'zip_site': zip_site,
                                'phone_site': phone_site
                                }
                     }

        return result
    
    _columns = {
        'type_picking': fields.many2one('collection.type', 'Type of Picking'),
        'place_site': fields.char('Place', size=255),
        'street_site': fields.char('Street', size=128),
        'colony_site': fields.char('Colony', size=128),
        'city_id_site': fields.many2one('res.country.state.city', 'City'),
        'number_site': fields.char('Number', size=128),
        'zip_site': fields.char('Zip', size=24),
        'state_id_site': fields.many2one('res.country.state', 'State'),
        'phone_site': fields.char('Phone', size=64),
        'lang': fields.selection(_lang_get, 'Language',help="Language for document that will be printed, If not, it will be English."),
    }
