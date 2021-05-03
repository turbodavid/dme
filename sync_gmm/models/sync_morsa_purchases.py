# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 OpenERP s.a. (<http://openerp.com>).
#
#    DME SOLUCIONES
#    David Alberto Pérez Payán <david.perez@pcsystems.mx>
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

import openerp.addons.decimal_precision as dp
from openerp import api, fields, models
import psycopg2
from openerp.tools.translate import _
import logging
import base64
from datetime import datetime
from openerp.addons.web.controllers.main import Session
from openerp.exceptions import Warning as UserError
from decorator import append

_logger = logging.getLogger(__name__)

COMPANY_ID_MOR = 1
ENTERPRISE = {'GMM':'culiacan', 'MOR':'mayoreo', 'VOH':'vohcom', 'desarrollo':'contpaq_morsa_desarrollo'}
JOURNALCODE = {'0': 'CMPNAC', '1': 'CMPNACUS', '2': 'CMPUS'}
TAXCODEPURCHASE = {'16': 53, '8': 69, '0': ''}
TAXCODESALE = {'16': 50, '8': 69, '0': ''}
CURRENCY_ID = {'0': 34, '1': 3}

class sync_morsa_purchases(models.Model):
    _name = 'sync.morsa.purchases'


    def _get_enterprise_used(self):

        sesion = Session()
        informacion = sesion.get_session_info()
        bd = informacion.get('db')

        return bd[0:3]

    enterprise = fields.Char(
            'Enterprise:',
            default=lambda self: self._get_enterprise_used(),
            help='Write the code for enterprise \nGMM: culiacan \nMOR: mayoreo \nVOH: vohcom\n Example: GMM',
                )

    fecha_inicial = fields.Date(
        default = fields.Date.today(),
        required=True,
    )

    fecha_final = fields.Date(
                default = fields.Date.today(),
                required=True,
    )

    procesardevoluciones = fields.Boolean("Procesar Devoluciones", default=False)

    cuenta_inventario = fields.Many2one(
                'account.account',
                    default=1919,
                    required=True
    )

    cuenta_prov_extranjeros = fields.Many2one(
        'account.account',
        default=1995,
        domain=[('code', 'like', '211-1'), ('type', '!=', 'view')],
        required=True
    )


    ou = fields.Many2one(
                'operating.unit', 'Operating Unit:',
                domain=[('code', 'not ilike', '-')],
                default=318,
        )

    conexion = ''
    period = ''
    msgErr = ''

    @api.multi
    @api.onchange('procesardevoluciones')
    def onchange_procesardevoluciones(self):
        self.cuenta_inventario = 1919
        domain = {'cuenta_inventario': [('type', '!=', 'view'), ('code', 'like', '113-1')]}

        if self.procesardevoluciones:
            self.cuenta_inventario = 1922
            domain = {'cuenta_inventario': [('type', '!=', 'view'), ('code', 'like', '113-1')]}

        return {'domain': domain}

    @api.multi
    def action_sync_purchases(self):

        self.period = self.fecha_inicial[5:7] + "/" + self.fecha_inicial[0:4]

        if self.period != self.fecha_final[5:7] + "/" + self.fecha_final[0:4]:
            raise UserError("El rango de fechas debe de estar dentro del mismo periodo:", self.period)

        if self.period in ['12/2018', '12/2017']:
            self._corrige_compras(self.period == '12/2017')
            return

        self.conexion = self.env['sync.morsa.conexion']._get_conexion("conexion_openerp_expense_newportal.csv", ENTERPRISE[self.enterprise])

        #try:
        if self.procesardevoluciones:
            if self._do_devoluciones():
                self.conexion.commit()
            else:
                raise UserError("No existen devoluciones con los datos proporcionados")
        else:
            if self.period[-4:] != '2016':
                self._do_purchases()
                self.conexion.commit()
            else:
                self._delete_purchases(self.period == '11/2016')
                self.conexion.commit()
        #except Exception as e:
        #    raise
        #finally:
        self.conexion.close()

        return

    def _do_purchases(self):

        domain = [
            ('code', '=', self.period),
            ('company_id', '=', COMPANY_ID_MOR)
            ]

        period_id = self.env['account.period'].search(domain)
        obj_invoice = self.env['account.invoice']
        obj_invoice_line = self.env['account.invoice.line']
        acc_journal = self.env['account.journal']
        res_partner = self.env['res.partner']
        attachment = self.env['ir.attachment']
        obj_ir_attachment_facturae = self.env['ir.attachment.facturae.mx']
        obj_sales_log = self.env['sync.sales.log']
        msgErr = ''

        crspurchase = self.conexion.cursor()
        crspurchase.execute(self._get_sql_purchases())
        purchases = crspurchase.fetchall()
        query_update = ''

        if crspurchase.rowcount == 0:
            raise UserError("There are not Purchases with the given parameters")

        # num_suc           0
        # num_prov          1
        # nom_prov          2
        # importacion       3
        # mon_prov          4
        # serie             5
        # foliofact         6
        # fecha             7
        # entrada           8
        # foliofiscal       9
        # subtotal          10
        # subtoalnum        11
        # iva               12
        # importe           13
        # ivacalc1          14
        # ivcalc2           15
        # tc                16
        # xmlfile           17
        # partner_id        18
        # vencimiento       19
        # concepto          20
	    # id_partner	    21

        rfc = ''
        supplier_invoice = ''
        uuid = ''
        haserror = False
        sales_log = {}

        for purchase in purchases:

            if haserror:
                try:
                    obj_sales_log.create(sales_log)
                except:
                    pass

            msgdocto = ''
            haserror = False
            try:

                sales_log = {
                    'tipo': 'Compra',
                    'operating_unit': self.ou.name,
                    'message': '',
                    'ip_addres': self.ou.ip_address,
                    'data_base': self.ou.data_base,
                }

                if purchase[3] == 'S':
                    if purchase[21]:
                        partnerid = purchase[21]
                    else:
                        break
                else:
                    partnerid = purchase[18]

                #partnerid = purchase[18] if purchase[3] == 'N' else purchase[21]
                opartner = res_partner.search([('id', '=', partnerid)])
                rfc = opartner.vat[2:]

                currencyrate = 1
                """LOGICA PARA SELECCIONAR LA CUENTA CORRECTA EN EL ENCABEZADO Y DETALLADO DE LA FACTURA"""
                ai_acc = opartner.property_account_payable.id
                ail_acc = self.cuenta_inventario.id
                if purchase[4] == '1':
                    ai_acc = self.cuenta_prov_extranjeros.id
                    currencyrate = purchase[16]
                    if purchase[17]:
                        currencyrate = obj_ir_attachment_facturae.parse_data(purchase[17], "TipoCambio")

                date_invoice = purchase[8]
                date_due = purchase[19]
                supplier_invoice = purchase[5] + '-' + str(purchase[6]) if purchase[5] else str(purchase[6])

                uuid = purchase[9] if purchase[9] else ''
                msgdocto  = 'RFC: %s. Factura: %s. UUID: %s. ' % (rfc, supplier_invoice, uuid)
                print "*** %s *****" % msgdocto

                # ENCABEZADO DE LA FACTURA
                invoice_header = {
                    'partner_id'                : partnerid,
                    'account_id'                : ai_acc,
                    'journal_id'                : self._get_journal(purchase[3],purchase[4]),
                    'operating_unit_id'         : self.ou.id,
                    'type'                      : 'in_invoice',
                    'origin'                    : supplier_invoice + '-' + str(purchase[1]),
                    'supplier_invoice_number'   : supplier_invoice,
                    'date_invoice'              : date_invoice,
                    'date_due'                  : date_due,
                    'currency_id'               : CURRENCY_ID[purchase[4]],
                    'currency_rate'             : currencyrate or 1,
                    'comment'                   : purchase[20] + ". Fecha Factura: %s" % purchase[7],
                    'period_id'                 : period_id.id or 165,
                }
                #SE CREA LA FACTURA Y AGREGO EL UPDATE AL CXPFACTURAS
                invoice = obj_invoice.create(invoice_header)
                print "Procesando factura: %s, registrada en %s" % (supplier_invoice + '-' + str(purchase[1]), invoice.id)

                """LOGICA PARA CREAR EL ATTACHMENT CON EL XML DE LA FACTURA"""
                if purchase[17]:
                    xml = purchase[17]
                    xml_file = xml #self._checking_characters(xml)
                    invoice_attachment = {
                        'name'      : rfc + '_' + supplier_invoice + '.xml',
                        'type'      : 'binary',
                        'datas'     : xml_file.encode('base64'),
                        'res_model' : 'account.invoice',
                        'res_id'    : invoice.id,
                    }
                    try:
                        attch = attachment.create(invoice_attachment)
                    except Exception as e:
                        msgdocto += 'En: Enlazando archivo XML). \n' + repr(e)
                        sales_log.update({'message': msgdocto})
                        haserror = True
                        pass

                    """LOGICA PARA ASIGNAR EL UUID A LA FACTURA CREADA EL UUID SE SACA DEL REGISTRO DONDE SE CREA EL ATTACHMENT"""
                #print '*** PASE EL ATTCHMENT ****', attch.id
                if uuid and not haserror:
                    attachment_facturae = {
                        'name'              : rfc + '_' + supplier_invoice,
                        'rfc_emisor': rfc,
                        'uuid'              : uuid,
                        'state'             : 'done',
                        'company_id'        : 1,
                        'cfdi_type'         : 'outgoing',
                        'file_xml_sign'     : attch.id,
                        'type_attachment'   : 'account.invoice',
                        'res_id'            : invoice.id,
                    }
                    try:
                        attch = ''
                        attch = obj_ir_attachment_facturae.create(attachment_facturae)
                        if attch:
                            invoice.write({'cfdi_id': attch.id})
                    except Exception as e:
                        pass
                        msgdocto += 'En: Asignando UUID. \n' + repr(e)
                        sales_log.update({'message': msgdocto})
                        haserror = True
                        pass

                """LINEAS DE LA FACTURA"""
                if not haserror:
                    invoice_line = {
                        'name': self.ou.code + '|COMPRA DE MERCANCIA',
                        'account_id': ail_acc,
                        'quantity': 1,
                        'price_unit': purchase[13] - purchase[15],
                        'uos_id': 1,
                        'invoice_line_tax_id': [
                            (6, 0, [TAXCODEPURCHASE[str(int(purchase[12]))]]),
                        ] if purchase[12] > 0 else '',
                        'invoice_id': invoice.id,
                    }
                    # SE CREAN LAS LINEAS DE LA FACTURA
                    try:
                        obj_invoice_line.create(invoice_line)
                        """SE ACTUALIZA LA LINEA DE IMPUESTOS PARA DESPUES ASIGNARLE DE MANERA MANUAL EL IMPORTE CORRECTO DEL IMPUESTO"""
                        invoice.button_reset_taxes()
                        invoice_tax = self.env['account.invoice.tax'].search([('invoice_id', '=', invoice.id)])
                        update_amount = {
                            'amount': purchase[15],
                        }
                        invoice_tax.update(update_amount)

                        query_update += "UPDATE cxpfacturas SET invoice_id = %s, erp = '1' " \
                                        "WHERE foliofact = %s and serie = '%s' and num_prov = %s;" \
                                                 % (invoice.id, purchase[6], purchase[5], purchase[1])
                        #print '*** INSERTE EL DETALLE **'
                        if purchase[4] == '0':
                            """SE VALIDA LA FACTURA CUANDO LA MONEDA ES 0 (MN)"""
                            invoice.invoice_open()
                    except Exception as e:
                        msgdocto += 'En: Creando el detalle. \n' + repr(e)
                        sales_log.update({'message': msgdocto})
                        haserror = True
                        pass
            except Exception as e:
                msgdocto += 'En: Creando Encabezado de Factura. \n' + repr(e)
                sales_log.update({'message': msgdocto})
                haserror = True
                pass

        if query_update:
            crspurchase.execute(query_update)

        return

    def _get_journal(self, importado, moneda, purchase=True, fiscal=True):

        if purchase:
            journalcode = JOURNALCODE[moneda if importado == 'N' else '2']
        else:
            journalcode = 'NCDEVCMP' if fiscal else 'NCDEVCMPNF'

        journal = self.env['account.journal'].search([('code', '=', journalcode)])
        idjournal = journal.id

        return idjournal

    def _get_sql_purchases(self):


        sql = """select f.num_suc, f.num_prov, p.nom_prov, importacion, mon_prov, trim(f.serie) serie,
                        foliofact, date(fec_fact::text) as fecha, date(fec_venc2::text) as entrada, 
                        foliofiscal, c.subtotal, c.subtotal/100::decimal, f.iva, f.importe, 
                        coalesce( f.importe - (c.subtotal::decimal/100), 0 ) ivacalc1, 
                        f.importe - round(f.importe/(1+(f.iva/100)),2) ivcalc2,
                        case when mon_prov='1' then t.tc_dolar else 1 end as tc, 
	                    regexp_replace(c.xml, '[^\x20-\x7f\x0d\x1b]', ' ', 'g') xmlfile,
	                    rfcs.id partner_id, date(fec_venc::text) vencimiento, trim(f.concepto) concepto,
			            scor.id_partner
                from cxpfacturas f 	inner join cxpproveedores p on (f.num_prov=p.num_prov) 
	                left join swpr_cfdcomprobanteproveedor c on (trim(replace(p.rfc,'-','')) = trim(c.emirfc) 
	                	and foliofact=c.folio and f.serie=c.serie) 
	                left join cxptipocambio t on (date(f.fec_fact::text) = t.fecha and t.estatus = 'A') 
	                left join openerp_get_rfcs() rfcs on (rfcs.rfc_sat=c.emirfc)
			left join fn_scor() scor on (p.cta_prov=replace(scor.c_contpaq,'-',''))
                where f.invoice_id = 0 and importacion = 'N' and f.num_suc = %s and date(f.fec_venc2::text) between '%s' and '%s'
                order by f.fec_venc2, f.num_prov;"""\
                                %(int(self.ou.code),self.fecha_inicial,self.fecha_final)

        return sql

    def _checking_characters(self, cadena=None):
        nueva_cadena = ''
        if cadena > '':
            for l in cadena:
                x = l
                if x == u'Ã':
                    x = 'e'
                elif x == u'©':
                    x = 'i'
                elif x == u'\xad':
                    x = ''
                elif x == u'­-':
                    x = ''
                elif x == u'\x91':
                    x = ''
                elif x == u'\x93':
                    x = ''
                elif x == u'\x9a':
                    x = ''
                elif x == u'\x9c':
                    x = ''
                nueva_cadena = nueva_cadena + x
                #print"TTTTTTTTTTTTTTTT", nueva_cadena
        if nueva_cadena == '':
            nueva_cadena = str(cadena)
        return nueva_cadena

    def _corrige_compras(self, borraPolizas=False):

        obj_purchase = self.env['account.invoice']
        purchases = obj_purchase.search([('type', '=', 'in_invoice'),
                                         ('journal_id', 'in', [112, 164]),
                                         ('state', 'in', ['draft', 'open']),
                                         ('partner_id', '=', 7509),
                                         ('amount_tax', '<', 0),
                                         ])
        obj_am = self.env['account.move']

        contador = 0
        for purchase in purchases:
            amount_line = purchase.amount_total / 1.16
            if not abs(amount_line - purchase.original_amount) > 0.20:
                continue

            contador += 1
            #  if borraPolizas:
            #       am = obj_am.search([('id', '=', purchase.move_id.id)])
            #      purchase.move_id.button_cancel()
            # print  "Cancelando poliza compra: %s. Canceladas: %s", purchase.number, contador
            # else:
            isopen = purchase.state == 'open'
            ail = self.env['account.invoice.line'].search([('invoice_id', '=', purchase.id)])
            ail.write({'price_unit': amount_line})
            if isopen:
                moveid = purchase.move_id
                moveid.button_cancel()
                moveid.write({'state': 'draft'})
                purchase.invoice_cancel()
                purchase.action_cancel_draft()
                purchase.button_compute()
                purchase.invoice_open()
            else:
                purchase.button_compute()

            #print "Corrigiendo Compra: %s. Corregidas: %s"%(purchase.number, contador)
        return

    def _delete_purchases(self, borraPolizas=False):

        obj_invoice = self.env['account.invoice']
        obj_invoice_line = self.env['account.invoice.line']
        res_partner = self.env['res.partner']
        attachment = self.env['ir.attachment']
        obj_ir_attachment_facturae = self.env['ir.attachment.facturae.mx']
        msgErr = ''


        sql = "SELECT foliofact, trim(serie) serie, num_prov, fec_fact, fec_venc2, invoice_id FROM cxpfacturas "\
               " WHERE fec_venc2 >= 20190101 and fec_fact < 20190101 and invoice_id < 0"

        crspurchase = self.conexion.cursor()
        crspurchase.execute(sql)
        purchases = crspurchase.fetchall()
        query_update = ''

        if crspurchase.rowcount == 0:
            raise UserError("There are not Purchases to delete")

        # foliofact         0
        # serie             1
        # num_prov          2
        # fecha             3
        # entrada           4
        # invoice_id        5

        supplier_invoice = ''
        for purchase in purchases:

            msgdocto = ''
            haserror = False
            try:

                supplier_invoice = purchase[1] + '-' + str(purchase[0]) if purchase[1] else str(purchase[0])
                origin = supplier_invoice + '-' + str(purchase[2])
                #invoice = obj_invoice.search([('id', '=', purchase[5])])
                #if not invoice:
                invoice = obj_invoice.search([('origin', '=', origin)])

                if not invoice or invoice.origin != origin:
                    continue

                if borraPolizas:
                    invoice.move_id.button_cancel()
                else:
                    #query_update = 'update cxpfacturas set invoice_id = 0 where invoice_id = %s' % invoice.id
                    invoice.invoice_cancel()
                    #invoice.action_cancel_draft()
                    invoice.write({'number': '', 'internal_number': ''})
                    # ir = attachment.search([('res_id', '=', invoice.id), ('res_model', '=', 'account.invoice')])
                    # if ir:
                    #     ir.unlink()
                    # ir_facte = obj_ir_attachment_facturae.search([('id', '=', invoice.cfdi_id)])
                    # if ir_facte:
                    #     ir_facte.unlik()
                    # invoice.unlik()
                    #crspurchase.execute(query_update)
            except Exception as e:
                raise e
        return

    def _do_devoluciones(self):

        domain = [
                ('code', '=', self.period),
                ('company_id', '=', COMPANY_ID_MOR)
            ]

        refunds_obj = self.env['sync.morsa.refunds']
        crsdev = self.conexion.cursor()
        sql = ''
        msgErr = ''
        lreturn = False


        try:
            try:
                refunds_obj.create_table_erpid(self.ou)
            except Exception as err:
                pass

            crsdev.execute(self._get_sql_refunds(False))
            devrecords = crsdev.fetchall()
        except Exception:
            crsdev.rollback()
            raise

        if crsdev.rowcount == 0:
            lreturn = refunds_obj.create_refunds(invoicetype='in_invoice',
                                  order='partner_id_internal, refund_uuid',
                                  operating_unit_id=self.ou.id
                                   )
            return lreturn
            #raise UserError("There are not Refund within the given parameters")

        purchase_id = self.id
        refundssuc = {}
        resid = {}


        for refund in devrecords:
            # creo un diccionario para buscar los folios fiscales en la sucursal cuando sean devoluciones
            if refund[13] in (630, 730):
                continue
            ou_code = str(refund[4]).zfill(2)
            keyrefund = str(refund[8])
            refundssuc.setdefault(ou_code, []).append(keyrefund)
            keyrefund = ou_code + keyrefund
            resid.setdefault(keyrefund, []).append([0, refund[0], '', '', '', '', '', refund[13]])

        try:
            resid = self._look_for_refund_cfdi(refundssuc, resid)
        except Exception as err:
            raise UserError(repr(err))

        sql = ''
        for refund in devrecords:

            msgdocto = ''
            haserror = False
            try:

                # if num_suc != refund[4]:
                #     num_suc = refund[4]
                #     ou_obj = ou_obj.search([('code', '=', str(num_suc).zfill(2))])
                partnerid = ''
                if not refund[1]:
                    partnerid = self.env['res.partner'].search([('vat', '=', 'MX'+refund[2].strip())])

                esfaltante = refund[13] in (630, 730)
                ou_code = str(refund[4]).zfill(2)
                dictrefund = {
                    'sync_morsa_purchases_id': purchase_id,
                    'invoice_type': 'in_invoice',
                    'partner_id_internal': refund[0],
                    'partner_vat': refund[2],
                    'partner_id': refund[1] if refund[1] else partnerid.id,
                    'state': 'draft',
                    'invoice_id': refund[3] if refund[3] > 0 else '',
                    'invoice_uuid': refund[11],
                    'date_refund': refund[5],
                    'amount_untaxed': refund[15],
                    'amount_total': refund[14],
                    'amount_taxes': refund[14] - refund[15],
                    'refund_ref': refund[8],
                    'invoice_number': refund[9],
                    'invoice_number_serie': refund[10],
                    'id_kardex': refund[12],
                    'num_mov':  refund[13],
                    'currency_id': CURRENCY_ID[refund[16]],
                    'currency_rate': refund[18] if refund[16] == '1' and refund[18] else 1.0,
                    'refund_number': '',
                    'refund_number_serie': '',
                    'refund_uuid': '',
                    'xmlfile': '',
                    'comment': '',
                    'operating_unit_id': '',
                }
                if esfaltante:
                    ou = self.env['operating.unit'].search([('code', '=', ou_code)])
                    dictrefund['operating_unit_id'] = ou.id
                else:
                    res = resid.get(ou_code + str(refund[8]) or [])
                    dictrefund.update(
                        {'refund_number': res[0][5],
                         'refund_number_serie': res[0][4],
                         'refund_uuid': res[0][2],
                         'xmlfile': res[0][6],
                         'comment': res[0][3],
                         'operating_unit_id': res[0][0],
                        })

                #print "procesando : ", res

                # SE CREA LA INFORMACIÓN DE LA DEVOLUCION
                refunds_obj = refunds_obj.create(dictrefund)
                sql += "insert into erpid values (%s, %s, 'cxpkardex', 'sync_morsa_refunds'); " % (refund[12], refunds_obj.id)

                lreturn = True
            except Exception as err:
                raise UserError(repr(err))

        refunds_obj.create_refunds(invoicetype='in_invoice',
                                  order='partner_id_internal, refund_uuid',
                                  operating_unit_id=self.ou.id
                                   )

        if sql:
            crsdev.execute(sql)

        return lreturn

    def _look_for_refund_cfdi(self, resrefunds, resid ):

        ou_obj = self.env['operating.unit']
        con_branch = self.env['sync.morsa.conexion']
        cursor_hq = self.conexion.cursor()
        sql = ''
        sql_hq = ''
        conexion = ''
        for ou_code in resrefunds.keys():
            ou_obj = ou_obj.search([('code', '=', ou_code)])
            if ou_obj:
                try:
                    refunds = resrefunds[ou_code]
                    #print "creando la información en la  sucursal :", ou_code
                    for v in refunds:
                        res = resid.get(ou_code + str(v) or [])
                        res[0][0] = ou_obj.id
                        resid.update({ou_code + str(v): res})

                    if ou_code == '01':
                        cursor = self.conexion.cursor()
                    else:
                        conexion = con_branch._get_conexion_direct(ou_obj.ip_address, ou_obj.data_base)
                        cursor = conexion.cursor()

                    sql = 'select folio, num_prov, trim(comentario1) comment1, trim(comentario2) comment2, trim(folio_fiscal) uuid ' \
                          'from cxpdevoluciones where folio in (%s);' % ','.join(map(str, refunds))

                    try:
                        cursor.execute(sql)
                        records = cursor.fetchall()
                        for record in records:
                            res = resid.get(ou_code + str(record[0]) or [])
                            if res[0][1] == record[1]:
                                res[0][2] = record[4] #igualo el UUID
                                res[0][3] = (record[2] + " " + record[3]).strip() #los comentarios de la devolucion

                                #ahora voy y busco la nota de credito en el swpr_comprobanesproveedor del corporativo
                                if record[4]:
                                    sql_hq = "select trim(serie), folio, regexp_replace(xml, '[^\x20-\x7f\x0d\x1b]', ' ', 'g') xmlfile " \
                                             "from swpr_cfdcomprobanteproveedor cfdi  where foliofiscal = '%s'; " % record[4]

                                    cursor_hq.execute(sql_hq)
                                    cfdi = cursor_hq.fetchone()
                                    if cfdi:
                                        res[0][4] = cfdi[0]
                                        res[0][5] = cfdi[1]
                                        res[0][6] = cfdi[2] #self._checking_characters(cfdi[2])

                            resid.update({ou_code + str(record[0]): res})
                    except Exception:
                        cursor.rollback()
                except Exception as err:
                    raise UserError(repr(err))
                    #graba en el log
                finally:
                    if ou_code != '01' and conexion:
                        conexion.close()

        cursor_hq.close()
        return resid

    def _get_sql_refunds(self, forUUID=False):
        """
        num_prov    0
        partner_id  1
        rfc	        2
        invoice_id	3
        sucdev	    4
        fecdev	    5
        uuidnc	    6
        serienc	    7
        referencia	8
        factdev	    9
        seriedev	10
        uuidfact	11
        id_cxpkar   12
        num_mov     13
        devolucion	14
        devsiniva   15
        mon_prov    16
        importacion 17
        tc_dolar    18
        """
        where = """
            where abs(total/100::numeric - coalesce(k.importe, 0)) < 1 and 
                k.num_mov in (620,630,720,730) and to_date( k.fec_fact::text, 'YYYYMMDD' ) between '%s' and '%s' 
                and id_cxpkar not in (select id from erpid where tabla = 'cxpkardex') """ \
                % (self.fecha_inicial, self.fecha_final)
        if self.ou:
            where += " and k.num_suc = %s " % int(self.ou.code)

        if forUUID:
            #numsuc         0
            #num_prov       1
            #fec_fact       2
            #referencia     3
            #id_cxpkar      4
            #folio_fsical   5
            sql = "select num_suc, num_prov, fec_fact, referencia, id_cxpkar, k.num_mov folio_fiscal from cxpkardex k " \
                  + where + \
                  "order by k.num_suc, k.fec_fact, k.num_prov, k.serie, k.foliofact;"
        else:
            sql = """
                select k.num_prov, rfcs.id partner_id, replace(trim(p.rfc),'-','') rfc, f.invoice_id, k.num_suc sucdev, 
                        to_date( k.fec_fact::text, 'YYYYMMDD' ) fecdev, k.folio_fiscal uuidnc, '' serienc, k.referencia, 
                        k.foliofact factdev, trim(k.serie) seriedev,
                        trim(s.foliofiscal) uuidfact, k.id_cxpkar, k.num_mov,
                        coalesce( k.importe, 0 ) devolucion,
                        round( coalesce( k.importe / (1+(k.iva/100)), 0 ), 2) devsiniva,
                        p.mon_prov, p.importacion, tc.tc_dolar
                from cxpkardex k left join cxpproveedores p on (k.num_prov = p.num_prov)
                    left join swpr_cfdcomprobanteproveedor s on (k.referencia = s.folio_carta  and k.num_suc = s.sucursal_carta and replace(trim(p.rfc),'-','') = trim(s.emirfc))
                    left join cxpfacturas f on (k.serie = f.serie and k.foliofact=f.foliofact and k.num_prov = f.num_prov)
                    left join openerp_get_rfcs() rfcs on (rfcs.rfc_sat = coalesce(s.emirfc, replace(trim(p.rfc),'-','')))
                    left join cxptipocambio tc on (tc.fecha = to_date( k.fec_fact::text, 'YYYYMMDD' ) and tc.estatus = 'A') %s
                order by k.num_prov, k.num_suc, k.fec_fact, k.foliofact;""" % where

        return sql


