    # coding: utf-8
# #############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# ############ Credits ########################################################
#    Coded by: David Perez                  <david.perez@pcsystems.mx>
# #############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
import time
from openerp.exceptions import Warning as UserError
from openerp.osv import fields, osv
from openerp import api, workflow
from openerp.addons import decimal_precision as dp
from openerp.tools.translate import _
import sync_conexion

PAYMENT_TYPE_CODE = '03'

class HrExpenseExpense(osv.Model):
    _inherit = "hr.expense.expense"

    def load_advances(self, cr, uid, ids, context=None):
        """ Load the expense advances table with the corresponding data. Adds
        account move lines that fulfill the following conditions:
            - Not reconciled.
            - Not partially reconciled.
            - Account associated of type payable.
            - That belongs to the expense employee or to the expense invoices
              partners.
        """
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        foliogasto = ''
        for exp in self.browse(cr, uid, ids, context=context):

            partner_id = exp.employee_id.address_home_id
            foliogasto = exp.name[2:exp.name.find("|")]
            tipo_gasto = exp.name[:1]
            folioanticipo = ''
            acondicion = ''
            aml_ids = []

            if tipo_gasto == '2':
                acc_id = partner_id.property_account_payable.id
                aml_ids = aml_obj.search(cr, uid, [('ref', '=', foliogasto), ('journal_id.type', 'in', ['bank', 'cash'])], context=context)
                if not aml_ids:
                    aml_ids = self._get_reembolso(cr, uid, foliogasto, exp, context=context)
            else:
                acc_id = partner_id.property_account_receivable.id

            acc_payable_ids = self.pool.get('account.account').search(cr, uid, [('id', '=', acc_id)], context=context)

            if tipo_gasto == '6':
                folioanticipo = self._get_viaticos(foliogasto)
            #     acondicion += [('account_id', 'in', acc_payable_ids)]
            #     aml_ids = aml_obj.search(cr, uid, acondicion , context=context)

            if not aml_ids:
                acondicion = [('reconcile_id', '=', False),
                                ('reconcile_partial_id', '=', False),
                                ('account_id', 'in', acc_payable_ids),
                                ('partner_id', '=', partner_id.id),
                                ('date', '>=', '2019-01-01'),
                                ('debit', '>', 0.0),
                            ]
                aml_ids = aml_obj.search(cr, uid, acondicion, context=context)

            vals = {}
            cr.execute(('SELECT aml_id FROM expense_advance_rel '
                        'WHERE expense_id != %s'), (exp.id,))
            already_use_aml = cr.fetchall()
            already_use_aml = [dat[0] for dat in already_use_aml]
            aml_ids = list(set(aml_ids) - set(already_use_aml))
            vals['advance_ids'] = \
                [(6, 0, aml_ids)]

            if folioanticipo:
                vals['note'] = 'El folio del anticipo que corresponde es: %s' % folioanticipo

            self.write(cr, uid, exp.id, vals, context=context)
        return True

    def _get_viaticos(self, foliogasto):

        acondicion = ''
        try:
            conexion = self.pool.get('sync.morsa.conexion')._get_conexion("conexion_openerp_expense_newportal.csv")
            sql = 'select folio_gasto from cxpgastosviaticos where folio_comprobacion = %s' % foliogasto
            crsgasto = conexion.cursor()
            crsgasto.execute(sql)
            gastos = crsgasto.fetchall()

            for gasto in gastos:
                #acondicion = [('ref', '=', '%s' % gasto[0])]
                acondicion = gasto[0]
                break
        except:
            raise

        return acondicion

    def _get_reembolso(self, cr, uid,  foliogasto, exp, context=None):
        #el  esta en  estatus = '1', estatugasto = 'A', pagar = '1'
        #mandarlo como si fuera anticipo
        conexion = self.pool.get('sync.morsa.conexion')._get_conexion("conexion_openerp_expense_newportal.csv")

        curanticipo = conexion.cursor()
        query_anticipos = self._get_sql_reembolsos(foliogasto)
        curanticipo.execute(query_anticipos)
        records = curanticipo.fetchall()

        amlid = []
        if not records:
            return amlid

        # folio                  0
        # fecha                  1
        # sucursal               2
        # notes                  3
        # importe                4
        # acrfolio               5
        # rfcfolio               6
        # nombrefolio            7
        # clabe                  8
        # partner_id_folio       9
        # bankcode               10
        # numctapagadora         11
        # bank_acc_id            12
        # bannkname              13

        try:

            sql_update = ''
            partnerid = ''
            msgdata = ''
            period  = ''
            obj_am = self.pool.get('account.move')
            obj_aml = self.pool.get('account.move.line')

            for record in records:

                if not period:
                    period = record[1][5:7] + "/" + record[1][0:4]
                    ap = self.pool.get('account.period').search(cr, uid, [('code', '=', period)], context=context)

                msgdata = 'Folio: ' + str(record[0]) + ". "
                partnerid = exp.employee_id.address_home_id.id

                journalid = self._get_journal_reembolsos(cr, uid, record, context=context)
                # ENCABEZADO
                header = {
                    'partner_id': partnerid,
                    'date': record[1],
                    'ref': record[0],
                    'journal_id': journalid,
                    'operating_unit_id': exp.operating_unit_id.id,
                    'company_id': 1,
                    'period_id': ap[0],
                    'narration': record[3] + '. Depositado a la cuenta: ' + record[8]
                }

                am = obj_am.create(cr, uid, header, context=context)

                adatos_ = [
                    [record[0], exp.employee_id.address_home_id.property_account_payable.id, record[4], 0],
                    [record[8], record[12], 0, record[4]]
                ]

                msgdata += "Cuenta Contable: " + exp.employee_id.address_home_id.property_account_payable.code + " " + \
                           exp.employee_id.address_home_id.property_account_payable.name

                # DETALLE DE POLIZA
                for i in (0, 1):
                    header = {
                        'partner_id': partnerid,
                        'name': adatos_[i][0],
                        'journal_id': journalid,
                        'account_id': adatos_[i][1],
                        'debit': adatos_[i][2],
                        'credit': adatos_[i][3],
                        'operating_unit_id': exp.operating_unit_id.id,
                        'company_id': 1,
                        'period_id': ap[0],
                        'move_id': am
                    }
                    aml = obj_aml.create(cr, uid, header, context=context)
                    if not amlid:
                        amlid = [aml]

                sql_update += "update cxpgastos set erp = '2' where folio = %s;" % (record[0])

            if sql_update:
                curanticipo.execute(sql_update)
                conexion.commit()
        except Exception as e:
            if msgdata:
                msgdata += "\n" + repr(e)
                raise UserError("Error procesando reembolso\n", msgdata)
            else:
                raise e
        finally:
            curanticipo.close()
            conexion.close()

        return amlid

    def _get_journal_reembolsos(self, cr, uid, record, context=None):

        journalcode = 'PR' + record[10] + record[11][-4:]
        obj_journal = self.pool.get('account.journal')
        journal = obj_journal.search(cr, uid, [('code', '=', journalcode)], context=context)
        journalid = ''
        if journal:
            journalid = journal[0]

        if not journalid:
            data = {
                'name': 'Pagos Reembolsos ' + record[13].title() + ' ' + record[11][-4:],
                'prefix': journalcode + '/%(y)s%(month)s/',
                'padding': 5,
                'number_next_actual': 1,
                'number_increment': 1,
                'implementation': 'standard'

            }
            sequence = self.pool.get('ir.sequence').create(cr, uid, data, context=context)
            obj_payment_type = self.pool.get('payment.type').search(cr, uid, [('code', '=', PAYMENT_TYPE_CODE)], context=context)

            data = {
                'name': 'Pagos Reembolsos ' + record[13].title() + ' ' + record[11][-4:],
                'code': journalcode,
                'type': 'bank',
                'payment_type_id': obj_payment_type[0],
                'default_debit_account_id': record[12],
                'default_credit_account_id': record[12],
                'update_posted': True,
                'sequence_id': sequence

            }
            journalid = obj_journal.create(cr, uid, data, context=context)

        return journalid

    def _get_sql_reembolsos(self, foliogasto):

        sql = ("""
            select  g.folio, to_date(g.ref_pago, 'YYYYMMDD') fecha, g.sucursal, trim(g.referencia) notes, 
                    g.importe, trim(g.acreedor) acrfolio, trim(acr.rfc) rfcfolio, trim(acr.nombre) nombrefolio, trim(acr.clabe) clabe, 
                    scor.id_partner partner_id_folio, 
                    trim(bank.codigo_interno) bankcode, trim(cpag.cuenta) numctapagadora, 
                    scorbank.id_open bank_acc_id, trim(bank.nombre) bankname
            from  cxpgastos g  
                left join acrectas acr on (g.acreedor=acr.acreedor)
                left join fn_scor() scor on (trim(g.acreedor)=replace(trim(scor.c_contpaq),'-',''))
                left join cxcctaspag cpag on (g.banco=cpag.numero)
                left join cxcbancos bank on (cpag.banco=bank.banco)
                left join fn_scor() scorbank on (trim(cpag.ctacon_bco)=replace(trim(scorbank.c_contpaq),'-',''))
                inner join cat_sucursales suc on (g.sucursal = suc.num_suc)            
            where g.folio = %s and g.pagar = '1'
            order by g.folio; """) % foliogasto

        return sql


    def show_entries(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = self.her_entries(cr, uid, ids, context=context)

        # for exp in self.browse(cr, uid, ids, context=context):
        #     for line in exp.advance_ids:
        #         for otherline in self.pool.get('account.move.line').search(cr, uid, [('move_id', '=', line.move_id.id),
        #                                                                                ('id', '!=', line.id)], context=context):
        #             aml = self.pool.get('account.move.line').browse(cr, uid, otherline, context=context)
        #             acc = self.pool.get('account.account').browse(cr, uid, aml.account_id.id, context=context)
        #             if acc.type in ['liquidity', 'bank', 'cash']:
        #                 res[exp.id] += [otherline]

        return {
            'domain': "[('id','in',\
                 [" + ','.join([str(res_id) for res_id in res[ids[0]]]) + "])]",
            'name': _('Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }

    def her_entries(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = {}.fromkeys(ids, [])
        for exp in self.browse(cr, uid, ids, context=context):
            res[exp.id] += exp.account_move_id \
                and [move.id for move in exp.account_move_id.line_id] or []
            res[exp.id] += [line.id for line in exp.advance_ids]
            for line in exp.advance_ids:
                for otherline in self.pool.get('account.move.line').search(cr, uid, [('move_id', '=', line.move_id.id),
                                                                                       ('id', '!=', line.id)], context=context):
                    aml = self.pool.get('account.move.line').browse(cr, uid, otherline, context=context)
                    acc = self.pool.get('account.account').browse(cr, uid, aml.account_id.id, context=context)
                    if acc.type in ['liquidity', 'bank', 'cash']:
                        res[exp.id] += [otherline]
            res[exp.id] += [line2.id for pay in exp.payment_ids
                            for line2 in pay.move_ids]
            for inv in exp.invoice_ids:
                if not inv.move_id:
                    continue
                for move2 in inv.move_id.line_id:
                    res[exp.id] += [move2.id]
        return res

    def action_receipt_create(self, cr, uid, ids, context=None):
        """main function that is called when trying to create the accounting
        entries related to an expense then this super tries to get rid of
        the Journal Entry Lines in zero
        """
#        super(HrExpenseExpense, self).action_receipt_create(
#            cr, uid, ids, context=context)

        move_obj = self.pool.get('account.move')
        for exp in self.browse(cr, uid, ids, context=context):
            if not exp.employee_id.address_home_id:
                raise osv.except_osv(_('Error!'), _('The employee must have a home address.'))
            if not exp.employee_id.address_home_id.property_account_payable.id \
                    and not exp.employee_id.address_home_id.property_account_receivable.id:
                raise osv.except_osv(_('Error!'), _('The employee must have a payable/receivable account set on his home address.'))
            company_currency = exp.company_id.currency_id.id
            diff_currency_p = exp.currency_id.id <> company_currency

            #create the move that will contain the accounting entries
            move_id = move_obj.create(cr, uid, self.account_move_get(cr, uid, exp.id, context=context), context=context)

            #one account.move.line per expense line (+taxes..)
            eml = self.move_line_get(cr, uid, exp.id, context=context)

            #create one more move line, a counterline for the total on payable account
            total, total_currency, eml = self.compute_expense_totals(cr, uid, exp, company_currency, exp.name, eml, context=context)
            if exp.name[:1] == '2':
                acc = exp.employee_id.address_home_id.property_account_payable.id
            else:
                acc = exp.employee_id.address_home_id.property_account_receivable.id
            eml.append({
                    'type': 'dest',
                    'name': exp.name[2:7],
                    'price': total,
                    'account_id': acc,
                    'date_maturity': exp.date_confirm,
                    'amount_currency': diff_currency_p and total_currency or False,
                    'currency_id': diff_currency_p and exp.currency_id.id or False,
                    'ref': exp.name[2:7]
                    })

            #convert eml into an osv-valid format
            lines = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, exp.employee_id.address_home_id, exp.date_confirm, context=context)), eml)
            journal_id = move_obj.browse(cr, uid, move_id, context).journal_id
            # post the journal entry if 'Skip 'Draft' State for Manual Entries' is checked
            if journal_id.entry_posted:
                move_obj.button_validate(cr, uid, [move_id], context)
            move_obj.write(cr, uid, [move_id], {'line_id': lines}, context=context)
            self.write(cr, uid, ids, {'account_move_id': move_id, 'state': 'done'}, context=context)

        aml_obj = self.pool.get('account.move.line')
        res = []
        for exp in self.browse(cr, uid, ids, context=context):
            if not exp.account_move_id.journal_id.entry_posted:
                for aml_brw in exp.account_move_id.line_id:
                    if not aml_brw.debit and not aml_brw.credit:
                        res.append(aml_brw.id)
        if res:
            aml_obj.unlink(cr, uid, res, context=context)
        return True

    def account_move_get(self, cr, uid, expense_id, context=None):
        """This method prepare the creation of the account move related to the
        given expense.

        For this case it will override the date_confirm using date_post

        :param expense_id: Id of voucher for which we are creating
                           account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        """
        context = context or {}
        period_obj = self.pool.get('account.period')
        expense = self.browse(cr, uid, expense_id, context=context)
        date = expense.date_post
        if len(expense.invoice_ids) > 0:
            expense.journal_id = expense.invoice_ids[0].journal_id
        else:
            expense.journal_id = \
                self.pool.get('account.journal').search(cr, uid, [('code', '=', 'GTOND')], context=context)[0]

        res = super(HrExpenseExpense, self).account_move_get(
            cr, uid, expense_id, context=context)
        # res.update({
        #     'date': date,
        #     'period_id': period_obj.find(cr, uid, date, context=context)[0],
        # })
        return res

    def payment_reconcile(self, cr, uid, ids, context=None):
        """ It reconcile the expense advance and expense invoice account move
        lines.
        """
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        per_obj = self.pool.get('account.period')
        for exp in self.browse(cr, uid, ids, context=context):
            self.check_advance_no_empty_condition(cr, uid, exp.id,
                                                  context=context)
            if not exp.account_move_id:
                raise osv.except_osv(
                    _('Warning Data Integrity Failure!!!'),
                    _('Journal Entry for this Expense has been previously '
                      'deleted, please cancel document and go through the '
                      'previous steps up to this current step to recreate it!'
                      ))

            # manage the expense move lines
            tipo_gasto = exp.name[:1]
            if tipo_gasto == '2':
                acc_type = 'payable'
            else:
                acc_type = 'receivable'
            exp_aml_brws = exp.account_move_id and \
                [aml_brw
                 for aml_brw in exp.account_move_id.line_id
                 if aml_brw.account_id.type == acc_type] or []

            advance_aml_brws = [aml_brw
                                for aml_brw in exp.advance_ids
                                if aml_brw.account_id.type == acc_type]

            inv_aml_brws = [aml_brw
                            for inv in exp.invoice_ids
                            for aml_brw in inv.move_id.line_id
                            if aml_brw.account_id.type == 'payable']

            for av_brw in exp.payment_ids:
                advance_aml_brws += \
                    [l for l in av_brw.move_ids
                     if l.account_id.type == acc_type
                     and not l.reconcile_id and not l.reconcile_partial_id]

            aml = {
                'exp':
                exp_aml_brws and [aml_brw.id for aml_brw in exp_aml_brws]
                or [],
                'advances': [aml_brw.id for aml_brw in advance_aml_brws],
                'invs': [aml_brw.id for aml_brw in inv_aml_brws],
                # self.group_aml_inv_ids_by_partner(
                # cr, uid, [aml_brw.id for aml_brw in inv_aml_brws],
                # context=context),
                'debit':
                sum([aml_brw.debit
                     for aml_brw in advance_aml_brws]),
                'credit':
                sum([aml_brw.credit
                     for aml_brw in exp_aml_brws + inv_aml_brws]),
                'exp_sum':
                sum([aml_brw.credit
                     for aml_brw in exp_aml_brws]),
                'inv_sum':
                sum([aml_brw.credit
                     for aml_brw in inv_aml_brws]),
                'invs_ids': [inv.id
                             for inv in exp.invoice_ids]
            }

            aml_amount = aml['debit'] - aml['credit']
            adjust_balance_to = aml_amount == 0.0 and 'liquidate' or \
                (aml_amount > 0.0 and 'debit') or 'credit'
            part_rec, ff, pp = [], [], []
            # create and reconcile invoice move lines
            full_rec = aml['invs'] and self.create_and_reconcile_invoice_lines(
                cr, uid, exp.id, aml['invs'],
                adjust_balance_to=adjust_balance_to, context=context) or []

            # change expense state
            if adjust_balance_to == 'debit':
                ff, pp = self.expense_reconcile_partial_deduction(
                    cr, uid, exp.id, aml, context=context)
                self.write(
                    cr, uid, exp.id,
                    {'state': 'paid'}, context=context)
            elif adjust_balance_to == 'credit':
                ff, pp = self.expense_reconcile_partial_payment(
                    cr, uid, exp.id, aml, context=context)
                self.write(
                    cr, uid, exp.id,
                    {'state': 'process'}, context=context)
            elif adjust_balance_to == 'liquidate':
                ff, pp = self.expense_reconcile_partial_deduction(
                    cr, uid, exp.id, aml, context=context)
                self.write(cr, uid, exp.id, {'state': 'paid'}, context=context)

            date_post = exp.date_post or fields.date.today()

            period_id = per_obj.find(cr, uid, dt=date_post)
            period_id = period_id and period_id[0]
            exp.write({'date_post': date_post})

            if not exp.account_move_id:
                raise osv.except_osv(
                    _('Warning Data Integrity Failure!!!'),
                    _('Journal Entry for this Expense has been previously '
                      'deleted, please cancel document and go through the '
                      'previous steps up to this current step to recreate it!'
                      ))

            x_aml_ids = [aml_brw.id for aml_brw in exp.account_move_id.line_id]

            vals = {'date': date_post, 'period_id': period_id}
            exp.account_move_id.write(vals)
            update_ok = exp.account_move_id.journal_id.update_posted
            if not update_ok:
                exp.account_move_id.journal_id.sudo().write({'update_posted':
                                                             True})
            exp.account_move_id.button_cancel()
            exp.account_move_id.journal_id.sudo().write({'update_posted':
                                                         update_ok})
            aml_obj.write(cr, uid, x_aml_ids, vals)
            for line_pair in full_rec + [ff]:
                if not line_pair:
                    continue
                try:
                    aml_obj.reconcile(
                        cr, uid, line_pair, 'manual', context=context)
                except BaseException:
                    new_line_pair = self.invoice_counter_move_lines(
                        cr, uid, exp.id, am_id=exp.account_move_id.id,
                        aml_ids=line_pair,
                        context=context)
                    for nlp in new_line_pair:
                        aml_obj.reconcile(
                            cr, uid, nlp, 'manual', context=context)
            for line_pair in part_rec + [pp]:
                if not line_pair:
                    continue
                aml_obj.reconcile_partial(
                    cr, uid, line_pair, 'manual', context=context)
        return aml
