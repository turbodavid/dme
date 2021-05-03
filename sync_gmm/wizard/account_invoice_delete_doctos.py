# -*- coding: utf-8 -*-

from openerp import api, models
from openerp.exceptions import Warning as UserError
from openerp.osv import osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp.modules.registry import RegistryManager

class AccountInvoiceDeleteDoctos(models.TransientModel):
    """Deleted selected invoices breaking the ERP rules"""

    _name = "account.invoice.delete.doctos"
    _description = __doc__

    @api.multi
    def invoice_delete_doctos(self):

        context = dict(self._context or {})
        active_ids = context.get("active_ids", []) or []

        where = str(tuple(active_ids)).replace(",)", ")")
#        if len(active_ids) == 1:
#            where = '(' + str(active_ids[0]) + ')'
        sqlfix = """
            with invoices as (
                select state, id, "number", internal_number, cfdi_id, "type", origin
                from account_invoice ai 
                where state = 'draft' and id in %s
                )
            """ % where
        sql = sqlfix + """               
                delete from ir_attachment_facturae_mx ir
                using invoices
                where ir.id = invoices.cfdi_id;
                """
        sql += sqlfix + """
                delete from ir_attachment ir
                using invoices
                where ir.res_id = invoices.id and ir.res_model = 'account.invoice';
                """
        sql += sqlfix + """
                update account_invoice ai set internal_number = null, "number" = null, cfdi_id = null 
                from invoices 
                where ai.id = invoices.id;
                """

        self.env.cr.execute(sql)
        #self.env.cr.fetchall()

        for invoice in self.env["account.invoice"].browse(active_ids):
            invoice.unlink()

        return {"type": "ir.actions.act_window_close"}

