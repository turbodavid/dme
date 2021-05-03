# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


{
    'name': 'Expense Report Date Capture',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 29,
    'summary': 'Expenses Report',
    'description': """
        -> Se agrego date_capture
        Basado en hr_expense_report
            OpenERP SA
            http://www.openerp.com            
            Addons: 9459
        create or replace view hr_expense_report as (
                 select
                     min(l.id) as id,
                     date_trunc('day',s.date) as date,
                     s.employee_id,
                     s.journal_id,
                     s.currency_id,
                     to_date(to_char(s.date_confirm, 'dd-MM-YYYY'),'dd-MM-YYYY') as date_confirm,
                     to_date(to_char(s.date_valid, 'dd-MM-YYYY'),'dd-MM-YYYY') as date_valid,
                     s.voucher_id,
                     s.user_valid as user_id,
                     s.department_id,
                     to_char(date_trunc('day',s.create_date), 'YYYY') as year,
                     to_char(date_trunc('day',s.create_date), 'MM') as month,
                     to_char(date_trunc('day',s.create_date), 'YYYY-MM-DD') as day,
                     avg(extract('epoch' from age(s.date_valid,s.date)))/(3600*24) as  delay_valid,
                     avg(extract('epoch' from age(s.date_valid,s.date_confirm)))/(3600*24) as  delay_confirm,
                     l.product_id as product_id,
                     l.analytic_account as analytic_account,
                     sum(l.unit_quantity * u.factor) as product_qty,
                     s.company_id as company_id,
                     sum(l.unit_quantity*l.unit_amount) as price_total,
                     (sum(l.unit_quantity*l.unit_amount)/sum(case when l.unit_quantity=0 or u.factor=0 then 1 else l.unit_quantity * u.factor end))::decimal(16,2) as price_average,
                     count(*) as nbr,
                     (select unit_quantity from hr_expense_line where id=l.id and product_id is not null) as no_of_products,
                     (select analytic_account from hr_expense_line where id=l.id and analytic_account is not null) as no_of_account,
                     s.state, to_char(date_trunc('day',s.date), 'YYYY-MM-DD') as date_capture
                 from hr_expense_line l
                 left join hr_expense_expense s on (s.id=l.expense_id)
                 left join product_uom u on (u.id=l.uom_id)
                 group by
                     date_trunc('day',s.date),
                     to_char(date_trunc('day',s.create_date), 'YYYY'),
                     to_char(date_trunc('day',s.create_date), 'MM'),
                     to_char(date_trunc('day',s.create_date), 'YYYY-MM-DD'),
                     to_date(to_char(s.date_confirm, 'dd-MM-YYYY'),'dd-MM-YYYY'),
                     to_date(to_char(s.date_valid, 'dd-MM-YYYY'),'dd-MM-YYYY'),
                     l.product_id,
                     l.analytic_account,
                     s.voucher_id,
                     s.currency_id,
                     s.user_valid,
                     s.department_id,
                     l.uom_id,
                     l.id,
                     s.state,
                     s.journal_id,
                     s.company_id,
                     s.employee_id,
                    to_char(date_trunc('day',s.date), 'YYYY-MM-DD')
            )
    """,
    'author': 'Jorge Medina',
    'depends': ['hr', 'account_voucher', 'account_accountant'],
    'data': ['hr_expense_report_view.xml'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
