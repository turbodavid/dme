# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 Camptocamp (<http://www.camptocamp.com>)
#    Authors: Ferdinand Gasauer, Joel Grand-Guillaume
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
import logging
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class stock_move(orm.Model):
    _inherit = "stock.move"

    _columns = {
        'price_unit_net': fields.float(
            'Purchase Price',
            digits_compute=dp.get_precision('Product Price'),
            help="This is the net purchase price, without landed cost "
            "as the price include landed price has been stored in "
            "price_unit field"),
    }

    def _get_reference_accounting_values_for_valuation(self, cr, uid, move, context=None):
        """
        Return the reference amount and reference currency representing the inventory valuation for this move.
        These reference values should possibly be converted before being posted in Journals to adapt to the primary
        and secondary currencies of the relevant accounts.
        """
        product_uom_obj = self.pool.get('product.uom')

        # by default the reference currency is that of the move's company
        reference_currency_id = move.company_id.currency_id.id

        default_uom = move.product_id.uom_id.id
        qty = product_uom_obj._compute_qty(cr, uid, move.product_uom.id, move.product_qty, default_uom)

        # if product is set to average price and a specific value was entered in the picking wizard,
        # we use it
        #price_to_use was added because journal entries must take this value to affect inventory accounts correctly
        #landed cost must affect also inventory accounts
        price_to_use = 0.00
        if move.location_dest_id.usage != 'internal' and move.product_id.cost_method == 'average':
            reference_amount = qty * move.product_id.standard_price
        elif move.product_id.cost_method == 'average' and move.price_unit:
            price_to_use = move.price_unit
            if move.price_unit_net:
                price_to_use = move.price_unit_net
            reference_amount = move.product_qty * price_to_use
            #reference_currency_id = move.price_currency_id.id or reference_currency_id

        #if move.location_dest_id.usage != 'internal' and move.product_id.cost_method == 'average':
            #reference_amount = qty * move.product_id.standard_price
        #elif move.product_id.cost_method == 'average' and move.price_unit:
            #reference_amount = move.product_qty * price_unit
            #reference_currency_id = move.price_currency_id.id or reference_currency_id

        # Otherwise we default to the company's valuation price type, considering that the values of the
        # valuation field are expressed in the default currency of the move's company.
        else:
            if context is None:
                context = {}
            currency_ctx = dict(context, currency_id=move.company_id.currency_id.id)
            amount_unit = move.product_id.price_get('standard_price', context=currency_ctx)[move.product_id.id]
            reference_amount = amount_unit * qty

        return reference_amount, reference_currency_id


#
# Inherit of picking to add the link to the PO
#
class stock_picking(orm.Model):
    _inherit = 'stock.picking'


    def _get_price_unit_invoice(self, cursor, user, move_line, type):

        if type == 'in_invoice':
            if move_line.purchase_line_id:
                if move_line.purchase_line_id.order_id.invoice_method == 'picking':
                # forzó a que sea el precio de la orden de compra con landed costs
                # cambie este linea price_unit = move_line.price_unit por
                    price_unit = move_line.purchase_line_id.price_unit
                    order = move_line.purchase_line_id.order_id
                # QUITE ESTE CODIGO if order.currency_id.id != order.company_id.currency_id.id:
                # price_unit =  self.pool.get('res.currency').compute(cursor, user,
                # order.company_id.currency_id.id, order.currency_id.id, move_line.price_unit, round=False, context=dict({}, date=order.date_order))
                    return price_unit
            else:
                return move_line.purchase_line_id.price_unit
        return super(stock_picking, self)._get_price_unit_invoice(cursor, user, move_line, type)


class stock_partial_picking(orm.TransientModel):
    _inherit = "stock.partial.picking"

    def _partial_move_for(self, cr, uid, move, context=None):
        partial_move = {
            'product_id': move.product_id.id,
            'quantity': move.product_qty if move.state == 'assigned' or move.picking_id.type == 'in' else 0,
            'product_uom': move.product_uom.id,
            'prodlot_id': move.prodlot_id.id,
            'move_id': move.id,
            'location_id': move.location_id.id,
            'location_dest_id': move.location_dest_id.id,
            'currency': move.picking_id and move.picking_id.company_id.currency_id.id or False,
        }
        if move.picking_id.type == 'in' and move.product_id.cost_method == 'average':
            partial_move.update(update_cost=True, **self._product_cost_for_average_update(cr, uid, move))

        return partial_move


    #def _partial_move_for(self, cr, uid, move, context=None):
        # get picking_id
        #purchase_id = move.picking_id.purchase_id
        # set None, this is for not use super from purchase
        #move.picking_id.purchase_id = None
        # call super
        #partial_move = super(stock_partial_picking, self)._partial_move_for(cr, uid, move, context=context)
        #print '** LOS DATOS SON: ***', partial_move
        # set value picking_id
        #move.picking_id.purchase_id = purchase_id
        # return value
        #return partial_move


    def _product_cost_for_average_update(self, cr, uid, move):
        # Be aware of an OpenERP Bug !! If your price_type
        # IS NOT in your comapny currency, AVG price is wrong.
        # Currently, the cost on the product form is supposed to be expressed
        # in the currency of the company owning the product. OpenERP
        # read the average price from price_get method, which
        # convert the price to company currency.
        # So, in case you have:
        #   Rate from CHF to EUR 1.2
        #   Company in CHF
        #   Price type in EUR
        #   Product AVG price = 10.-
        #   Reception new product with cost 15.- (in CHF in price_unit
        #   of moves)
        #   The price_get will return the current average price in CHF of 12.-
        #   The price computed will be =(12 * qty + 15 * qty') / (qty + qty')
        #   in CHF. The new cost will be store as is in the procuct
        #   standard_price instead of converting the result in EUR
        # Reference : https://bugs.launchpad.net/ocb-addons/+bug/1238525
        res = super(
            stock_partial_picking, self)._product_cost_for_average_update(
                cr, uid, move)
        _logger.debug('Before res stock_partial_picking `%s`', res)
        # Re-take the cost from the PO line landed_costs field
        if move.purchase_line_id:
            if move.purchase_line_id.landing_costs_order > 0:
                currency_amount = move.purchase_line_id.landed_costs
                po_obj = self.pool.get('purchase.order')
                po = po_obj.browse(cr, uid, move.purchase_line_id.order_id.id)
                if po:
                    cur_obj = self.pool.get('res.currency')
                    cur = po.pricelist_id.currency_id
                    currency_amount = cur_obj.compute(cr, uid, cur.id, po.company_id.currency_id.id, move.purchase_line_id.landed_costs)
                res['cost'] = (currency_amount /
                               move.purchase_line_id.product_qty)
                res['currency'] = po.company_id.currency_id.id
        _logger.debug('After res stock_partial_picking `%s`', res)
        return res
