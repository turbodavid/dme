# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 OpenERP s.a. (<http://openerp.com>).
#
#    Coded By:
#       Jesus Antonio Meza Espinoza (jesus.meza@dmesoluciones.com)
#       Jorge Alfonso Medina Uriarte (jorge.medina@dmesoluciones.com)
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

import time

from openerp.osv import fields, osv
from datetime import datetime
from openerp.report import report_sxw
#from l10n_mx_invoice_amount_to_text import amount_to_text_es_MX
from collections import OrderedDict
from num2words import num2words

class account_voucher(osv.Model):
    _inherit = 'account.voucher' 
    #Do not touch _name it must be same as _inherit
    #_name = 'account.voucher'
    
    _columns = {
        'payment_beneficiary': fields.boolean(string = "Payment to the beneficiary",
                                              help="Determine if shows the legend \'Amount to pay the beneficiary\' on report."),
    }
    _defaults = {
        'payment_beneficiary': lambda *a: False,
    }
    
parents = []
id_wizard = 0
class report_print_check(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        parents[:] = []
        #name beneficiary
        name_beneficiary = ''
        #check if come from wizard
        if context.get('active_model') == "account.voucher.wizard":
            #get active id
            id_wizard = context and context.get('active_id')
        else:
            id_wizard = 0
        #super
        super(report_print_check, self).__init__(cr, uid, name, context)        
        self.localcontext.update({
            'time': time,
            'convert_to_words': self._convert_to_words,
            'date_to_text': self._get_date_to_text,
            'month_and_day_to_text': self._get_month_and_day_to_text,
            'year_to_text': self._get_year,
            'parent_account': self._get_parent_account,
            'account': self._get_account,
            'amount_print': self._get_amount_print,
            'total_amount_debit': self._get_total_amount_debit,
            'total_amount_credit': self._get_total_amount_credit,
            'legend_payment_beneficiary': self._get_legend_payment_beneficiary,
            'get_lines': self.get_lines,
            'fill_stars' : self.fill_stars,
            'get_lines_check': self._get_lines_check,
            'get_lines_parent': self._get_lines_parent,
            'exist_line_parent': self._exist_line_parent,
            'getCreateUser': self._getCreateUser,
            'get_id_beneficiary': id_wizard,
            'get_name_beneficiary': self._get_name_beneficiary,
        })
    
    def fill_stars(self, amount):
        if amount:
            if len(amount) < 100:
                stars = 100 - len(amount)
                return ' '.join([amount,'*'*stars])

            else:
                return amount
    
    def get_lines(self, voucher_lines):
        result = []
        self.number_lines = len(voucher_lines)
        for i in range(0, min(10,self.number_lines)):
            if i < self.number_lines:
                res = {
                    'date_due' : voucher_lines[i].date_due,
                    'name' : voucher_lines[i].name,
                    'amount_original' : voucher_lines[i].amount_original and voucher_lines[i].amount_original or False,
                    'amount_unreconciled' : voucher_lines[i].amount_unreconciled and voucher_lines[i].amount_unreconciled or False,
                    'amount' : voucher_lines[i].amount and voucher_lines[i].amount or False,
                }
            else :
                res = {
                    'date_due' : False,
                    'name' : False,
                    'amount_original' : False,
                    'amount_due' : False,
                    'amount' : False,
                }
            result.append(res)
        return result
                
    def _convert_to_words(self, voucher):
        return num2words(voucher.amount, lang='es').upper() + ' ' + voucher.currency_id.name
        #return amount_to_text_es_MX.get_amount_to_text(self, voucher.amount, 'es_cheque', voucher.currency_id.name)
    
    def _get_date_to_text(self, date):
        MES=["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        dates = str(date).split('/')
        if len(dates) > 1:
            m = int(dates[1])
            return dates[0] + " de " + str(MES[m-1]) + " de " + dates[2]
        else:
            dates = str(date).split('-')
            m = int(dates[1])
            return dates[2] + " de " + str(MES[m-1]) + " de " + dates[0]
    
    def _get_month_and_day_to_text(self, date):
        MES=["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        dates = str(date).split('/')
        if len(dates) > 1:
            m = int(dates[1])
            return dates[0] + " de " + str(MES[m-1])
        else:            
            dates = str(date).split('-')
            m = int(dates[1])
            return dates[2] + " de " + str(MES[m-1])
    
    def _get_year(self, date):
        dates = str(date).split('/')
        if len(dates) > 1:
            return (str(date).split('-')[2])[2:] # retorna de "2016" -> 16
        else:
            dates = str(date).split('-')
            return (str(date).split('-')[0])[2:] # retorna de "2016" -> 16
    
    def _get_parent_account(self, account):
        return str(account.code)[:3]
    
    def _get_account(self, account):
        return str(account.code)[-7:]
    
    def _get_amount_print(self, amount):
        if amount > 0:
            return amount
        else:
            return '&nbsp;'
    
    def _get_total_amount_debit(self, voucher):
        #check if has bank statement
        if not voucher.account_bank_statement_id:
            move_ids = voucher.move_ids
        else:
            move_ids = voucher.account_bank_statement_id.move_line_ids
        #initialize
        total_amount = 0
        #
        for l in move_ids:
            total_amount += l.debit
        
        return total_amount
    
    def _get_total_amount_credit(self, voucher):
        #check if has bank statement
        if not voucher.account_bank_statement_id:
            move_ids = voucher.move_ids
        else:
            move_ids = voucher.account_bank_statement_id.move_line_ids
        #initialize
        total_amount = 0
        #
        for l in move_ids:
            total_amount += l.credit
        
        return total_amount
    
    def _get_legend_payment_beneficiary(self, voucher, origen):
        if voucher.payment_beneficiary:
            msj = '<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; border:1pt solid black; width:130px;text-align:center;">*** PARA ABONO EN CUENTA DEL BENEFICIARIO ***</td>'
            if voucher.print_legend_policy:
                if origen == 'policy':
                    return msj
                else:
                    return '<td>&nbsp;</td>'                    
            else:
                return msj
        else:
            return '<td>&nbsp;</td>'

    def _get_lines_check(self, voucher):
        order_lines = {}
        #check if has bank statement
        if not voucher.account_bank_statement_id:
            move_lines = voucher.move_ids
        else:
            move_lines = voucher.account_bank_statement_id.move_line_ids

        #get moves id and code parent
        for l in move_lines:
            major_account = self._get_parent_account(l.account_id)
            #order
            if major_account in ["201","202","203","204","205"]:
                major_account = "01" + major_account 
            elif major_account in ["118","119"]:
                major_account = "02" + major_account
            elif major_account in ["102"]:
                major_account = "03" + major_account
            else:
                major_account = "04" + major_account
            #set major account
            order_lines[l.id] = major_account
        #order dictionary
        order_lines = OrderedDict(sorted(order_lines.items(), key=lambda x: x[1]))
        #set dictionary sorted in list
        ids = []
        for o in order_lines:
            ids.append(o)
        #set context
        context = {}
        move_lines = self.pool.get('account.move.line').browse(self.cr, self.uid, ids, context)
        return move_lines  
    
    def _get_lines_parent(self, line, account_line_id, field, voucher):
        context = {}
        value = ''
        id = voucher.id
         #check if has bank statement
        if not voucher.account_bank_statement_id:
            moves_ids = voucher.move_ids
        else:
            moves_ids = voucher.account_bank_statement_id.move_line_ids
        
        id_line = str(account_line_id) + field + str(id)
        if id_line not in parents:
            #add to list
            parents.append(id_line)
            if (field == 'parent_id'):
                value = self._get_parent_account(line.account_id.parent_id)
            elif field == 'parent_id_name':
                value = line.account_id.parent_id.name
            if (field == 'account_id'):
                value = self._get_account(line.account_id)
            elif field == 'name':
                value = line.account_id.name
            elif field == 'partial':
                sum = 0
                for m in moves_ids:
                    #get major account 
                    major_account = line.account_id.id
                    line_account = m.account_id.id
                    #if major is equal a major of line, sum
                    if major_account == line_account:
                        value_cr_dr = m.debit + m.credit
                        #sum value
                        sum = sum + value_cr_dr
                value  = sum
                #change value 0 to empty
                if value == 0:
                    value = ''
            elif field == 'debit' or field == 'credit':
                sum = 0
                for m in moves_ids:
                    #get major account 
                    major_account = self._get_parent_account(line.account_id.parent_id)
                    line_account = self._get_parent_account(m.account_id)
                    #if major is equal a major of line, sum
                    if major_account == line_account:
                        value_cr_dr = m.debit if field == 'debit' else m.credit
                        #sum value
                        sum = sum + value_cr_dr
                value  = sum
                #change value 0 to empty
                if value == 0:
                    value = ''
        return value

    def _exist_line_parent(self, line, account_line_id,  field, id):
        res = 0
        id_line = str(account_line_id) + field + str(id)
        if id_line in parents:
            res = 1
        return res
    
    def _getCreateUser(self, voucher):
        create_user = ''
        for m in voucher.message_ids:
            if m.body == "<p>Comprobante contable creado</p>": # we need to change this part.
                create_user = m.author_id.name
        return create_user

    def _get_name_beneficiary(self, id):
        context = {}
        #get record
        account_voucher_wizard = self.pool.get('account.voucher.wizard').browse(self.cr, self.uid, [id], context=context)
        #return  beneficiary name
        return account_voucher_wizard[0].name

#from netsvc import Service

#del Service._services['report.account.print.check.top']
#del Service._services['report.account.print.check.middle']
#del Service._services['report.account.print.check.bottom']

report_sxw.report_sxw(
    'report.account.print.check.top',
    'account.voucher',
    'addons/account_check_writing/report/check_print_top.rml',
    parser=report_print_check,header=False
)
report_sxw.report_sxw(
    'report.account.print.check.middle',
    'account.voucher',
    'addons/account_check_writing/report/check_print_middle.rml',
    parser=report_print_check,header=False
)
report_sxw.report_sxw(
    'report.account.print.check.bottom',
    'account.voucher',
    'reports_sacsa/report/check_print_sacsa.mako',
    parser = report_print_check,
    header = False
)
