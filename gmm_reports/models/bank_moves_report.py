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
from openerp.exceptions import Warning as UserError
from datetime import datetime, timedelta

class bank_moves_report(models.TransientModel):
    _name = 'bank.moves.report'
    _description = 'Reportes de Movimientos Bancarios'

    _defaults = {
        'date_start': lambda *a: dt.date.today().strftime('%Y-%m-%d'),
        'date_end': lambda *a: dt.date.today().strftime('%Y-%m-%d'),
    }

    date_start = fields.Date(
        'Fecha Inicial:',
    )

    date_end = fields.Date(
        'Fecha Final:',
    )

    acc_bank = fields.Many2one(
                'account.account',
                'Cuenta Contable',
                required=True
    )

    ou = fields.Many2one(
        'operating.unit', 'Operating Unit:',
        domain=[('code', 'not ilike', '-')],
    )

    isforbank = fields.Boolean('Es para Conciliación Bancaria?')

    acc_contpaq = fields.Char()

    sinitialbalance = fields.Char()
    sdebit = fields.Char()
    scredit = fields.Char()
    stotdebit = fields.Char()
    stotcredit = fields.Char()
    sfinalbalance = fields.Char()

    movtos = fields.One2many(
        'bank.moves.report.detail',
        'bank_moves_report_id',
        string='Moves')


    @api.multi
    @api.onchange('isforbank')
    def onchange_isforbank(self):
        domain = {'acc_bank': [('type', '!=', 'view')]}

        if self.isforbank:
            domain = {'acc_bank': [('type', '!=', 'view'), ('type', '=', 'liquidity')]}

        return {'domain': domain}


    def _get_cta_contpaq(self):

        """Se crea la conexion al base de datos correspondientes"""
        synccon = self.env['sync.morsa.conexion']
        scor_dbname = 'contpaq_openerp_morsa_' + synccon._get_enterprise_used().lower()
        con = synccon._get_conexion("conexion_openerp.csv", scor_dbname)
        cursor = con.cursor()

        record = ''
        query = "select replace(scor.c_contpaq,'-','') from sync_contpaq_openerp_rel scor where id_open = %s" % self.acc_bank.id
        try:
            cursor.execute(query)
            record = cursor.fetchone()
            con.commit()

        except Exception:
            cursor.rollback()
            raise

        finally:
            cursor.close()
            con.close()

        return record[0] if len(record) > 0 else 'NO IDENTIFICADA'

    def _get_saldo_inicial(self):

        query = """	select aml.date, debit, credit, ap.date_start, ap.date_stop, ap.id 
                    from account_move_line aml inner join account_period ap on (aml.period_id = ap.id)
                    where account_id = %s and period_id in (select id from account_period where special ) 
                    order by aml.date desc;""" % self.acc_bank.id
        try:
            self.env.cr.execute(query)
            res = self.env.cr.dictfetchone()

        except Exception:
            self.env.cr.rollback()
            raise

        datestart = res.get('date_stop') or '2018-01-01' if res else '2018-01-01'
        datestop = (datetime.strptime(self.date_start,"%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")


        query = """select sum(aml.debit) debit,  sum(aml.credit) credit, sum(aml.debit-aml.credit) balance
                    from account_move_line aml inner join account_period ap on (aml.period_id = ap.id)
                    inner join account_move am on (aml.move_id = am.id)
                    where  aml.account_id = %s and aml.date between '%s' and '%s';
                """ % (self.acc_bank.id, datestart, datestop)

        try:
            self.env.cr.execute(query)
            res = self.env.cr.dictfetchone()

        except Exception:
            self.env.cr.rollback()
            raise

        return {
            'debit': res.get('debit') or 0.0,
            'credit': res.get('credit') or 0.0,
            'init_balance': res.get('balance') or 0.0,
                }

    @api.multi
    def execute_report(self):

        self.acc_contpaq = self._get_cta_contpaq()
        sqlwhere = "account_id = %s and aml.date between '%s' and '%s'" % (self.acc_bank.id, self.date_start, self.date_end)

        if self.ou:
            sqlwhere += ' and aml.operating_unit_id = %s' % (self.ou.id)

        if self.isforbank:
            init_balances = {
                'debit':  0.0,
                'credit':  0.0,
                'init_balance': 0.0,
            }
        else:
            init_balances = self._get_saldo_inicial()

        debit = init_balances['debit']
        credit = init_balances['credit']
        initbalance = balance = init_balances['init_balance']

        self.sinitialbalance = '{0:.2f}'.format(balance)
        self.sdebit = '{0:.2f}'.format(debit)
        self.scredit = '{0:.2f}'.format(credit)

        query = """                    
                    --set lc_time to 'es_MX.UTF-8';
                    select to_char(aml.date, 'dd/TMMon/YYYY') fecha, aml.move_id, aml.debit, aml.credit, aa.code, '%s' c_contpaq,
                        ou.name, case when aml.state != 'valid' then 'Descuadrado' else 'Cuadrado' end movtostate,
                        case when am.state = 'posted' then 'Validada' else 'Sin Validar' end polizastate,
                        rp.name partner_name, aml.name move_ref
                    from account_move_line aml inner join account_account aa on (aml.account_id = aa.id)
                                        inner join account_move am on (aml.move_id = am.id)
                                        left join operating_unit ou on (aml.operating_unit_id = ou.id)
                                        left join res_partner rp on (aml.partner_id = rp.id)
                    where %s
                    order by aml.date, aml.id;
                """ % (self.acc_contpaq, sqlwhere)

        try:
            self.env.cr.execute(query)
            registros = self.env.cr.fetchall()
        except Exception:
            self.env.cr.rollback()
            raise

        debit = credit = 0
        movtos = []
        if len(registros) > 0:
            for move in registros:

                balance += (move[2]-move[3])
                debit += move[2]
                credit += move[3]

                rs = {
                    'bank_moves_report_id': self.id,
                    'move_date': move[0],
                    'move_id': move[1],
                    'debit': move[2],
                    'credit': move[3],
                    'code_open': move[4],
                    'code_contpaq': move[5],
                    'ou_name': move[6],
                    'move_state': move[7],
                    'journal_state': move[8],
                    'partner_name': move[9],
                    'move_ref': move[10],
                    'balance': balance,
                    }

                movtos.append(rs)

            self.stotdebit = '{0:.2f}'.format(debit)
            self.stotcredit = '{0:.2f}'.format(credit)
            self.sfinalbalance = '{0:.2f}'.format(balance)
            self.movtos = movtos

            reportdict =  {
                    'type': 'ir.actions.report.xml',
                    'report_name': ('bank' if self.isforbank else 'account') + '.moves.report.aeroo',
                    'datas': {
                        'model': 'bank.moves.report',
                        'id': self.id,
                        'ids': [self.id],
                        'report_type': 'xls'
                    },
                    'nodestroy': True
            }

            return reportdict
        else:
            raise UserError("There are no records.")



#class bank_moves_report

class bank_moves_report_detail(models.TransientModel):

    _name = 'bank.moves.report.detail'

    bank_moves_report_id = fields.Many2one(
        'bank.moves.report', 'Banks Moves Report',
    )

    move_date = fields.Char(
        'Move Date',
    )
    move_id = fields.Integer(
        'Move ID',
    )
    debit = fields.Float()
    credit = fields.Float()
    code_open = fields.Char('ERP Code')
    code_contpaq = fields.Char('Contpaq Code')
    ou_name = fields.Char('OU Name')
    move_state = fields.Char('Move State')
    journal_state = fields.Char('Journal State')
    partner_name = fields.Char('Partner Name')
    move_ref = fields.Char('Entry Reference')
    balance = fields.Float()

# class bank_moves_re   port_detail
