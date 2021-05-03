
#-*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 OpenERP s.a. (<http://openerp.com>).
#
#    DME SOLUCIONES
#    Jorge Medina <alfonso.moreno@dmesoluciones.com>
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

CHEQUE_BOTADO = {220: [1649, 'NF-'], 310: [2063, 'NFDD-']}
IACC = 0
SERIENF = 1
DEFAULT_UNIT_ID = 318
DEFAULT_UNIT_CODE = '01'
CTA_VTAS_SERIE_ME = 2168


class SyncMorsaSales(models.Model):
    _name = 'sync.morsa.sales'

    fecha_inicial = fields.Date(
        default = fields.Date.today(),
        required=True,
    )

    fecha_final = fields.Date(
                default = fields.Date.today(),
                required=True,
    )

    cuenta_ventas_contado = fields.Many2one(
                'account.account',
                    default=2157,
                    domain=[('code', 'like', '410-'), ('type','!=', 'view')],
                    required=True
    )

    cuenta_ventas_credito = fields.Many2one(
                'account.account',
                    default=2158,
                    domain=[('code', 'like', '410-'), ('type', '!=', 'view')],
                    required=True
    )

    cuenta_ventas_pr = fields.Many2one(
                'account.account',
                    default=2159,
                    domain=[('code', 'like', '410-'), ('type', '!=', 'view')],
                    required=True
    )

    cliente_pr = fields.Many2one(
                'res.partner',
                    default=7275,
                    domain=[('name', 'like', 'Relacion')],
                    required=True
    )

    impuesto = fields.Many2one(
                'account.tax',
                default=50,
                domain=[('type_tax_use','=','sale')],
                required=True
    )

    ou = fields.Many2many('operating.unit',domain=[('ip_address', '!=', '')])

    unit_process = fields.Boolean('Procesar todas las UO', default=True)

    num_registros = fields.Integer('Numero de facturas', required=True)

    @api.multi
    def action_sync_sales(self):
        sesion = Session()
        informacion = sesion.get_session_info()
        bd = informacion.get('db')
        if bd[0:3] == 'GMM':
            unidades = []
            limitante = ""
            obj_invoice = self.env['account.invoice']
            obj_invoice_line = self.env['account.invoice.line']
            obj_ir_attachment_facturae = self.env['ir.attachment.facturae.mx']
            obj_sales_log = self.env['sync.sales.log']
            attachment = self.env['ir.attachment']
            obj_invoice_tax = self.env['account.invoice.tax']
            company = self.env['res.company'].search([('id', '=', 1)])
