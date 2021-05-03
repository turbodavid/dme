#!/usr/bin/env python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2019 Grupo MORSA - http://www.morsa.com.mx
#    All Rights Reserved.
############################################################################
#    Coded by:
#       David Alberto Perez Payán (davidperez@dmesoluciones.com)
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

from openerp.addons.web.controllers.main import Session
from openerp import fields, models, api
import datetime as dt
import locale
from openerp.exceptions import Warning as UserError
from datetime import datetime, timedelta

class EmployeeExpenses(models.TransientModel):
    _name = 'employee.expenses.report'
    _description = 'Reportes de Gastos de Empleados'

    _defaults = {
        'date_start': lambda *a: dt.date.today().strftime('%Y-%m-%d'),
        'date_end': lambda *a: dt.date.today().strftime('%Y-%m-%d'),
    }

    def _get_enterprise_used(self):
        sesion = Session()
        informacion = sesion.get_session_info()
        bd = informacion.get('db')

        return bd[0:3]

    def _get_account_receivable_default(self):

        acc_id = 1181
        company = self._get_enterprise_used()
        if company == 'GMM':
            acc_id = 1888
        elif company == 'MOR':
            acc_id = 1919

        return acc_id

    def _get_account_expense_parent_default(self):

        acc_id = 747
        company = self._get_enterprise_used()
        if company == 'GMM':
            acc_id = 2218
        elif company == 'MOR':
            acc_id = 887

        return acc_id

    date_start = fields.Date(
        'Fecha Inicial:',
    )

    date_end = fields.Date(
        'Fecha Final:',
    )

    acc_employee = fields.Many2one(
        'account.account',
        'Cuenta Deudora Viaticos',
        default=lambda self: self._get_account_receivable_default(),
        required=True,
        domain=[('type', '=', 'receivable')],
    )

    acc_expense_parent = fields.Many2one(
        'account.account',
        'Cuenta Gastos Viaticos',
        default=lambda self: self._get_account_expense_parent_default(),
        required=True,
        domain=[('type', '=', 'view'), ('code', 'like', '610-')],
    )

    expense_total = fields.Float('Expenses Total')

    lines = fields.One2many(
        'employee.expenses.report.detail',
        'employee_expenses_report_id',
        string='Viaticos Pagados')

    lines2 = fields.One2many(
        'employee.provenexpenses.report.detail',
        'employee_expenses_report_id',
        string='Viaticos Comprobados')

    date_range = fields.Char('Fecha Inicial a Imprimir')

    @api.multi
    def expenses_report(self):

        # query = """
        #     select ai.internal_number DoctoOrigen,
        #         substring( gto.name from 3 for position('|' in gto.name)-3) gasto,
        #         concat(trim(aaexp.code), ' ', trim(aaexp.name)) expense_category,
        #         sum(ail.price_subtotal_signed + ail.tax_amount_signed) expense_amount
        #     from account_invoice ai
        #         inner join hr_expense_expense gto on (gto.id = ai.expense_id)
        #         inner join account_invoice_line ail on (ail.invoice_id = ai.id)
        #         inner join account_account aaexp on (ail.account_id = aaexp.id)
        #     where left(gto.name,1) = '6' and
        #         gto.date_post between '%s'  and '%s' and aaexp.parent_id  != %s
        #     group by ai.internal_number,gto.name, aaexp.code, aaexp.name
        #     order by ai.internal_number;
        # """ % (self.date_start, self.date_end, self.acc_expense_parent.id)
        #
        # try:
        #     self.env.cr.execute(query)
        #     registros = self.env.cr.fetchall()
        # except Exception:
        #     self.env.cr.rollback()
        #     raise
        #
        # if len(registros) > 0:
        #     msg = 'Los siguientes documentos NO pertenecen al grupo de Cuentas: %s. \n' % self.acc_expense_parent.code
        #     for move in registros:
        #         msg += "Gasto/Factura: %s. Cuenta asignada: %s. Importe: %s. \n" \
        #                % (move[0], move[2], '{0:.2f}'.format(move[3]))
        #
        #     raise UserError(msg)

        locale.setlocale(locale.LC_ALL, "es_MX.UTF-8")
        query = self._sql_acumulado()

        try:
            self.env.cr.execute(query)
            registros = self.env.cr.fetchall()
        except Exception:
            self.env.cr.rollback()
            raise

        total = 0
        lines = []
        lines2 = []
        if len(registros) > 0:
            for move in registros:

                total += move[2]

                rs = {
                    'employee_expenses_report_id': self.id,
                    'employee_cu': move[0],
                    'employee_name': move[1],
                    'expense_amount': move[2],
                    }

                lines.append(rs)
                lines2.append(rs)

            self.expense_total = total
            #'{0:.2f}'.format(debit)
            self.lines = lines
            self.lines2 = lines2

            self.date_range = datetime.strftime(datetime.strptime(self.date_start, '%Y-%m-%d'), '%d de %B de %Y').upper() + \
                    " AL " + datetime.strftime(datetime.strptime(self.date_end, '%Y-%m-%d'), '%d de %B de %Y').upper()

            reportdict = {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'employee.expenses.report.aeroo',
                    'datas': {
                        'model': 'employee.expenses.report',
                        'id': self.id,
                        'ids': [self.id],
                        'report_type': 'xls'
                    },
                    'nodestroy': True
            }

            return reportdict
        else:
            raise UserError("There are no records.")

        return

    def _sql_acumulado(self):

        sql = self._get_viaticos()
        sql += """
                select concat('CU', '-', lpad(emp.id::text, 7, '0')) cu_empleado, 
                        upper(emp.name_related) nombre_empleado, sum(debit) importe
                from viaticos inner join hr_employee emp on (emp.address_id = viaticos.partner_id)
                group by emp.id, emp.name_related
                order by emp.id;
            """

        return sql

    def _get_viaticos(self):

        sql = """
                with viaticos as 
                (
                    select aml.id aml_id, aml.account_id, concat(trim(aa.code), ' ', trim(aa."name")) account_ant, 
                            aml."date", partner_id, debit, aml."ref", rp."name"
                    from account_move_line aml inner join account_journal aj on (aml.journal_id = aj.id)
                            inner join res_partner rp on (aml.partner_id = rp.id)
                            inner join account_account aa on (aml.account_id = aa.id)
                    where aml.account_id = %s and left(aj.code,2) = 'AN' and debit > 0
                            and aml."date" between '%s' and '%s'
                )    
            """ % (self.acc_employee.id, self.date_start, self.date_end)

        return sql

    def _valida_reporte(self):

        query = """                    
            select ai.internal_number DoctoOrigen,
                substring( gto."name" from 3 for position('|' in gto."name")-3) gasto,
                concat(trim(aaexp.code), ' ', trim(aaexp.name)) expense_category,
                sum(ail.price_subtotal_signed + ail.tax_amount_signed) expense_amount
            from account_invoice ai 
                inner join hr_expense_expense gto on (gto.id = ai.expense_id) 
                inner join account_invoice_line ail on (ail.invoice_id = ai.id)
                inner join account_account aaexp on (ail.account_id = aaexp.id)
            where left(gto.name,1) = '6' and 
                gto.date_post between '%s'  and '%s' and aaexp.parent_id  != %s 
            group by ai.internal_number,gto."name", aaexp.code, aaexp."name"
            order by ai.internal_number;                
        """ % (self.date_start, self.date_end, self.acc_expense_parent.id)

        try:
            self.env.cr.execute(query)
            registros = self.env.cr.fetchall()
        except Exception:
            self.env.cr.rollback()
            raise

        if len(registros) > 0:
            msg = 'Los siguientes documentos NO pertenecen al grupo de Cuentas: %s. \n' % self.acc_expense_parent.code
            for move in registros:
                msg += "Gasto/Factura: %s. Cuenta asignada: %s. Importe: %s. \n" \
                       % (move[0], move[2], '{0:.2f}'.format(move[3]))

            UserWarning(msg)
            return False

        return True

#class ExpensesReportDetail, pagos de viáticos
class ExpensesReportDetail(models.TransientModel):
    _name = 'employee.expenses.report.detail'

    employee_expenses_report_id = fields.Many2one(
          'employee.expenses.report', 'Employee Expenses',
    )

    employee_cu = fields.Char(
        'Employee CU',
    )
    employee_name = fields.Char(
        'Employee Name',
    )

    expense_amount = fields.Float()

# class ExpensesReportDetail

#class ProvenExpensesReportDetail, viáticos comprobados
class ProvenExpensesReportDetail(models.TransientModel):
    _name = 'employee.provenexpenses.report.detail'

    employee_expenses_report_id = fields.Many2one(
          'employee.expenses.report', 'Employee Expenses',
    )

    employee_cu = fields.Char(
        'Employee CU',
    )
    employee_name = fields.Char(
        'Employee Name',
    )

    expense_amount = fields.Float()
    proven_expense_amount = fields.Float()
    positive_balance = fields.Float()
    negative_balance = fields.Float()

# class ProvenExpensesReportDetail
