# -*- coding: utf-8 -*-
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

class sync_morsa_sales(models.Model):
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
                domain=[('code', '=','410-1-1')],
                required=True
    )

    cuenta_ventas_credito = fields.Many2one(
                'account.account',
                domain=[('code', '=','410-1-2')],
                required=True
    )

    cuenta_ventas_pr = fields.Many2one(
                'account.account',
                domain=[('code', '=','410-1-3')],
                required=True
    )

    cliente_pr = fields.Many2one(
                'res.partner',
                required=True
    )

    impuesto = fields.Many2one(
                'account.tax',
                domain=[('type_tax_use','=','sale')],
                required=True
    )

    ou = fields.Many2many('operating.unit')

    unit_process = fields.Boolean('Procesar todas las UO', default = True)

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
                try:
                    unit = self.env['operating.unit'].browse(unidad)
                    """Se crea la conexion por cada unidad operativa que se selecciona"""
                    con = psycopg2.connect("host='%s' port=none dbname='%s' user='none' password='none'"%(unit.ip_address,unit.data_base))
                    cursor = con.cursor()
                    date_init = self.fecha_inicial.replace('-','')
                    date_end = self.fecha_final.replace('-','')
                    query_sales = ("""select f.id_factura, f.numdocto,
                                        '['|| f.numcte::text || '-' || f.numsocio::text || ']' refcli,
                                         importe, iva, f.subtotal, f.importe_iva, f.importe_descuento,
                                         trim(cast(substr(fecha_gen::Text,1,10)||'T'||substr(fecha_gen::Text,12,8) as char(19))) fecha,
                                        f.fechaven, trim(f.serie) serie, parte_rel, tipo_venta, folio_fiscal, c.nombre,
                                         replace(c.rfc, '-','') rfc,  s.cfdi_xml
                                     from cxcfacturas f inner join cxcclientes c on f.numcte=c.numcte
                                         left join cfdi_sellado s on f.serie=s.serie and f.numdocto=s.numdocto
                                     where fechadoc between %s and %s and tipomov=110 order by numdocto %s;"""%(date_init,date_end,limitante))
                    #and paso_erp = 0::bit clausula pendiente de agregar al query
                    cursor.execute(query_sales)
                    registros = cursor.fetchall()
                    id_facturas = []
                    if registros:
                        for reg in registros:
                            """ARREGLO CON LOS IDS DE LAS FACTURAS DEL SERVIDOR DE GM"""
                            id_facturas.append(reg[0])
                            """LOGICA PARA SELECCIONAR LA CUENTA CORRECTA EN EL ENCABEZADO Y DETALLADO DE LA FACTURA"""
                            if reg[11] == 'S':
                                ai_acc = self.cliente_pr.property_account_receibavle.id
                                ail_acc = self.cuenta_ventas_pr.id
                            elif reg[12] == 'C':
                                ail_acc = self.cuenta_ventas_contado.id
                            else:
                                ai_acc = unit.partner_id.property_account_receivable.id
                                ail_acc = self.cuenta_ventas_credito.id

                            date_inv = reg[8]
                            date_invoice = date_inv[0:10]
                            date_due = datetime.strptime(str(reg[9]), '%Y%m%d')
                            fecha_ven = datetime.strftime(date_due,'%Y-%m-%d')
                            #ENCABEZADO DE LA FACTURA
                            invoice_header = {
                                    'partner_id': unit.partner_id.id,
                                    'account_id': ai_acc,
                                    'journal_id': 1,#preguntar que diario usar
                                    'operating_unit_id' : unit.id,
                                    'type'      : 'out_invoice',
                                    'origin'    : str(reg[0]),
                                    'date_invoice': date_invoice,
                                    'date_due' : fecha_ven,
                                    'number': reg[10] + '-' + str(reg[1]),
                                    'internal_number': reg[10] + '-' + str(reg[1]),
                                    'reference': reg[2]+' '+ reg[14].strip(),
                                    'name': reg[15] + reg[2],
                                    'origin': str(reg[0]),
                                }
                            #SE CREA LA FACTURA
                            invoice = obj_invoice.create(invoice_header)
                            """LOGICA PARA CREAR EL ATTACHMENT CON EL XML DE LA FACTURA"""
                            if reg[16]:
                                xml = reg[16]
                                xml_file = self._checking_characters(xml)
                                invoice_attachment = {
                                'name':unit.partner_id.vat_split + '.xml',
                                'type': 'binary',
                                'datas': xml_file.encode('base64'),
                                'res_model': 'account.invoice',
                                'datas_fname': unit.partner_id.vat_split + '_' + reg[10] + '-' + str(reg[1]),
                                'res_id': invoice.id,
                                }
                                attch = attachment.create(invoice_attachment)
                            """LOGICA PARA ASIGNAR EL UUID A LA FACTURA CREADA EL UUID SE SACA DEL REGISTRO DONDE SE CREA EL ATTACHMENT"""
                            if reg[13]:
                                attachment_facturae = {
                                    'name':reg[10] + '-' + str(reg[1]),
                                    'uuid' : reg[13],
                                    'state': 'done',
                                    'company_id':1,
                                    'cfdi_type' : 'incoming',
                                    'file_xml_sign': attch.id,
                                    'type_attachment': 'account.invoice',
                                    'res_id':invoice.id,
                                    }
                                obj_ir_attachment_facturae.create(attachment_facturae)
                            """LINEAS DE LA FACTURA"""
                            invoice_line = {
                                    'name': reg[2]+' '+ reg[14].strip(),
                                    'account_id' : ail_acc,
                                    'quantity': 1,
                                    'price_unit': reg[5] - reg[7],
                                    'uos_id': 1,
                                    'invoice_line_tax_id': [
                                            (6, 0, [self.impuesto.id]),
                                        ],
                                    'invoice_id': invoice.id,
                                }
                            #SE CREAN LAS LINEAS DE LA FACTURA
                            obj_invoice_line.create(invoice_line)
                            """SE ACTUALIZA LA LINEA DE IMPUESTOS PARA DESPUES ASIGNARLE DE MANERA MANUAL EL IMPORTE CORRECTO DEL IMPUESTO"""
                            invoice.button_reset_taxes()
                            invoice_tax = obj_invoice_tax.search([('invoice_id', '=', invoice.id)])
                            update_amount = {
                                'amount': reg[6],
                                }
                            invoice_tax.update(update_amount)
                            """SE VALIDA LA FACTURA"""
                            invoice.invoice_open()
                        else:
                            raise UserError(('No se encontraron registros en las fechas seleccionadas'))
                except:
                    """EXCEPCION PARA LAS UNIDADES OPERATIVAS QUE NO PUDIERON CONECTARSE A SUS RESPECTIVAS
                       BASE DE DATOS Y SE CREA EL REGISTRO EN UN LOG DE SINCRONIZACION DE VENTAS EN DONDE
                       SE MUESTRAN LAS UNIDADES OPERATIVAS QUE NO SE PUDIERON CONECTAR A SU RESPECTIVO
                       SERVIDOR
                    """
                    print"ENTRE AL EXCEPCTION POR LA UNIDAD:", unit.name
                    sales_log = {
                        'operating_unit' : unit.name,
                        'message' : 'Conexion refusada favor de checar parametros IP addres y Base de datos',
                        'ip_addres' : unit.ip_address,
                        'data_base' : unit.data_base,
                        }
                    obj_sales_log.create(sales_log)
            """QUERY DE ACTUALIZACION A PETICION EN EL REQUERIMIENTO"""
            #query_update = ("update cxcfacturas set paso_erp = 1::bit where id_factura in %s"%str((tuple(id_facturas))))
            #cursor.execute(query_update)
        else:
            raise UserError(("Base de datos erronea favor de correr el proceso en la base de datos GMM"))
#
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