# class sync_morsa_refunds(models.Model):
#     _name = 'sync.morsa.refunds'
#
#     sync_morsa_purchases_id = fields.Many2one(
#             'sync.morsa.purchases', 'Sync Purchase ID',
#             ondelete='cascade', index=True,
#         )
#
#     sync_morsa_incomes_id = fields.Many2one(
#         'sync.morsa.incomes', 'Sync Income ID',
#         ondelete='cascade', index=True,
#     )
#
#     invoice_type = fields.Selection([
#             ('out_invoice', 'Customer Invoice'),
#             ('in_invoice', 'Supplier Invoice'),
#             ('in_payment', 'Customer Payment'),
#             ('out_payment', 'Supplier Payment'),
#             ], 'Type'
#         )
#
#     partner_id_internal = fields.Integer('Partner ID Internal')
#     partner_id_internal_socio = fields.Integer('Partner ID with an associate')
#     partner_vat = fields.Char(size=20, string="RFC")
#     partner_id = fields.Many2one('res.partner', 'Partner')
#     operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')
#     state = fields.Selection([
#             ('draft', 'Draft'),
#             ('open', 'Open'),
#             ('paid', 'Paid'),
#             ('cancel', 'Cancelled'),
#             ('posted', 'Posted'),
#             ], 'Status'
#         )
#
#     invoice_id = fields.Integer()
#     refund_id = fields.Integer()
#     invoice_uuid = fields.Char('Invoice UUID')
#     refund_uuid = fields.Char('Refund UUID')
#     date_refund = fields.Date('Refund Date')
#
#     amount_untaxed = fields.Float(digits_compute=dp.get_precision('Account'), string='SubTotal')
#     amount_total = fields.Float(digits_compute=dp.get_precision('Account'), string='Total')
#     amount_taxes = fields.Float(digits_compute=dp.get_precision('Account'), string='Impuestos')
#
#     refund_ref = fields.Integer('Internal Refund ID, for refund details')
#     invoice_number = fields.Char('Supplier Invoice Number', size=64)
#     invoice_number_serie = fields.Char('Supplier Invoice Number prefix', size=20)
#     refund_number = fields.Char('Supplier Refund Number', size=64)
#     refund_number_serie = fields.Char('Supplier Refund Number prefix', size=20)
#     num_mov = fields.Integer('Tipo de Movimiento')
#     id_kardex = fields.Integer('ID en el Origen')
#     xmlfile = fields.Text()
#     comment = fields.Text('Notes')
#     acc_relative_partner_id = fields.Many2one('account.account', 'Cuenta Contable')
#     currency_id = fields.Many2one('res.currency', default=34)
#     currency_rate = fields.Float(digits_compute=dp.get_precision('Currency Rate'), default=1.0)
#     voucher_id = fields.Many2one('account.voucher', 'ID Pago')
#
#     serie_invoice_number = fields.Char(compute='_get_invoice_number', string='Número de Factura')
#     serie_refund_number = fields.Char(compute='_get_refund_number', string='Número de NC/Pago')
#
#     @api.depends('invoice_number')
#     def _get_invoice_number(self):
#         serie = ''
#         invnumber = ''
#         for rec in self:
#             serie = rec.invoice_number_serie
#             serie = (serie.strip() + '-') if serie else ''
#             invnumber = rec.invoice_number if rec.invoice_number else ''
#             rec.serie_invoice_number = serie + invnumber
#
#         return
#
#     @api.depends('refund_number')
#     def _get_refund_number(self):
#
#         serie = ''
#         refnumber = ''
#         for rec in self:
#             serie = rec.refund_number_serie
#             serie = (serie.strip() + '-') if serie else ''
#             refnumber = rec.refund_number if rec.refund_number else ''
#             rec.serie_refund_number = serie + refnumber
#
#         return
#
#     def _get_refund_journal(self, refund, acc_id, fiscal=True):
#
#         ou_name = refund.operating_unit_id.name
#         journaltype = refund.invoice_type
#         serie = refund.refund_number_serie
#         tipomov = refund.num_mov
#         journalcode = ''
#
#         if journaltype == 'in_invoice':
#             purchasecode = 'CMP'
#             currencyid = ''
#             cmsgadi = ''
#             if refund.currency_id.id == CURRENCY_ID['1']:
#                 purchasecode = 'CUS'
#                 acc_id = ''
#                 currencyid = CURRENCY_ID['1']
#                 cmsgadi = 'US '
#
#             if tipomov in (620, 720):
#                 ccode = 'DEV'
#                 cmsg = cmsgadi + 'Devoluciones'
#             else:
#                 ccode = 'FAL'
#                 cmsg = cmsgadi + 'Faltantes'
#             journalcode = 'NC' + ccode + purchasecode + ('' if fiscal else 'NF')
#             datos = {
#                 'name': 'Notas Credito ' + cmsg + ('' if fiscal else '(NO Fiscal)'),
#                 'code': journalcode,
#                 'type': 'purchase_refund',
#                 'analytic_journal_id': self.env['account.analytic.journal'].search([('code', '=', 'purchase')]).id,
#                 'default_debit_account_id': acc_id,
#                 'default_credit_account_id': acc_id,
#                 'active': True,
#                 'update_posted': True,
#                 'currency': currencyid,
#             }
#         else:
#             if fiscal:
#                 if not serie:
#                     serie = ''
#                 if len(serie) >= 7:
#                     journalcode = 'NC'
#                 else:
#                     journalcode = 'NCVT'
#                 journalcode += serie
#             else:
#                 journalcode = 'NCVTANF'
#
#             datos = {
#                 'name': 'Nota Credito Ventas ' + ( '' if fiscal else 'No Fiscal ' ) + \
#                         ou_name + ' ' + (serie if serie else ''),
#                 'code': journalcode,
#                 'type': 'sale_refund',
#                 'analytic_journal_id': self.env['account.analytic.journal'].search([('code', '=', 'sale')]).id,
#                 'default_debit_account_id': acc_id,
#                 'default_credit_account_id': acc_id,
#                 'active': True,
#                 'update_posted': True,
#                 }
#
#         journal = self.env['account.journal'].search([('code', '=', journalcode)])
#         if not journal:
#             journal = journal.create(datos)
#
#         return journal.id
#
#     ##process refunds that are not processed yet
#     def create_refunds(self, invoicetype='in_invoice',
#                        order='partner_id_internal, refund_uuid',
#                        operating_unit_id=None
#                        ):
#
#         if invoicetype == 'in_invoice':
#             domain = [('state', '=', 'draft'),
#                       ('invoice_type', '=', invoicetype)]
#         else:
#             domain = [('state', '=', 'draft'), ('num_mov', '>=', 610),
#                       ('invoice_type', '=', invoicetype),
#                     ]
#
#         if operating_unit_id:
#             domain.append(('operating_unit_id', '=', operating_unit_id))
#
#         refunds_to_create = self.search(domain, order=order)
#
#         if len(refunds_to_create) == 0:
#             return
#
#         invoice = ''
#         invoice_line = self.env['account.invoice.line']
#         obj_sales_log = self.env['sync.sales.log']
#         ir_fe = self.env['ir.attachment.facturae.mx']
#         uuid = ''
#         partner = ''
#         acc_line_id = ''
#         acc_relative_partner = ''
#         sql = False
#         wronginvoice = ''
#         errormsg = ''
#         tipodoctomsg = ''
#         taxid = ''
#         refundref = 0
#         cpartnerlabel = ''
#         uuidexists = {}
#
#         for refund in refunds_to_create:
#
#             if wronginvoice and refund.refund_uuid.strip() and wronginvoice == refund.refund_uuid.strip():
#                 continue
#
#             if refund.refund_uuid in uuidexists.keys():
#                 continue
#
#             #print "Generando: ", refund.refund_ref, refund.refund_uuid, refund.partner_id_internal
#             if partner != refund.partner_id_internal or \
#                 ((not refund.refund_uuid or refund.refund_uuid.strip() == '') and refund.refund_ref != refundref) \
#                     or (refund.refund_uuid and uuid != refund.refund_uuid.strip()):
#
#                 sql = True
#                 acc_relative_partner = ''
#                 wronginvoice = ''
#                 taxcode = str(int(round((refund.amount_taxes / refund.amount_untaxed) * 100, 0)))
#                 if taxcode not in ['16', '8', '0']:
#                     taxcode = '16'
#                 if invoicetype == 'in_invoice':
#                     cpartnerlabel = 'Proveedor'
#                     acc_line_id = refund.sync_morsa_purchases_id.cuenta_inventario.id
#                     tipodoctomsg = 'Nota Credito Compras'
#                     taxid = TAXCODEPURCHASE[taxcode]
#                 else:
#                     cpartnerlabel = 'Cliente'
#                     acc_relative_partner = refund.acc_relative_partner_id.id
#                     tipodoctomsg = 'Nota Credito Ventas'
#                     taxid = TAXCODESALE[taxcode]
#                     if refund.num_mov in [620, 720]:
#                         acc_line_id = refund.sync_morsa_incomes_id.acc_refund_id.id
#                     else:
#                         acc_line_id = refund.sync_morsa_incomes_id.acc_benefit_id.id
#
#                 if partner and invoice:
#                     invoice.button_reset_taxes()
#                     invoice.invoice_open()
#
#                 partner = refund.partner_id_internal
#                 uuid = refund.refund_uuid.strip() if refund.refund_uuid else ''
#                 refundref = refund.refund_ref
#                 try:
#                     ir_fe = ir_fe.search([('uuid', '=', uuid)])
#                     if uuid and ir_fe:
#                         values = [ir_fe.res_id, refund.partner_id_internal]
#                         uuidexists.setdefault(uuid, ir_fe.res_id)
#                         continue
#                     invoice, wronginvoice = self._create_refund_header(refund, acc_line_id)
#                     errormsg = wronginvoice
#                 except Exception as err:
#                     wronginvoice = uuid or 'ERROR'
#                     errormsg = err.message + "\n" + \
#                                "UUID: %s. Factura: %s. %s: %s. Nota Credito: %s " \
#                                % (uuid, refund.invoice_number_serie+refund.invoice_number,
#                                   cpartnerlabel, refund.partner_id_internal, refund.refund_ref)
#                     raise
#
#                 if wronginvoice:
#                     sales_log = {
#                         'tipo': tipodoctomsg,
#                         'operating_unit': refund.operating_unit_id.name,
#                         'message': errormsg,
#                         'ip_addres': refund.operating_unit_id.ip_address,
#                         'data_base': refund.operating_unit_id.data_base,
#                     }
#                     obj_sales_log.create(sales_log)
#                     if wronginvoice == 'ERROR':
#                         wronginvoice = ''
#                         continue
#
#             """LINEAS DE LA NOTA DE CREDITO"""
#             ref_to_record = refund.invoice_uuid.strip() if refund.invoice_uuid else ''
#             ref_to_record += "[" + refund.invoice_number_serie.strip() + \
#                              ("-" if refund.invoice_number_serie else '') + refund.invoice_number + "]"
#             datos = {
#                 'name': invoice.operating_unit_id.code + '|' + ref_to_record,
#                 'account_id': acc_line_id,
#                 'quantity': 1,
#                 'price_unit': refund.amount_untaxed,
#                 'uos_id': 1,
#                 'company_id': 1,
#                 'invoice_line_tax_id': [(6, 0, [taxid]),] if taxid else '',
#                 'invoice_id': invoice.id,
#             }
#             # SE CREAN LAS LINEAS DE LA FACTURA
#             invoice_line = invoice_line.create(datos)
#             refund.write({'refund_id': invoice.id, 'state': 'open'})
#
#         else:
#             if invoice:
#                 invoice.button_reset_taxes()
#                 invoice.invoice_open()
#
#         if invoicetype  == 'in_invoice':
#             return sql
#
#         #rectifica las ya validadas
#         #k = uuid
#         #v = [invoice_id, partner_internal]
#         av = self.env['account.voucher']
#         invoice = self.env['account.invoice']
#         for k, v in uuidexists.items():
#             vouchers = self.search([('refund_uuid', '=', k), ('voucher_id', '!=', False)])
#             refunds_to_create = self.search([('refund_uuid', '=', k), ('refund_id', '=', False)])
#             invoice = invoice.search([('id', '=', v)])
#             lines = []
#             if invoice:
#                 internalpartner = invoice.name[invoice.name.find("[") + 1:]
#                 internalpartner = internalpartner[:internalpartner.find("-")]
#
#                 voucherstoaffect = []
#                 vlines = []
#                 if vouchers:
#                     for ml in invoice.move_id.line_id:
#                         if ml.account_id.id == invoice.account_id.id:
#                             mlid = ml
#                             break
#
#                     for voucher in vouchers:
#                         if voucher.voucher_id.state == 'posted':
#                             voucherstoaffect.append(voucher.voucher_id)
#                             voucher.voucher_id.cancel_voucher()
#                             voucher.voucher_id.action_cancel_draft()
#                         elif voucher.voucher_id.state == 'cancel':
#                             continue
#
#                         for vl in voucher.voucher_id.line_dr_ids:
#                             if vl.move_line_id == mlid:
#                                 vlines.append(vl)
#
#                 if invoice.state == 'open':
#                     if invoice.move_id.state == 'posted':
#                         moveid = invoice.move_id
#                         moveid.button_cancel()
#                         moveid.write({'state': 'draft'})
#
#                     invoice.invoice_cancel()
#                     invoice.action_cancel_draft()
#
#                 if invoice.state == 'draft':
#                     for refund in refunds_to_create:
#                         taxcode = str(int(round((refund.amount_taxes / refund.amount_untaxed) * 100, 0)))
#                         if taxcode not in ['16', '8', '0']:
#                             taxcode = '16'
#                         taxid = TAXCODESALE[taxcode]
#                         if refund.num_mov in [620, 720]:
#                             acc_line_id = refund.sync_morsa_incomes_id.acc_refund_id.id
#                         else:
#                             acc_line_id = refund.sync_morsa_incomes_id.acc_benefit_id.id
#
#                         ref_to_record = refund.invoice_uuid.strip() if refund.invoice_uuid else ''
#                         ref_to_record += "[" + refund.invoice_number_serie.strip() + \
#                                          ("-" if refund.invoice_number_serie else '') + refund.invoice_number + "]"
#                         datos = {
#                             'name': invoice.operating_unit_id.code + '|' + ref_to_record,
#                             'account_id': acc_line_id,
#                             'quantity': 1,
#                             'price_unit': refund.amount_untaxed,
#                             'uos_id': 1,
#                             'company_id': 1,
#                             'invoice_line_tax_id': [(6, 0, [taxid]), ] if taxid else '',
#                             'invoice_id': invoice.id,
#                         }
#                         # SE CREAN LAS LINEAS DE LA FACTURA
#                         invoice_line = invoice_line.create(datos)
#                         refund.write({'refund_id': invoice.id, 'state': 'open'})
#                     invoice.button_reset_taxes()
#                     invoice.invoice_open()
#
#                 if vlines:
#                     for ml in invoice.move_id.line_id:
#                         if ml.account_id.id == invoice.account_id.id:
#                             mlid = ml
#                             break
#
#                     for vl in vlines:
#                         vl.write({'move_line_id': mlid.id, 'reconcile': False})
#
#                     for voucher in voucherstoaffect:
#                         voucher.proforma_voucher()
#         return sql
#
#     def _create_refund_header(self, refund, acc_line_id):
#
#         invoice = self.env['account.invoice']
#         ir_attach_fe = self.env['ir.attachment.facturae.mx']
#         ir_attach = self.env['ir.attachment']
#         obj_sales_log = self.env['sync.sales.log']
#         numrefund = ''
#         numinvoice = ''
#         esfiscal = ''
#         acc_relative_partner = refund.acc_relative_partner_id.id
#         cmsgforerror = 'Proveedor'
#         err = ''
#
#         esfiscal = (refund.refund_uuid.strip() != '') if refund.refund_uuid else False
#         numrefund = refund.refund_number_serie.strip()
#         numrefund += ('-' if numrefund else '') + refund.refund_number
#         journalnumber = numrefund
#
#         currencyvalue = 1
#         if refund.invoice_type == 'in_invoice':
#             acc_payable_receivable = refund.partner_id.property_account_payable.id
#             if refund.currency_id.id == CURRENCY_ID['1']:
#                 acc_payable_receivable = refund.sync_morsa_purchases_id.cuenta_prov_extranjeros.id
#                 currencyvalue = refund.currency_rate
#                 if refund.xmlfile and refund.xmlfile.strip() != 'None':
#                     currencyvalue = ir_attach_fe.parse_data(refund.xmlfile, "TipoCambio")
#             doctype = 'in_refund'
#             numinvoice = refund.invoice_number_serie
#             numinvoice += ('-' if numinvoice else '') + refund.invoice_number
#             if not esfiscal:
#                 numrefund = ''
#                 journalnumber = ''
#         else:
#             cmsgforerror = 'Cliente'
#             acc_payable_receivable = acc_relative_partner if acc_relative_partner \
#                         else refund.partner_id.property_account_receivable.id
#             doctype = 'out_refund'
#             numinvoice = refund.refund_ref
#             journalnumber = str(numinvoice) + "/" + numrefund
#
#         datos = {
#             'partner_id': refund.partner_id.id,
#             'company_id': 1,
#             'account_id': acc_payable_receivable,
#             'journal_id': self._get_refund_journal(refund, acc_line_id, esfiscal),
#             'operating_unit_id': refund.operating_unit_id.id,
#             'type': doctype,
#             'origin': numinvoice,
#             'date_invoice': refund.date_refund,
#             'number': journalnumber,
#             'internal_number': journalnumber,
#             'supplier_invoice_number': numrefund,
#             'reference': refund.refund_ref,
#             'name': refund.partner_vat + "[" + str(refund.partner_id_internal) + "-" + str(refund.partner_id_internal_socio) + "]",
#             'comment': str(refund.num_mov) + '-' + refund.comment,
#             'currency_id': refund.currency_id.id,
#             'currency_rate': currencyvalue,
#         }
#
#         invoice = invoice.create(datos)
#
#         if invoice and esfiscal and refund.xmlfile and refund.xmlfile.strip() != 'None':
#             datos = {
#                 'name': refund.partner_vat + '_' + numrefund + '.xml',
#                 'type': 'binary',
#                 'datas': refund.xmlfile.encode('base64'),
#                 'res_name': 'NC ' + cmsgforerror + ' ' + str(refund.refund_ref) + "/" + numrefund,
#                 'res_model': 'account.invoice',
#                 'company_id': 1,
#                 'datas_fname': refund.partner_vat + '_' + numrefund + '.xml',
#                 'res_id': invoice.id,
#             }
#             try:
#                 ir_attach = ir_attach.create(datos)
#             except Exception as e:
#                 err = repr(e)
#                 pass
#
#         """LOGICA PARA ASIGNAR EL UUID A LA NC CREADA """
#         if invoice and esfiscal and err == '':
#             datos = {
#                 'name': refund.partner_vat + '_' + numrefund,
#                 'uuid': refund.refund_uuid.strip(),
#                 'state': 'done',
#                 'company_id': 1,
#                 'cfdi_type': 'outgoing',
#                 'file_xml_sign': ir_attach.id,
#                 'type_attachment': 'account.invoice',
#                 'res_id': invoice.id,
#             }
#             try:
#                 ir_attach_fe = ir_attach_fe.create(datos)
#                 if ir_attach_fe:
#                     invoice.write({'cfdi_id': ir_attach_fe.id})
#             except Exception as e:
#                 err = repr(e)
#
#         return invoice, err
#
#     def create_table_erpid(self, ou):
#
#         sql = "SELECT 1 FROM  pg_tables WHERE  schemaname = 'public' AND tablename = 'erpid'"
#         conexion = self.env['sync.morsa.conexion']._get_conexion_direct(ou.ip_address, ou.data_base)
#         cursor = conexion.cursor()
#         try:
#             cursor.execute(sql)
#             record = cursor.fetchall()
#             if len(record) == 0:
#                 sql = """
#                 CREATE TABLE erpid (
#                     id int4 NOT NULL,
#                     erpid int4 NULL,
#                     tabla varchar(40) NOT NULL,
#                     tablaerp varchar(40) NULL,
#                     CONSTRAINT erpid_pk PRIMARY KEY (id,tabla)
#                 );
#                 CREATE INDEX erpid_erpid_idx ON erpid (erpid,tablaerp);
#                 """
#                 cursor.execute(sql)
#         except Exception as err:
#             cursor.rollback()
#             raise
#         finally:
#             conexion.commit()
#             conexion.close()
#
#         return
# ##class sync_morsa_refunds
#
#
# class DuplicateCFDIError(Exception):
#     message = 'Folio Fiscal (UUID) duplicado.'
#     pass
