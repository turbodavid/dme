# -*- coding: utf-8 -*-
# © 2009 Pexego/Comunitea
# © 2016 Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from openerp import api, fields, models, _
import logging
import re

class AccountBalanceReportingTemplateLineExcel(models.Model):
    _name = "account.balance.reporting.template.line.excel"
    _description = (
        "Account balance report template line / Accounting concept template "
        "Adds the Excel cell where the balances of this line will be show.")

    template_line_id = fields.Many2one(
        comodel_name='account.balance.reporting.template.line', string='Template Line',
        ondelete='cascade')

    name = fields.Char(
        string='Concept', size=64, required=True,
        help="Concept name that will be showed")

    sheet_acum = fields.Char(
        string='Sheet Name for Acumulative Balance', size=64,
        help='Sheet Name where the Acumulative Balance will be showed')

    sheet_month = fields.Char(
        string='Sheet Name for Monthly Balance', size=64,
        help="Sheet Name where the Monthly Balance will be showed, empty if there's no monthly balance")

    cell_acum_current = fields.Char(
        string="Cell for current period balance", size=4,
        help="Cell (row/col) position for the current balance")

    cell_acum_previous = fields.Char(
        string="Cell for previous period balance", size=4,
        help="Cell (row/col) position for the previous balance")

    cell_month_current = fields.Char(
        string="Cell for current month balance", size=4,
        help="Cell (row/col) position for the current balance, empty if there's no monthly balance" )

    cell_month_previous = fields.Char(
        string="Cell for previous month balance", size=4,
        help="Cell (row/col) position for the previous balance, empty if there's no monthly balance")

    corporate_expense = fields.Boolean("Is a Corporate Expense?", default=False,
                                       help="Select if this Concept is a Corporate Expense")

    operating_unit_ids = fields.One2many(
        'account.balance.reporting.template.line.excel.ou', 'excel_id', 'OUs'
    )

    def excel_template(self):


        return True

    def _get_max_period(self, reportid):
        report = self.env['account.balance.reporting.line']
        reportid = report.search([('id', '=', reportid)])
        tmpl = reportid.template_id
        maxperiod = ''
        return maxperiod

# class AccountBalanceReportingTemplateLineExcel
class AccountBalanceReportingTemplateLineExcelOU(models.Model):
    _name = "account.balance.reporting.template.line.excel.ou"
    _description = (
        "Operating Unit that limits the Excel Concept.")

    excel_id = fields.Many2one(
        comodel_name='account.balance.reporting.template.line.excel', string='Excel Concept ID',
        ondelete='cascade')

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit', string='OUs', ondelete='cascade'
    )

    _sql_constraints = [
       ('excel_line_code_uniq', 'unique(excel_id,operating_unit_id)',
        _("Only one Code per Operating Unit can be assigned!"))
        ]

    # @api.multi
    # def default_get(self):
    #     fields = self._fields
    #     res = super(AccountBalanceReportingTemplateLineExcelOU, self).default_get(fields)
    #     ids = []
    #     #id = self.create({'excel_id': self.env.context['excel_id']})
    #     ids.append({'excel_id': self.env.context['excel_id']})
    #
    #     res['result_ids'] = ids
    #    return res

# class AccountBalanceReportingTemplateLineExcelOU


class AccountBalanceReportTemplate(models.Model):
    _inherit = 'account.balance.reporting.template'

    use_materialized_view = fields.Boolean("Use Materialized View", default=False,
                                           help="Select if a Report with this Template will use Materialized View for processing")
# class AccountBalanceReportTemplate(models.Model):

class AccountBalanceReportTemplateLine(models.Model):
    _inherit = 'account.balance.reporting.template.line'

    template_line_excel_ids = fields.One2many('account.balance.reporting.template.line.excel', 'template_line_id', 'Template Excel ID')

    @api.model
    def _get_action_window_excel_concepts(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'name': _('Excel Concepts'),
            'res_model': 'account.balance.reporting.template.line.excel',
            'context': {'default_template_line_id': self.id},
            'target': 'current',
        }

    @api.multi
    def excel_concepts(self):
        self.ensure_one()
        res = self._get_action_window_excel_concepts()
        res['domain'] = [('template_line_id', 'in', self.ids)]

        return res
