import logging
logger = logging.getLogger('report_aeroo')

from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse
import random
import time
import re
import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        print '__init__*************************************'        
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'lines':self.get_lines,            
        })
        self.context = context     


    def get_lines(self, o):
        cr = self.cr
        uid = self.uid      
        result = []
        list_product = []
        #print o
        date_ini = o['date_ini']
        date_fin = o['date_fin']
        #date_cls = o['date_close']
        comp_id = o['company_id'][0]
        part_id = o['partner_id'][0]
        insolutos = o['chk_insoluto']
        if insolutos!=True:
            sql = ( "SELECT *,(select apt.name from account_payment_term apt where id= tbl.payment_term) as tipoPago FROM ("
                            "SELECT rp2.name as Vendedor, ccs.name Zona,  ai.move_id, ai.partner_id, rp.name Cliente, rp.vat_split RFC, aj.name Sucursal, ai.number Factura, "
                                    "ai.type TipoDocto, ai.state Estatus, ai.date_invoice FechaFactura, ai.date_due Vencimiento, get_categ_firstlevel(pt.categ_id) Familia, "
                                    "pt.name NombreProducto, get_categ_secondlevel(pt.categ_id,1) Linea, pc.name Proveedor, ail.quantity Cantidad, "
                                    "ail.price_subtotal Venta, 0 Devolucion, 0 Bonificacion, payment.last_rec_date DiaPago, ai.payment_term, ai.amount_total  as totalfactura, ai.residual  SaldoActual, fn_get_payment_acum(ai.move_id, payment.date_payment) abonos, ail.price_unit precio "
                            "FROM account_invoice ai INNER JOIN res_partner rp ON (ai.partner_id = rp.id) INNER JOIN account_invoice_line ail ON (ail.invoice_id = ai.id) "
                                                    "INNER JOIN product_product pp ON (ail.product_id = pp.id) "
                                                    "INNER JOIN product_template pt ON (pp.product_tmpl_id = pt.id) INNER JOIN product_category pc ON (pt.categ_id = pc.id) "
                                                    "INNER JOIN res_users ru ON (ai.user_id = ru.id) INNER JOIN res_partner rp2 ON (ru.partner_id = rp2.id) "
                                                    "LEFT  JOIN crm_case_section ccs ON (ai.section_id = ccs.id) "
                                                    "INNER JOIN account_journal aj ON (ai.journal_id = aj.id) "
                                                    "LEFT JOIN fn_get_payment(ai.move_id, '" + date_fin + "') Payment ON (ai.move_id = payment.move_id) "
                            "WHERE ai.date_invoice BETWEEN '" + date_ini + "' AND '" + date_fin + "' AND ai.type IN ('out_invoice')  AND ai.state IN ('open','paid') "
                            "AND ai.company_id = " + str(comp_id) + " AND ai.partner_id=" + str(part_id) + " "
                            "UNION "
                            "SELECT rp2.name as Vendedor, ccs.name Zona, ai.move_id, ai.partner_id, rp.name Cliente, rp.vat_split RFC, aj.name Sucursal, ai.number Factura, "
                                    "ai.type TipoDocto, ai.state Estatus, ai.date_invoice FechaFactura, ai.date_due Vencimiento, get_categ_firstlevel(pt.categ_id) Familia, "
                                    "pt.name NombreProducto, get_categ_secondlevel(pt.categ_id,1) Linea, pc.name Proveedor, CASE WHEN ai.origin IS NULL THEN 0 ELSE -ail.quantity END Cantidad, "
                                    "0 Venta, CASE WHEN ai.origin IS NOT NULL THEN -ail.price_subtotal ELSE 0 END Devolucion, CASE WHEN ai.origin IS NULL THEN -ail.price_subtotal ELSE 0 END Bonificacion, "
                                    "payment.last_rec_date DiaPago, ai.payment_term, ai.amount_total  as totalfactura, -ai.residual  SaldoActual, -fn_get_payment_acum(ai.move_id, payment.date_payment) abonos, -ail.price_unit precio "
                            "FROM account_invoice ai INNER JOIN res_partner rp ON (ai.partner_id = rp.id) INNER JOIN account_invoice_line ail ON (ail.invoice_id = ai.id) "
                                                    "INNER JOIN product_product pp ON (ail.product_id = pp.id) "
                                                    "INNER JOIN product_template pt ON (pp.product_tmpl_id = pt.id) INNER JOIN product_category pc ON (pt.categ_id = pc.id) "
                                                    "INNER JOIN res_users ru ON (ai.user_id = ru.id) INNER JOIN res_partner rp2 ON (ru.partner_id = rp2.id) "
                                                    "LEFT JOIN crm_case_section ccs ON (ai.section_id = ccs.id) INNER JOIN account_journal aj ON (ai.journal_id = aj.id) "
                                                    "LEFT JOIN fn_get_payment(ai.move_id, '" + date_fin + "') Payment ON (ai.move_id = payment.move_id) "
                            "WHERE ai.date_invoice BETWEEN '" + date_ini + "' AND '" + date_fin + "' AND ai.type IN ('out_refund') AND ai.state IN ('open','paid') "
                            "AND ai.company_id = " + str(comp_id) + " AND ai.partner_id=" + str(part_id) + " "
                            "And ai.parent_id in " # NCR este en facturas filtradas
                                "( "
                                    "Select Id "
                                    "FROM account_invoice ai "
                                    "WHERE ai.date_invoice  BETWEEN '" + date_ini + "' AND '" + date_fin + "' "
                                        "AND ai.type IN ('out_invoice') "
                                        "AND ai.state IN ('open','paid') "
                                        "AND ai.company_id = " + str(comp_id) + " AND ai.partner_id=" + str(part_id) + " "
                                ") "
                            ") tbl "
                        "ORDER BY  factura, linea,  FechaFactura" )
        else:
            sql = ( "SELECT *,(select apt.name from account_payment_term apt where id= tbl.payment_term) as tipoPago FROM ("
                            "SELECT rp2.name as Vendedor, ccs.name Zona,  ai.move_id, ai.partner_id, rp.name Cliente, rp.vat_split RFC, aj.name Sucursal, ai.number Factura, "
                                    "ai.type TipoDocto, ai.state Estatus, ai.date_invoice FechaFactura, ai.date_due Vencimiento, get_categ_firstlevel(pt.categ_id) Familia, "
                                    "pt.name NombreProducto, get_categ_secondlevel(pt.categ_id,1) Linea, pc.name Proveedor, ail.quantity Cantidad, "
                                    "ail.price_subtotal Venta, 0 Devolucion, 0 Bonificacion, payment.last_rec_date DiaPago, ai.payment_term, ai.amount_total  as totalfactura, ai.residual  SaldoActual,  fn_get_payment_acum(ai.move_id, payment.date_payment) abonos, ail.price_unit precio "
                            "FROM account_invoice ai INNER JOIN res_partner rp ON (ai.partner_id = rp.id) INNER JOIN account_invoice_line ail ON (ail.invoice_id = ai.id) "
                                                    "INNER JOIN product_product pp ON (ail.product_id = pp.id) "
                                                    "INNER JOIN product_template pt ON (pp.product_tmpl_id = pt.id) INNER JOIN product_category pc ON (pt.categ_id = pc.id) "
                                                    "INNER JOIN res_users ru ON (ai.user_id = ru.id) INNER JOIN res_partner rp2 ON (ru.partner_id = rp2.id) "
                                                    "LEFT  JOIN crm_case_section ccs ON (ai.section_id = ccs.id) "
                                                    "INNER JOIN account_journal aj ON (ai.journal_id = aj.id) "
                                                    "LEFT JOIN fn_get_payment(ai.move_id, '" + date_fin + "') Payment ON (ai.move_id = payment.move_id) "
                            "WHERE ai.date_invoice BETWEEN '" + date_ini + "' AND '" + date_fin + "' AND ai.type IN ('out_invoice')  AND ai.state IN ('open') "
                            "AND ai.company_id = " + str(comp_id) + " AND ai.partner_id=" + str(part_id) + " "
                            "UNION "
                            "SELECT rp2.name as Vendedor, ccs.name Zona, ai.move_id, ai.partner_id, rp.name Cliente, rp.vat_split RFC, aj.name Sucursal, ai.number Factura, "
                                    "ai.type TipoDocto, ai.state Estatus, ai.date_invoice FechaFactura, ai.date_due Vencimiento, get_categ_firstlevel(pt.categ_id) Familia, "
                                    "pt.name NombreProducto, get_categ_secondlevel(pt.categ_id,1) Linea, pc.name Proveedor, CASE WHEN ai.origin IS NULL THEN 0 ELSE -ail.quantity END Cantidad, "
                                    "0 Venta, CASE WHEN ai.origin IS NOT NULL THEN -ail.price_subtotal ELSE 0 END Devolucion, CASE WHEN ai.origin IS NULL THEN -ail.price_subtotal ELSE 0 END Bonificacion, "
                                    "payment.last_rec_date DiaPago, ai.payment_term, ai.amount_total as totalfactura, -ai.residual  SaldoActual, - fn_get_payment_acum(ai.move_id, payment.date_payment) abonos, -ail.price_unit precio  "
                            "FROM account_invoice ai INNER JOIN res_partner rp ON (ai.partner_id = rp.id) INNER JOIN account_invoice_line ail ON (ail.invoice_id = ai.id) "
                                                    "INNER JOIN product_product pp ON (ail.product_id = pp.id) "
                                                    "INNER JOIN product_template pt ON (pp.product_tmpl_id = pt.id) INNER JOIN product_category pc ON (pt.categ_id = pc.id) "
                                                    "INNER JOIN res_users ru ON (ai.user_id = ru.id) INNER JOIN res_partner rp2 ON (ru.partner_id = rp2.id) "
                                                    "LEFT JOIN crm_case_section ccs ON (ai.section_id = ccs.id) INNER JOIN account_journal aj ON (ai.journal_id = aj.id) "
                                                    "LEFT JOIN fn_get_payment(ai.move_id, '" + date_fin + "') Payment ON (ai.move_id = payment.move_id) "
                            "WHERE ai.date_invoice BETWEEN '" + date_ini + "' AND '" + date_fin + "' AND ai.type IN ('out_refund') AND ai.state IN ('open') "
                            "AND ai.company_id = " + str(comp_id) + " AND ai.partner_id=" + str(part_id) + " "
                            "And ai.parent_id in " # NCR este en facturas filtradas
                                "( "
                                    "Select Id "
                                    "FROM account_invoice ai "
                                    "WHERE ai.date_invoice  BETWEEN '" + date_ini + "' AND '" + date_fin + "' "
                                        "AND ai.type IN ('out_invoice') "
                                        "AND ai.state IN ('open','paid') "
                                        "AND ai.company_id = " + str(comp_id) + " AND ai.partner_id=" + str(part_id) + " "
                                ") "
                            ") tbl "
                        "ORDER BY  factura, linea, FechaFactura" )
        
        print sql
        self.cr.execute(sql)
        data = self.cr.dictfetchall()
        cont = 1
        factura = ""
        facturan = ""
        list_product = []
        lista_detalles = []
        lista_todo =[]
        lineas = []        
        sumaFactura = 0
        sumaAbonos = 0
        sumaSaldo = 0
        totalFacturas = 0
        #sumalinea = 0
        for i in data:
            #print 'inicio'
            if cont == 1:             
                totalFacturas = totalFacturas + 1
                sumaFactura = sumaFactura + i['totalfactura']
                sumaSaldo = sumaSaldo + i['saldoactual']
                sumaAbonos = sumaAbonos+ i['abonos']
                list_product.append({   'factura': i['factura'],
                                        'fechafactura': i['fechafactura'],
                                        'vencimiento': i['vencimiento'],
                                        'tipopago': i['tipopago'],                                                                         
                                        'zona': i['zona'],
                                        'rfc': i['rfc'],                                        
                                        'totalfactura': i['totalfactura'],
                                        'saldoactual': i['saldoactual'],                                        
                                        'lineas' : [],
                                        'abonos' : i['abonos'],
                                     })
                lineas = list_product[0]['lineas']
                lineas.append({ 'linea': i['linea'],
                                'suma': 0,
                                'detalles': [],
                            })                         
                lineas[0]['suma'] = i['venta']
                #sumaLinea = lineas[0]['suma']
                lista_detalles = lineas[0]['detalles']
                lista_detalles.append({        'producto': i['nombreproducto'],
                                                'preciounit': i['precio'],
                                                'cantidad' : i['cantidad'],
                                                'importe_producto' : i['venta'],                                                
                                            }) 
                factura = i['factura']
            else:
                facturan = i['factura']
                if factura <> facturan:
                    totalFacturas = totalFacturas + 1
                    sumaFactura = sumaFactura + i['totalfactura']
                    sumaSaldo = sumaSaldo + i['saldoactual']
                    sumaAbonos = sumaAbonos+ i['abonos']
                    factura = i['factura']
                    list_product.append({   'factura': i['factura'],
                                            'fechafactura': i['fechafactura'],
                                            'vencimiento': i['vencimiento'],
                                            'tipopago': i['tipopago'],                                                                         
                                            'zona': i['zona'],
                                            'rfc': i['rfc'],                                        
                                            'totalfactura': i['totalfactura'],
                                            'saldoactual': i['saldoactual'],                                             
                                            'lineas' : [],
                                            'abonos' : i['abonos'],
                                         })
                    lineas = list_product[len(list_product)-1]['lineas']
                    lineas.append({ 'linea': i['linea'],
                                    'suma': 0,
                                    'detalles': [],
                                })                      
                    lineas[0]['suma'] = i['venta']
                    sumaLinea = lineas[0]['suma']
                    lista_detalles = lineas[0]['detalles']
                    #lista_detalles = list_product[len(list_product)-1]['detalles']
                    lista_detalles.append({    'producto': i['nombreproducto'],
                                                'preciounit': i['precio'],
                                                'cantidad' : i['cantidad'],
                                                'importe_producto' : i['venta'],                                                
                                            })
                else:
                    if lineas[len(lineas)-1]['linea'] == i['linea']:
                        #sumaLinea = sumaLinea + i['venta']                        
                        lineas[len(lineas)-1]['suma'] = lineas[len(lineas)-1]['suma'] + i['venta']
                    else:
                        lineas.append({ 'linea': i['linea'],
                                    'suma': 0,
                                    'detalles': [],
                                })
                        lineas[len(lineas)-1]['suma'] = lineas[len(lineas)-1]['suma'] + i['venta']
                        #sumaLinea = lineas[len(lineas)-1]['suma']
                        lista_detalles = lineas[len(lineas)-1]['detalles']
                    lista_detalles.append({'producto': i['nombreproducto'],
                                                'preciounit': i['precio'],
                                                'cantidad' : i['cantidad'],
                                                'importe_producto' : i['venta'],                                                
                                            })
            cont = cont + 1
        lista_todo.append({ 'sumaFactura': sumaFactura,
                            'lista_facturas' : list_product,
                            'sumaSaldo' : sumaSaldo,
                            'sumaAbonos' : sumaAbonos,
                        })
        print totalFacturas
        return lista_todo
    
      
    
