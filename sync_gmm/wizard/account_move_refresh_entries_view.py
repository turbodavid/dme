# -*- coding: utf-8 -*-

from openerp import api, models
from openerp.exceptions import Warning as UserError
from openerp.osv import osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp.modules.registry import RegistryManager
from openerp.addons.web.controllers.main import Session

class AccountMoveRefreshEntriesView(models.TransientModel):
    """Actualiza los movimiento en la vista account_entries_report"""

    _name = "account.move.refresh.entries.view"
    _description = __doc__

    @api.multi
    def refresh_view_confirm(self):
        context = dict(self._context or {})
        active_ids = context.get("active_ids", []) or []

        query = "refresh materialized view concurrently account_entries_report;"
        self.env.cr.execute(query)

        return {"type": "ir.actions.act_window_close"}

class AccountMoveRefreshDiotView(models.TransientModel):
    """Actualiza los movimiento de la DIOT que nos calculados de forma automática"""

    _name = "account.move.refresh.diot.view"
    _description = __doc__

    @api.multi
    def refresh_diot_confirm(self):
        context = dict(self._context or {})
        active_ids = context.get("active_ids", []) or []

        scompany = self.get_enterprise_used()
        query = ""
        if scompany == 'GMM':
            query = self.get_sql_gmm()
        elif scompany == 'VOH':
            query = self.get_sql_voh()
        elif scompany == 'MOR':
            query = self.get_sql_mor()

        if query:
            self.env.cr.execute(query)

        return {"type": "ir.actions.act_window_close"}

    def get_enterprise_used(self):
        sesion = Session()
        informacion = sesion.get_session_info()
        bd = informacion.get('db')

        return bd[0:3]

    def get_sql_gmm(self):

        sql = """
        with diot8 as
        (
            select  aml.move_id, aml.id move_line_id , aml."date", aml."ref", aml."name", aml.account_id, currency_id,
                    aml.debit, aml.credit, aml.tax2_base, aml.tax2_base_company_currency,
                    case when tax2_base = 0 then 0 else debit/tax2_base end calculado,
                    tax2_id, debit / 0.08 ImpOK
            from account_move_line aml 
                    inner join account_period ap on (aml.period_id = ap.id)
                    inner join account_move am on (aml.move_id = am.id)
            where aml."date" >= '2020-06-01' and not ap.special and aml.debit > 0 and aml.currency_id is null
               and aml.account_id in (3462) and	  debit > 0 
               and (aml.tax2_base is null 
                        or aml.tax2_base != debit / 0.08
                        or tax2_id is null 
                        or tax2_base_company_currency is null
               )
        )
        update account_move_line aml set tax2_id = 107, tax2_base = diot8.impok, tax2_base_company_currency = diot8.impok
        from diot8
        where aml.id = diot8.move_line_id;        
        """
        sql += self.sql_gmm_diot16(True) + self.sql_gmm_diot16(False)
        sql += self.sql_gmm_diot16(True, True) + self.sql_gmm_diot16(False, True)

        return sql

    def sql_gmm_diot16(self, withIVA=True, isUS=False):

        whereiva = """ and aml."name"  in ('IVA(16%) GASTOS CONTADO', 'IVA16GTOCONT - IVA(16%) GASTOS CONTADO')
                   """ if withIVA else ""

        wherecurr = " and aml.currency_id is null "
        impcurr = " diot.impok "
        if isUS:
            wherecurr = " and aml.currency_id != 34"
            impcurr = " diot.impokcurrency "

        sql = """
           with diot as 
          (
              select  aml.move_id, aml.id move_line_id, aml."date", aml."ref", aml."name", aml.account_id,
                      aml.debit, aml.credit, aml.tax2_base, aml.tax2_base_company_currency,
                      case when tax2_base = 0 then 0 else debit/tax2_base end calculado,
                      tax2_id, debit / 0.16 ImpOK, aml.currency_id, aml.amount_currency ImpOKCurrency
              from account_move_line aml 
                      inner join account_period ap on (aml.period_id = ap.id)
                      inner join account_move am on (aml.move_id = am.id)
                      --inner join account_tax atax on (aml."name" = atax."name")
              where aml."date" >= '2020-06-01' and not ap.special and aml.account_id in (1901, 1902) and debit > 0 
                  and (  
                       (aml.tax2_base_company_currency is null or aml.tax2_base is null or aml.tax2_base != debit / 0.16)
                      )
                  %s %s
          )
          update account_move_line aml set  tax2_base = %s, 
                  tax2_base_company_currency = diot.impok 
                  , tax2_id = case when aml.tax2_id is not null then aml.tax2_id 
                                      else case when aml.account_id = 1902 then 62 else 53 end end  
          from diot
          where aml.id = diot.move_line_id;
          """ % (whereiva, wherecurr, impcurr)

        return sql

    def get_sql_voh(self):
        sql = """
        with diot8 as
        (
            select  aml.id, aml.move_id, aml.id move_line_id, aml."date", aml."ref", aml."name", aml.account_id,
                    aml.debit, aml.credit, aml.tax2_base, aml.tax2_base_company_currency,
                    case when tax2_base = 0 then 0 else debit/tax2_base end calculado,
                    tax2_id, debit / 0.08 ImpOK
            from account_move_line aml 
                    inner join account_period ap on (aml.period_id = ap.id)
                    inner join account_move am on (aml.move_id = am.id)
            where aml."date" >= '2020-06-01' and not ap.special 
                and aml.account_id in (232,1214) and debit > 0 
                and ( tax2_id is null or tax2_id in (17))
                and ( tax2_base != debit / 0.08 or tax2_base is null or tax2_base_company_currency is null)
                and aml."name" = 'IVA(8%) GASTOS CONTADO'
        )
        update account_move_line aml set tax2_id = 17, 
            tax2_base = diot8.impok, tax2_base_company_currency = diot8.impok
        from diot8
        where aml.id = diot8.move_line_id;
        with diot as 
        (
            select  aml.move_id, aml.id move_line_id, aml."date", aml."ref", aml."name",
                    aml.debit, aml.credit, aml.tax2_base, aml.tax2_base_company_currency,
                    case when tax2_base = 0 then 0 else debit/tax2_base end calculado,
                    tax2_id, debit / 0.16 ImpOK
            from account_move_line aml 
                    inner join account_period ap on (aml.period_id = ap.id)
                    inner join account_move am on (aml.move_id = am.id)
            where aml."date" >= '2020-06-01' and aml."date" >= '2020-06-30' 
                    and not ap.special and aml.account_id = 232 and debit > 0 
                    and ( tax2_id is null or tax2_id in (8,12,17))
                    and ( tax2_base != debit / 0.16 or tax2_base is null or tax2_base_company_currency is null)
        )
        update account_move_line aml set  tax2_base = diot.impok, 
                        tax2_base_company_currency = diot.impok, 
                        tax2_id = case when (aml.tax2_id is null or aml.tax2_id = 17) then 12 else aml.tax2_id end
        from diot
        where aml.id = diot.move_line_id;
        """

        return sql

    def get_sql_mor(self):

        sql = """
        with diot8 as
        (
            select  aml.move_id, aml.id move_line_id, aml."date", aml."ref", aml."name", aml.account_id,
                    aml.debit, aml.credit, aml.tax2_base, aml.tax2_base_company_currency,
                    case when tax2_base = 0 then 0 else debit/tax2_base end calculado,
                    tax2_id, debit / 0.08 ImpOK
            from account_move_line aml 
                    inner join account_period ap on (aml.period_id = ap.id)
                    inner join account_move am on (aml.move_id = am.id)
            where aml."date" >= '2020-06-01' and not ap.special and 
               aml.account_id in (1962) and	  debit > 0 
               and (aml.tax2_base is null or aml.tax2_base != debit / 0.08)
        )
        update account_move_line aml set tax2_id = 109, tax2_base = diot8.impok, tax2_base_company_currency = diot8.impok
        from diot8
        where aml.id = diot8.move_line_id;
        with diot as 
        (
            select  aml.move_id, aml.id move_line_id, aml."date", aml."ref", aml."name",
                    aml.debit, aml.credit, aml.tax2_base, aml.tax2_base_company_currency,
                    case when tax2_base = 0 then 0 else debit/tax2_base end calculado,
                    tax2_id, debit / 0.16 ImpOK
            from account_move_line aml 
                    inner join account_period ap on (aml.period_id = ap.id)
                    inner join account_move am on (aml.move_id = am.id)
            where aml."date" >= '2020-01-01' and not ap.special and aml.account_id = 259 and debit > 0 
                and ( aml.tax2_base != debit / 0.16 
                                    or aml.tax2_base is null
                                    or tax2_base_company_currency is null 	
                                    or tax2_id is null 
                    )
        )
        update account_move_line aml set tax2_id = 30, tax2_base = diot.impok, tax2_base_company_currency = diot.impok
        from diot
        where aml.id = diot.move_line_id;
        """
        return sql