# class AccountBalanceReportingTemplateLine


class AccountBalanceReporting(models.Model):
    _inherit = "account.balance.reporting"

    @api.multi
    def action_calculate(self):

        super(AccountBalanceReporting, self).action_calculate()

        #if self.template_id.use_materialized_view:
        #    self._refresh_materialized_view()

        return True

    def _refresh_materialized_view(self):

        sql = """
            refresh materialized view concurrently  gastos_gmm_acc;
            reindex index gastos_gmm_index;
            """

        self.env.cr.execute(sql)

        return True
# class AccountBalanceReporting(models.Model):

class AccountBalanceReportingLineforExcel(models.Model):
    _inherit = "account.balance.reporting.line"
    _order = "sequence, code"

    @api.multi
    def _get_account_balance(self, expr, domain, balance_mode=0):
        """It returns the (debit, credit, balance*) tuple for a account with
        the given code, or the sum of those values for a set of accounts
        when the code is in the form "400,300,(323)"

        Depending on the balance_mode, the balance is calculated as follows:
          Mode 0: debit-credit for all accounts (default);
          Mode 1: debit-credit, credit-debit for accounts in brackets;
          Mode 2: credit-debit for all accounts;
          Mode 3: credit-debit, debit-credit for accounts in brackets.

        Also the user may specify to use only the debit or credit of the
        account instead of the balance writing "debit(551)" or "credit(551)".
        """

        domain_ous = self._get_operating_units()
        move_line_obj = self.env['account.move.line']
        account_obj = self.env['account.account']
        logger = logging.getLogger(__name__)
        res = 0.0
        company_id = self[:1].report_id.company_id.id
        # We iterate over the accounts listed in "code", so code can be
        # a string like "430+431+432-438"; accounts split by "+" will be added,
        # accounts split by "-" will be substracted.
        move_lines = self.env['account.move.line']
        for code in expr.split(','):
            # re.findall(r'(-?\w*\(?[0-9a-zA-Z_]*\)?)', expr):
            # Check if the code is valid (findall might return empty strings)
            code = code.strip()
            if not code:
                continue
            sign, acc_code, mode, sign_mode = self._get_code_sign_mode(
                code, balance_mode)
            # Search for the account (perfect match)
            accounts = account_obj.search(
                [('code', '=', acc_code), ('company_id', '=', company_id)])
            if not accounts:
                # Search for a subaccount ending with '0'
                accounts = account_obj.search(
                    [('code', '=like', '%s%%0' % acc_code),
                     ('company_id', '=', company_id)])
            if not accounts:
                logger.warning("Account with code '%s' not found!", acc_code)
                continue
            account_ids = accounts._get_children_and_consol()
            domain_account = list(domain)
            if domain_ous:
                domain_account.append(domain_ous)
            domain_account.append(('account_id', 'in', account_ids))
            domain_account.append(('state', '=', 'valid'))
            group = move_line_obj.read_group(
                domain_account, ['debit', 'credit'], [])[0]
            move_lines += move_line_obj.search(domain_account)
            if mode == 'debit':
                res -= (group['debit'] or 0.0) * sign
            elif mode == 'credit':
                res += (group['credit'] or 0.0) * sign
            else:
                res += (sign * sign_mode *
                        ((group['debit'] or 0.0) - (group['credit'] or 0.0)))
        return res, move_lines

    def _get_operating_units(self):

        domain = ''
        excel_ids = self.template_line_id.template_line_excel_ids.ids
        if excel_ids:
            sql = """
                select operating_unit_id
                from account_balance_reporting_template_line_excel_ou abrtleou
                where excel_id in %s
                """ % str(tuple(excel_ids)).replace(",)", ")")

            self.env.cr.execute(sql)
            ous = self.env.cr.fetchall()

            if ous:
                ous = [x[0] for x in ous]
                domain = ('operating_unit_id', 'in', ous)

        return domain
# class AccountBalanceReportingLine(models.Model):

