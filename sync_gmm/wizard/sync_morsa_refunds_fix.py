# -*- coding: utf-8 -*-

from openerp import api, models
from openerp.exceptions import Warning as UserError
from openerp.osv import osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp.modules.registry import RegistryManager

class SyncMorsaRefundsFix(models.TransientModel):
    """Fix the selected Refunds"""

    _name = "sync.morsa.refunds.fix"
    _description = __doc__

    @api.multi
    def customers_refunds_fix(self):

        context = dict(self._context or {})
        active_ids = context.get("active_ids", []) or []
        resrefunds = {}
        ou = ''
        cursor = ''
        conexion = ''
        smrefunds = self.env['sync.morsa.refunds']
        con_branch = self.env['sync.morsa.conexion']
        invoice = self.env['account.invoice']
        refundnumber = ''

        for record in smrefunds.browse(active_ids):

            if record.refund_id in resrefunds.keys() or record.invoice_type != 'out_invoice':
                continue

            smrtofix = smrefunds.search([("refund_uuid", "=", record.refund_uuid)], order="id_kardex")
            refundnumber = record.refund_number_serie + "-" + record.refund_number.strip()
            resrefunds.setdefault(record.refund_id, refundnumber)

            sql = "select id_kar, seriedoc, numdocto, tipomov, importe, iva from cxckardex " \
                  "where concat(trim(serie),'-',referencia::varchar) = '%s' order by id_kar;" % refundnumber

            if ou != record.operating_unit_id:
                if ou:
                    conexion.close()
                ou = record.operating_unit_id
                conexion = con_branch._get_conexion_direct(ou.ip_address, ou.data_base)
                cursor = conexion.cursor()

            cursor.execute(sql)
            refundsok = cursor.fetchall()

            res = {}
            for refund in refundsok:
                res.setdefault(refund[0], refund)

            refunds_to_sum = 0
            amount_paid = 0

            for refund in refundsok:

                serie = res[refund.id_kardex][1].strip()
                factura = str(res[refund.id_kardex][2])
                total = res[refund.id_kardex][4]
                subtotal = round(res[refund.id_kardex][4] / (1 + (res[refund.id_kardex][5] / 100)), 2)
                taxes = total - subtotal
                uuid = ''
                invoiceid = ''
                invoice = invoice.search([('number', '=', serie + '-' + factura)])
                if invoice:
                    uuid = invoice.cfdi_id.uuid
                    invoiceid = invoice.id

                toupdate = {'num_mov': res[refund.id_kardex][3],
                            'invoice_number': factura,
                            'invoice_number_serie': serie,
                            'amount_total': total,
                            'amount_taxes': taxes,
                            'amount_untaxed': subtotal,
                            'invoice_uuid': uuid,
                            'invoice_id': invoiceid
                        }
                if refund.state == 'draft':
                    toupdate.update({'state': 'open'})
                refund.write(toupdate)

                refunds_to_sum += subtotal
                amount_paid += total if refund.voucher_id else 0

            invoice = invoice.search([('id', '=', record.refund_id)])
            if invoice and invoice.amount_untaxed != refunds_to_sum:
                count = 0
                for il in invoice.invoice_line:
                    if count == 0:
                        iltokeep = il
                        count = 1
                        continue
                    il.unlink()

                total = refunds_to_sum
                iltokeep.write({'price_unit': total})
                invoice.button_reset_taxes()
                invoice.write({'residual': invoice.amount_total - amount_paid})


        return {"type": "ir.actions.act_window_close"}

    # def customers_refunds_fix(self):
    #
    #     sql = """
    #          with wrongnc as
    #          (
    #              select  smr.refund_id, smr.refund_uuid, smr.id_kardex
    #              from sync_morsa_refunds smr inner join operating_unit ou on (smr.operating_unit_id = ou.id)
    #              where invoice_type = 'out_invoice' and  invoice_number = refund_number and trim(invoice_number_serie) = ''
    #          )
    #          select distinct wrongnc.refund_id, smr.operating_unit_id,
    #                concat(trim(smr.refund_number_serie),'-',trim(smr.refund_number)) notcre,
    #                ou.ip_address, ou.data_base
    #          from sync_morsa_refunds smr inner join wrongnc on (smr.refund_uuid = wrongnc.refund_uuid)
    #              inner join operating_unit ou on (smr.operating_unit_id = ou.id)
    #          where smr.id_kardex != wrongnc.id_kardex
    #          order by smr.operating_unit_id, wrongnc.refund_id;
    #          """
    #
    #     self.env.cr.execute(sql)
    #     smrtofix = self.env.cr.fetchall()
    #     if len(smrtofix) == 0:
    #         UserWarning("No existen Notas de Crédito por Corregir")
    #         return
    #
    #     ou = ''
    #     cursor = ''
    #     conexion = ''
    #     con_branch = self.env['sync.morsa.conexion']
    #     for smr in smrtofix:
    #
    #         sql = "select id_kar, seriedoc, numdocto, tipomov, importe, iva from cxckardex " \
    #               "where concat(trim(serie),'-',referencia::varchar) = '%s';" % smr[2]
    #         if ou != smr[1]:
    #             if ou:
    #                 conexion.close()
    #             ou = smr[1]
    #             conexion = con_branch._get_conexion_direct(smr[3], smr[4])
    #             cursor = conexion.cursor()
    #
    #         cursor.execute(sql)
    #         refundsok = cursor.fetchall()
    #
    #         res = {}
    #         for refund in refundsok:
    #             res.setdefault(refund[0], refund)
    #
    #         tofix = self.search([('refund_id', '=', smr[0])], order="id_kardex")
    #
    #         invoice = self.env['account.invoice']
    #         refunds_to_sum = 0
    #         amount_paid = 0
    #         for refund in tofix:
    #
    #             serie = res[refund.id_kardex][1].strip()
    #             factura = str(res[refund.id_kardex][2])
    #             total = res[refund.id_kardex][4]
    #             subtotal = round(res[refund.id_kardex][4] / (1 + (res[refund.id_kardex][5] / 100)), 2)
    #             taxes = total - subtotal
    #             uuid = ''
    #             invoiceid = ''
    #             invoice = invoice.search([('number', '=', serie + '-' + factura)])
    #             if invoice:
    #                 uuid = invoice.cfdi_id.uuid
    #                 invoiceid = invoice.id
    #
    #             refund.write(
    #                 {'num_mov': res[refund.id_kardex][3],
    #                  'refund_id': smr[0],
    #                  'invoice_number': factura,
    #                  'invoice_number_serie': serie,
    #                  'amount_total': total,
    #                  'amount_taxes': taxes,
    #                  'amount_untaxed': subtotal,
    #                  'invoice_uuid': uuid,
    #                  'invoice_id': invoiceid
    #                  })
    #
    #             refunds_to_sum += subtotal
    #             amount_paid += total if refund.voucher_id else 0
    #
    #         invoice = invoice.search([('id', '=', smr[0])])
    #         if invoice and invoice.amount_untaxed != refunds_to_sum:
    #             count = 0
    #             for il in invoice.invoice_line:
    #                 if count == 0:
    #                     iltokeep = il
    #                     count = 1
    #                     continue
    #                 il.unlink()
    #
    #             total = refunds_to_sum
    #             iltokeep.write({'price_unit': total})
    #             invoice.button_reset_taxes()
    #             invoice.write({'residual': invoice.amount_total - amount_paid})
    #
    #     return {"type": "ir.actions.act_window_close"}