#           print '*** RFC COMPANY ***', company.partner_id.vat[2:]

            if self.unit_process:
                query_ou = ("select id from operating_unit")
                self.env.cr.execute(query_ou)
                operating_unit = self.env.cr.fetchall()
                for reg in operating_unit:
                    unidades.append(reg[0])
            else:
                if self.ou:
                    for reg in self.ou:
                        unidades.append(reg.id)
                else:
                    raise UserError(('Seleccionar una o mas unidades operativas'))

            if self.num_registros > 0:
                limitante = "limit %s"%str(self.num_registros)

            for unidad in unidades:
                # print "Intentare la Unidad %s"%(unidad)
                try:
                    if self.ou.code != "99":
                        sidfact = """f.id_factura,  f.numdocto,
                                     '['|| f.numcte::text || '-' || f.numsocio::text || ']' refcli,
                                     importe, iva, f.subtotal, f.importe_iva, f.importe_descuento, 
                                  """
                    else:
                        sidfact = """f.numdocto id_factura,  f.numdocto,
                                     '['|| f.numcte::text || '-' || f.numsocio::text || ']' refcli,
                                    importe, iva, round(importe / (1+(iva/100)), 2) subtotal, 
                                    round(importe - (importe / (1+(iva/100))), 2) importe_iva, f.importe_descuento, 
                                   """
                    unit = self.env['operating.unit'].browse(unidad)
                    """Se crea la conexion por cada unidad operativa que se selecciona"""
                    #sconexion = "host='%s' port=5432 dbname='%s' user='kerberox' password='alcatraz'" % (
                    #unit.ip_address, unit.data_base)
                    con = self.env['sync.morsa.conexion']._get_conexion_direct(unit.ip_address, unit.data_base)
                    #con = psycopg2.connect(sconexion)
                    cursor = con.cursor()
                    date_init = self.fecha_inicial.replace('-', '')
                    date_end = self.fecha_final.replace('-', '')
                    query_sales = ("""select %s 
                                        trim(cast(substr(fecha_gen::Text,1,10)||'T'||substr(fecha_gen::Text,12,8) as char(19))) fecha,
                                        f.fechaven, trim(f.serie) serie, parte_rel, tipo_venta, folio_fiscal, c.nombre,
                                        replace(c.rfc, '-','') rfc, regexp_replace(s.cfdi_xml, '[^\x20-\x7f\x0d\x1b]', ' ', 'g') cfdi_xml,
                                        invoice_id, tipomov
                                     from cxcfacturas f inner join cxcclientes c on f.numcte=c.numcte
                                         left join cfdi_sellado s on f.serie=s.serie and f.numdocto=s.numdocto
                                     where /*invoice_id = 0 and*/ estatus = 'V' and 
                                            ((folio_fiscal is not null and trim(folio_fiscal) <> '') or tipomov in (220,310)) and 
                                            fechadoc between %s and %s and tipomov in (110,120,210,220,230,240,250,310)
                                     order by id_factura %s;""" % (sidfact, date_init, date_end, limitante))

                    # and paso_erp = 0::bit clausula pendiente de agregar al query
                    try:
                        cursor.execute(query_sales)
                    except:
                        raise UserError("Error en el query: %s" % (query_sales))


                    registros = cursor.fetchall()
                    id_facturas = []
                    bloquefacturas = 0
                    query_update = ''

                    if not registros:
                        raise UserError('No se encontraron registros en las fechas seleccionadas: del %s al %s' \
						 % (self.fecha_inicial,self.fecha_final))

                    #id_factura             0
                    #numdocto               1
                    #refcli                 2
                    #importe                3
                    #iva                    4
                    #subtotal               5
                    #importe_iva            6
                    #importe_descuento      7
                    #fecha                  8
                    #fechaven               9
                    #serie                  10
                    #parte_rel              11
                    #tipo_venta             12
                    #folio_fiscal           13
                    #nombre                 14
                    #rfc                    15
                    #cfdi_xml               16
                    #invoice_id             17
                    #tipomov                18

                    for reg in registros:
                        #valido que la factura no haya sido sincronizada antes y si lo fue, la actualizo
                        invoice = ''
                        docto_origen = "'%s'"%(reg[0])
                        docto_cliente = reg[10] + \
                                        ('-' if reg[10]
                                         else (CHEQUE_BOTADO[reg[18]][SERIENF]+unit.code+'-')
                                        ) + str(reg[1])

                        oinvoice = obj_invoice.search([('type', '=', 'out_invoice'),
                                                        ('internal_number', '=', docto_cliente)])
                        #obj_invoice = self.env['account.invoice'].search([('origin','=','%s'%(reg[0])),
                        #                                    ('operating_unit_id','=',unit.id),('type','=','out_invoice')])
                        #print '** DOCTO ORIGEN: %s, %s' % (docto_origen, docto_cliente)

                        invoice = oinvoice.id if oinvoice else ''
                        if invoice:
                            if reg[17] != invoice:
                                sqlcorrige_invoice = """update cxcfacturas set invoice_id = %s 
                                                        where trim(serie)='%s' and numdocto=%s""" \
                                                     % (invoice, reg[10], reg[0])
                                cursor.execute(sqlcorrige_invoice)
                                con.commit()

                            if oinvoice.amount_total:
                                continue
                            else:
                                for line in oinvoice.invoice_line:
                                    line.unlink()

                        msgdocto = ''
                        haserrors = False

                        """ARREGLO CON LOS IDS DE LAS FACTURAS DEL SERVIDOR DE GM"""
                        id_facturas.append(reg[0])
                        """LOGICA PARA SELECCIONAR LA CUENTA CORRECTA EN EL ENCABEZADO Y DETALLADO DE LA FACTURA"""
                        ai_acc = unit.partner_id.property_account_receivable.id
                        if reg[11] == 'S':
                            ai_acc = self.cliente_pr.property_account_receivable.id
                            ail_acc = self.cuenta_ventas_pr.id
                        elif reg[12] == 'C':
                            ail_acc = self.cuenta_ventas_contado.id
                        else:
                            ail_acc = self.cuenta_ventas_credito.id

                        taxid = [(6, 0, [self.impuesto.id]),]
                        lineprice = reg[5] - reg[7]
                        if reg[18] in CHEQUE_BOTADO.keys():
                            ail_acc = CHEQUE_BOTADO[reg[18]][IACC]
                            lineprice = reg[3]
                            taxid = ''

                        msgdocto = 'RFC: %s. Serie:%s. Factura: %s. UUID: %s' % (reg[15], reg[10], reg[1], reg[13] if reg[13] else '')

                        date_inv = reg[8]
                        date_invoice = date_inv[0:10]
                        date_due = datetime.strptime(str(reg[9]), '%Y%m%d')
                        fecha_ven = datetime.strftime(date_due, '%Y-%m-%d')

                        try:
                            # ENCABEZADO DE LA FACTURA
                            invoice_header = {
                                'partner_id': unit.partner_id.id,
				                'company_id' : 1,
                                'account_id': ai_acc,
                                'journal_id': self._get_journal(unit, reg[10]),  # preguntar que diario usar
                                'operating_unit_id': unit.id if unit.code != '99' else DEFAULT_UNIT_ID,
                                'type': 'out_invoice',
                                'origin': str(reg[0]),
                                'date_invoice': date_invoice,
                                'date_due': fecha_ven,
                                'number': docto_cliente,
                                'internal_number': docto_cliente,
                                'reference': reg[2] + ' ' + reg[14].strip(),
                                'name': reg[15] + reg[2],
                                'comment': reg[18],
                            }
