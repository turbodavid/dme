# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#
#   Coded By:
#       Cindy Yukie Ley Garcia cindy.ley@dmesoluciones.com
#       Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com
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
class sale_order(osv.Model):
    _inherit = 'sale.order'

    def onchange_client_ref(self, cr, uid, ids, client_ref, context=None):
        values = {}
        if client_ref:
            client_ref = self.pool.get('res.partner').browse(cr, uid, client_ref, context=context)
            values['value'] = {'client_order_ref':client_ref.name or False, 'phone_logistic' : client_ref.phone, 'contact_logistic':client_ref.name}
        else:
            values['value'] = {'phone_logistic' : '', 'contact_logistic':''}
        return values

    def onchange_collection_address_id(self, cr, uid, ids, collection_address_id, context=None):
        result = {}
        if (collection_address_id):
            obj_collection_address = self.pool.get('collection.address').browse(cr, uid, collection_address_id, context=context)
            result['value'] = {'phone_collection': obj_collection_address.phone_site or False, 'contact_site': obj_collection_address.contact_site or False}
        return result

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        if not partner_id:
            return {}
        #invocamos la método base
        values = super(sale_order,self).onchange_partner_id(cr, uid,ids, partner_id,context=context)
        #buscamos el parter
        partner_id = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        childs = []
        #recorremos los hijos y los metemos a una lista
        for child in partner_id.child_ids:
            childs.append(child.id)
        #Asignamos el dominio para limitar en forma dinámica dependiendo del partner

        #Con el dominio funciona pero se queda colgado
        #values['domain'] = {'client_ref': [('parent_id', 'in', [partner_id])],}
        #Actualizamos cambos al realizar on change
        # Se toma el primer contacto
        child_default = False
        if (len(childs)>0):
            child_default = childs[0]

        values['value'].update({'childs_list': childs})
        values['value'].update({'client_order_ref': ''})
        values['value'].update({'client_ref': [child_default]})
        return values

    def _default_client_ref(self, cr, uid, context=None):
        res = self.pool.get('res.partner').search(cr, uid, [('parent_id','=','partner_id')], context=context)
        #return res and res[0] or False
        values = {}		
        values['domain'] = {'client_ref': [],}
        return []#values

    def _get_child_partner(self, cr, uid, ids, field_name, arg, context):
        res = {}
        if ids != False:
            proy_ids = self.read(cr, uid, ids, ['partner_id'], context)
            for proy_id in proy_ids:
                proy = proy_id['partner_id'][0]
                cr.execute("SELECT id FROM res_partner "\
                "WHERE parent_id =  " + str(proy) + " order by id ")
                res[ids[0]] = [id[0] for id in cr.fetchall() ]
        return res

    def _default_collection_address(self, cr, uid, context):
        return 4 # La idea es considerar un default se podria poner una marca en el collection address
    
    _columns = {
        'merchandise_insurance' : fields.boolean("Merchandise insurance request by the client "),
        'scaffold': fields.boolean("scaffold"),
        'unloading_maneuvers':fields.boolean("unloading maneuvers"),
        'type_service': fields.selection([('1','Flete Local'),('2','Flete Nacional'),('3','Recolección')],"Type Of Service",select=True),
        'reference': fields.text(string="Reference"),
        'contact_logistic':  fields.char('Contact', size=128),
        'contact_site':  fields.char('Contact', size=128),
        'budget_valid':fields.char('Budget valid for ',size=128),
        'freight_destination_v': fields.selection([('1','SI'),('0','NO')],"Freight Destination",select=True),
        'delivery_time':fields.char('Delivery time', size=128),
        'client_ref': fields.many2one('res.partner','Client Reference'),#, domain=[('parent_id','=', )]),
        'childs_list': fields.function(_get_child_partner, method=True, type='char', string='Contacts', store=False),
        'collection_address_id': fields.many2one('collection.address','Collection Address'),
        'phone_logistic': fields.char('Phone', size= 64),
        'phone_collection': fields.char('Phone', size= 64),
    }

    _defaults = {
        'budget_valid': _("7 dias hábiles"),
        'collection_address_id': _default_collection_address
    }
