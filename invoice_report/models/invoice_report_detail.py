#!/usr/bin/env python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2018 Grupo SACSA - http://www.gruposacsa.com.mx
#    All Rights Reserved.
############################################################################
#    Coded by:
#       Jorge Alfonso Medina Uriarte (desarrollo.sacsa@gruposacsa.com.mx)
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


from openerp import fields, models, api


class invoice_report_detail(models.TransientModel):

    _name = 'invoice.report.detail'

    invoice_report_id = fields.Many2one(
        'invoice.report', 'Invoice Report',
    )
    invoice_date = fields.Date(
        'Invoice Date',
    )
    invoice_folio = fields.Char(
        'Invoice Folio',
    )
    sale_name = fields.Char(
        'Sale Name',
    )
    client_name = fields.Char(
        'Client Name',
    )
    invoice_refund_date = fields.Date(
        'Invoice Refund Date',
    )
    invoice_refund_folio = fields.Char(
        'Invoice Refund Folio',
    )
    invoice_amount = fields.Float()
    invoice_refund_amount = fields.Float()
    product = fields.Char(
        'Product',
    )
    line = fields.Char(
        'Line',
    )
    invoice_payment_date = fields.Date(
        'Invoice Payment Date',
    )
    state = fields.Char(
        'State',
    )
    days = fields.Integer(
        'Days',
    )
    credit_type = fields.Char(
        'Credit Type',
    )
    net_sale = fields.Float()
    family = fields.Char(
        'Family',
    )
    supplier = fields.Char(
        'Supplier',
    )
    quantity = fields.Float()
    residual = fields.Float()