#                           SE CREA LA FACTURA Y AGREGO EL UPDATE AL CXCFACTURAS
#                           print  '**** EL ENCABEZADO ****', invoice_header
                            if not oinvoice:
                                oinvoice = obj_invoice.create(invoice_header)
                                invoice = oinvoice.id

                            #print  'Factura %s' % invoice, msgdocto
                            # if bloquefacturas >	= 50:
                            #    id_facturas.append(query_update)
                            #    query_update = ''
                            #    bloquefacturas = 0

                            """LOGICA PARA CREAR EL ATTACHMENT CON EL XML DE LA FACTURA"""

                            if reg[16] and not oinvoice.cfdi_id:
                                xml = reg[16]
                                xml_file = self._checking_characters(xml)
                                invoice_attachment = {
                                    'name': company.partner_id.vat[2:] + '_' + reg[10] + '-' + str(reg[1]) + '.xml',
                                    'type': 'binary',
                                    'datas': xml_file.encode('base64'),
                                    'res_model': 'account.invoice',
                                    'company_id': 1,
                                    'datas_fname': company.partner_id.vat[2:] + '_' + reg[10] + '-' + str(reg[1]),
                                    'res_id': invoice,
                                }
                                try:
                                    attch = attachment.create(invoice_attachment)
                                except Exception as e:
                                    msgdocto += 'En: Enlazando archivo XML. \n' + repr(e)
                                    haserrors = True
                                    pass

                            """LOGICA PARA ASIGNAR EL UUID A LA FACTURA CREADA EL UUID SE SACA DEL REGISTRO DONDE SE CREA EL ATTACHMENT"""
                            if reg[13] and not oinvoice.cfdi_id:
                                attachment_facturae = {
                                    'name': reg[10] + '-' + str(reg[1]),
                                    'uuid': reg[13],
                                    'state': 'done',
                                    'company_id': 1,
                                    'cfdi_type': 'incoming',
                                    'file_xml_sign': attch.id,
                                    'type_attachment': 'account.invoice',
                                    'res_id': invoice,
                                }
                                attch = ''
                                try:
                                    attch = obj_ir_attachment_facturae.create(attachment_facturae)
                                    if attch:
                                        oinvoice.write( {'cfdi_id': attch.id})
                                except Exception as e:
                                    msgdocto += 'En: Asignando UUID. \n' + repr(e)
                                    haserrors = True
                                    pass
                            """LINEAS DE LA FACTURA"""

                            invoice_line = {
                                'name': (unit.code.rstrip() if unit.code != '99' else DEFAULT_UNIT_CODE) +
                                            '|' + reg[2] + ' ' + reg[14].strip(),
                                'account_id': CTA_VTAS_SERIE_ME if oinvoice.journal_id.code.strip()[-1:] == 'E'
                                else ail_acc,
                                'quantity': 1,
                                'price_unit': lineprice,
                                'uos_id': 1,
				                'company_id': 1,
                                'invoice_line_tax_id': taxid,
                                'invoice_id': invoice,
                            }
                            # SE CREAN LAS LINEAS DE LA FACTURA
                            try:
                                obj_invoice_line.create(invoice_line)
                            except Exception as e:
                                msgdocto += 'En: Creando detalle. \n' + repr(e)
                                haserrors = True
                                pass

                            """SE ACTUALIZA LA LINEA DE IMPUESTOS PARA DESPUES ASIGNARLE DE MANERA MANUAL EL IMPORTE CORRECTO DEL IMPUESTO"""
                            if taxid:
                                oinvoice.button_reset_taxes()
                                invoice_tax = obj_invoice_tax.search([('invoice_id', '=', invoice)])
                                update_amount = {
                                    'amount': reg[6],
                                }
                                invoice_tax.update(update_amount)
                            """SE VALIDA LA FACTURA"""
                            oinvoice.invoice_open()
                            query_update = query_update + \
                                           "UPDATE cxcfacturas SET invoice_id = %s WHERE trim(serie) = '%s' and numdocto=%s;" % (
                                                                    invoice, reg[10], reg[0])
                        except Exception as e:
                            msgdocto += 'En: Creando encabezado. \n' + repr(e)
                            haserrors = True
                            pass
                        finally:
                            if haserrors:
                                sales_log = {
                                    'tipo': 'Venta',
                                    'operating_unit': unit.name,
                                    'message': msgdocto,
                                    'ip_addres': unit.ip_address,
                                    'data_base': unit.data_base,
                                }
                                obj_sales_log.create(sales_log)

                    #if bloquefacturas > 0 or query_update:
                    #    id_facturas.append(query_update)

                    #for sqlupdate in id_facturas:
                        #print "Query: ", sqlupdate
                        #cursor.execute(sqlupdate)
                        #con.commit()
                    #cursor.close()

                    if query_update:
                        #print query_update
                        cursor.execute(query_update)
                        con.commit()
                        cursor.close()
                except Exception as ex:
                    """EXCEPCION PARA LAS UNIDADES OPERATIVAS QUE NO PUDIERON CONECTARSE A SUS RESPECTIVAS
                       BASE DE DATOS Y SE CREA EL REGISTRO EN UN LOG DE SINCRONIZACION DE VENTAS EN DONDE
                       SE MUESTRAN LAS UNIDADES OPERATIVAS QUE NO SE PUDIERON CONECTAR A SU RESPECTIVO
                       SERVIDOR
                    """
                    #print"ENTRE AL EXCEPCTION POR LA UNIDAD:", unit.name
                    sales_log = {
                        'tipo': 'Venta',
                        'operating_unit' : unit.name,
                        'message' : repr(ex),
                        'ip_addres' : unit.ip_address,
                        'data_base' : unit.data_base,
                        }
                    obj_sales_log.create(sales_log)
                finally:
                    if con:
                        con.close()

            """QUERY DE ACTUALIZACION A PETICION EN EL REQUERIMIENTO"""
            #query_update = ("update cxcfacturas set paso_erp = 1::bit where id_factura in %s"%str((tuple(id_facturas))))
        else:
            raise UserError(("Base de datos erronea favor de correr el proceso en la base de datos GMM"))

    def _get_journal(self, unit=None,serie=None):

        if serie:
            if len(serie) >= 7:
                cCode = 'VT'
            else:
                cCode = 'VTA'
            cCode += serie
        else:
            cCode = 'VTANF'
        #cCode = 'VTA' + serie if serie else 'NF'
        journal = self.env['account.journal'].search([('code', '=', cCode)])
        datos = {}
        idjournal = journal.id
        if not journal.id:
            datos = {
                'name': 'Ventas ' + unit.name + ' ' + serie,
                'code': cCode,
                'type': 'sale',
                'analytic_journal_id': self.env['account.analytic.journal'].search([('code', '=', 'sale')]).id,
                'default_debit_account_id': self.cuenta_ventas_contado.id,
                'default_credit_account_id': self.cuenta_ventas_contado.id,
                'active': True,
                'update_posted': True,
            }
            journal = journal.create(datos)
            idjournal = journal.id


        return idjournal

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

