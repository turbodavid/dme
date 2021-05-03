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
import datetime as dt
from openerp.exceptions import Warning as UserError
from datetime import datetime

class invoice_report(models.TransientModel):

    _name = 'invoice.report'
    _description = 'Invoice Report'

    _defaults = {
        'date_start': lambda *a: dt.date.today().strftime('%Y-%m-%d'),
        'date_end': lambda *a: dt.date.today().strftime('%Y-%m-%d'),
    }

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id
    )
    date_start = fields.Date(
        'Date Start',
    )
    date_end = fields.Date(
        'Date End',
    )
    detail_ids = fields.One2many(
        'invoice.report.detail',
        'invoice_report_id',
        string='Details',
    )
    category_ids = fields.Many2many(
        'product.category', string='Category',
    )

    def get_category_child(self, category_id):
        query = """Select Id, parent_id
                   From product_category 
                   Where parent_id in (%s)""" % category_id

        # query
        self.env.cr.execute(query)
        registros = self.env.cr.fetchall()
        list_category = []
        for move in registros:
            list_category += self.get_category_child(move[0])
            if move[0] not in list_category:
                list_category.append(move[0])
        return list_category

    def quitarAcentos(x, cadena):
        nueva_cadena = ''
        if cadena > '':
            for l in cadena:
                x = l
                if x == u'Ñ':
                    x = 'N'
                elif x == u'ñ':
                    x = 'n'
                elif x == u'Á':
                    x = 'A'
                elif x == u'É':
                    x = 'E'
                elif x == u'Í':
                    x = 'I'
                elif x == u'Ó':
                    x = 'O'
                elif x == u'Ú':
                    x = 'U'
                elif x == u'Ü':
                    x = 'U'
                elif x == u'á':
                    x = 'a'
                elif x == u'é':
                    x = 'e'
                elif x == u'í':
                    x = 'i'
                elif x == u'ó':
                    x = 'o'
                elif x == u'ú':
                    x = 'u'
                elif x== u'°':
                    x = ''
                elif x== u'¨':
                    x = ''
                elif x == u'´':
                    x = ''
                elif x == u',':
                    x = ''
                nueva_cadena = nueva_cadena + x
        if nueva_cadena == '':
            nueva_cadena = str(cadena)
        return nueva_cadena

    @api.multi
    def execute_report(self):
        list_category = [0]
        # gets Childs Ids
        for category_id in self.category_ids:
            if category_id.id not in list_category:
                list_category.append(category_id.id)
            list_category += self.get_category_child(category_id.id)

        where_filter = """
        Where ai.type = 'out_invoice' 
        And ai.state in ('open', 'paid')  
        And(ai.date_invoice - interval '1h' * 7) >= '%s' 
        And(ai.date_invoice - interval '1h' * 7) <= '%s %s' 
        And ai.company_id in (% s) """ % (self.date_start,
                                                         self.date_end, '23:59:59',
                                                         self.company_id.id)
        if len(list_category) > 1:
            if where_filter <> '':
                where_filter = where_filter + "And pt.categ_id in %s " % str(tuple(list_category))

        query = """Select JM.Id, JM.Name, JM.Linea, JM.price_subtotal, (JM.NCR).Folio, (JM.NCR).Fecha, (JM.NCR).Importe,
                   JM.invoice_payment_date, JM.state, JM.price_subtotal - Coalesce((JM.NCR).Importe,0) as net_sale,
                   JM.Familia, JM.Proveedor, JM.quantity, JM.residual
                   FROM(
                   Select distinct ai.Id, pt.name, get_categ_secondlevel(pt.categ_id,1) Linea, ail.price_subtotal,
                        --public.fn_get_ncr_invoice_product(ai.id, ail.product_id) as amount_ncr
                        public.fn_get_ncr_invoice_product_array(ai.id, ail.product_id) ncr,
                        payment.last_rec_date as invoice_payment_date, ai.state,
                        get_categ_firstlevel(pt.categ_id) as Familia,pc.name as Proveedor,
                        ail.quantity, ai.residual
                   From account_invoice ai 
                   inner join account_invoice_line ail on ai.id = ail.invoice_id
                   inner join product_product p on ail.product_id = p.id
                   inner join product_template pt on p.product_tmpl_id = pt.id
                   left join product_category pc ON (pt.categ_id = pc.id) 
                   left join fn_get_payment(ai.move_id) Payment ON (ai.move_id = payment.move_id) 
                   """

        query = query + where_filter + ')JM Order by JM.Id'
        # query
        #print query
        self.env.cr.execute(query)
        registros = self.env.cr.fetchall()
        if len(registros) > 0:
            detail_ids = []
            date_format = "%Y-%m-%d"
            id_factura =  registros[0][0] # Primer registro
            residual = registros[0][13]  # Saldo
            for move in registros:
                #verifica si cambia de id factura, asiga el nuevo Id factura y el Saldo
                if id_factura <> move[0]:
                    id_factura = move[0]
                    residual= move[13]

                account_invoice_obj = self.env['account.invoice'].browse(move[0])
                days = 0
                credit_type = ''
                #has payment date
                if move[7]:
                    f1 = datetime.strptime(account_invoice_obj.date_invoice, date_format)
                    f2 = datetime.strptime(move[7], date_format)
                    days = (f2 - f1).days
                    credit_type = 'CONTADO' if days <= 30 else 'CRÉDITO'


                rs = {
                    'invoice_report_id': self.id,
                    'invoice_date': account_invoice_obj.date_invoice,
                    'invoice_folio': account_invoice_obj.internal_number,
                    'sale_name': account_invoice_obj.user_id.name,
                    'client_name': account_invoice_obj.partner_id.name,
                    'invoice_refund_date': move[5] or None,
                    'invoice_refund_folio': move[4] or '',
                    'invoice_amount': move[3] or 0.0,
                    'invoice_refund_amount': move[6] or 0.0,
                    'product': move[1],
                    'line': move[2],
                    'invoice_payment_date': move[7],
                    'state': move[8],
                    'days': days,
                    'credit_type' : credit_type,
                    'net_sale' : move[9] or 0.0,
                    'family': move[10],
                    'supplier': move[11],
                    'quantity': move[12],
                    'residual': residual
                }
                #sigue siendo la misma factura
                if id_factura == move[0]:
                    residual = 0
                detail_ids.append(rs)
            self.detail_ids = detail_ids
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'invoice.report.aeroo',
                    'datas': {
                        'model': 'invoice.report',
                        'id': self.id,
                        'ids': [self.id],
                        'report_type': 'ods'
                    },
                    'nodestroy': True
            }
        else:
            raise UserError("There are no records.")