# -*- coding: utf-8 -*-

from openerp import api, models
from openerp.exceptions import Warning as UserError
from openerp.osv import osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp.modules.registry import RegistryManager

class AccountVoucherConfirm(models.TransientModel):
    """Confirm the selected vouchers"""

    _name = "account.voucher.confirm"
    _description = __doc__

    @api.multi
    def voucher_confirm(self):
        # context = dict(self._context or {})
        # active_ids = context.get("active_ids", []) or []

        # for record in self.env["account.voucher"].browse(active_ids):
        #     if record.state not in ("draft", "proforma", "proforma2"):
        #         raise UserError(
        #             _(
        #                 "Los pagos seleccionados no puede ser confirmados por no están en "
        #                 "'Borrador' or 'Pro-Forma'."
        #             )
        #         )
        #     record.proforma_voucher()

        self.aplica_pagos()

        return {"type": "ir.actions.act_window_close"}

    def aplica_pagos(self):


        ou_filter = [('code', 'not ilike', '-'), ('code', '!=', 'OU1')]
        ous = self.env["operating.unit"].search(ou_filter, order='code')
        for ou in ous:

            vouchers = self.env["account.voucher"].search([
                                        ('type', '=', 'receipt'),
                                        ('state', '=', 'draft'),
                                        ('voucher_operating_unit_id', '=', ou.id)
                                        ], order='id')
            count = 0
            for voucher in vouchers:

                try:
                    #print "Voucher ID:", voucher.id
                    voucher.proforma_voucher()
                    count += 1
                    if count >= 5:
                        self.env.cr.commit()
                        count = 0
                except:
                    continue

        return
