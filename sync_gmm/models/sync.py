# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 OpenERP s.a. (<http://openerp.com>).
#
#    DME SOLUCIONES
#    Jorge Medina <jorge.medina@dmesoluciones.com>
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

from openerp.osv import orm, fields
from datetime import datetime, timedelta
import openerp.netsvc
import time
import psycopg2#,openerplib,
import xmlrpclib
from openerp.tools.translate import _
import os
import sync_conexion

class sync_morsa(orm.Model):
    _name ='sync.morsa'    

    #def _get_conexion(self, filename, dbname):
        ## Se lee el archivo de conexcion (no incluido en el branch por cuestiones de seguridad
		#BASE_PATH = reduce (lambda l,r: l + os.path.sep + r, os.path.dirname( os.path.realpath( __file__ ) ).split( os.path.sep )[:-1] )
		#archi = open(BASE_PATH + '/data/' + filename,'rb')
		#linea = archi.readline()
		#archi.close()        
		#parametros = linea.split(',')        
		#if dbname =='':
			#dbname = parametros[4]
		#return psycopg2.connect("host='%s' port=%s dbname='%s' user='%s' password='%s'"%(parametros[0], parametros[1], dbname, parametros[2], parametros[3])) 
   
    def action_sync_partner(self, cr, uid, ids, context=None):
        #Datos de Conexion
        conexion = self.pool.get('sync.morsa.conexion')._get_conexion("conexion.csv", "")
        
        print 'Conexion exitosa'
        
        cursor = conexion.cursor()
        #Query datos MORSA
        query = ("SELECT numcte, nombre, direccion, cod_postal, telefono, tel_dos, fax, "
                "limite_cred, rfc, vigente, correo_ventas, num_int, num_exterior, colonia, "
                "sucursal, agente1, cte_prov "
                "FROM clientes nolock "
                "Where pasado_erp = 'N';");
        cursor.execute(query)
        resultados= cursor.fetchall()
        cursorUpdate = conexion.cursor()

        #Objetos
        res_country_obj = self.pool.get('res.country')
        res_partner_obj = self.pool.get('res.partner')
        res_user_obj = self.pool.get('res.users')
        crm_case_section_obj = self.pool.get('crm.case.section')
        res_company_obj = self.pool.get('res.company')        
        sync_morsa_log_obj = self.pool.get('sync.morsa.log.generic')
        
        #Obtenemos el Id Pais México
        country_id = res_country_obj.search(cr, uid, [('name', '=', 'México')])[0]
        is_customer = False
        is_supplier = False
        #delete log
        sync_morsa_log_ids = sync_morsa_log_obj.search(cr, uid, [])
        sync_morsa_log_obj.unlink(cr, uid, sync_morsa_log_ids, context=None)   
        #Recorremos elementos
        for i in resultados:
            #0 numcte, 1 nombre, 2 direccion, 3 cod_postal, 4 telefono, 5 tel_dos, 6fax,
            #7 limite_cred, 8 rfc, 9 vigente, 10 correo_ventas, 11 num_int, 12 num_exterior, 13 colonia,
            #14 sucursal, 15 agente1, 16 cte_prov
            #print 'EN PROCESO %s'%i[1]
            #RFC con MX
            RFC="MX%s"%i[8].strip().replace('-','')
            
            #Cuando es RFC Generico se lo brinca
            if (RFC == 'MXXAXX010101000'):
                continue
                
            #Revisa si tiene Padre, toma el primer registro
            parent_id = res_partner_obj.search(cr, uid, [('vat', '=', RFC),('parent_id','=', None)])
            if len(parent_id) > 0 :
                parent_id = parent_id[0]
            else:
                parent_id = None
            
            #Obtener vendedor de MORSA
            vendedor_morsa = i[15]
            equipo_venta_morsa = 0
            
            #Si el codigo morsa tiene longitud mayor/igual a 3 toma el primer valor como equipo morsa el resto es el vendedor
            if len(str(vendedor_morsa)) >= 3:
                equipo_venta_morsa = str(vendedor_morsa)[0]
                vendedor_morsa = str(vendedor_morsa)[1:]
            # si el vendedor es 2 o 24 se cambia a vendedor 5
            if int(vendedor_morsa) == 2 or int(vendedor_morsa) == 24:
                vendedor_morsa = 5
            
            # Vendedor (Usuario)
            #vendedor_row = res_user_obj.search(cr, uid, [('login', '=', vendedor_morsa)])[0]
            
            #Equipo Vendedor COMENTADO 25/05/2015 SE VA A DEFINIR ING.DAVID
            #section_row = crm_case_section_obj.search(cr, uid, [('code', '=', str(equipo_venta_morsa))])[0]
            
            #Verifica si es Cliente o Proveedor
            if (i[16] == "C"): # C : Cliente
                is_customer = True
                is_supplier = False
            elif (i[16] == "P"): # P : Proveedor
                is_customer = False
                is_supplier = True
            elif (i[16] == "A"): # A : Ambos
                is_customer = True
                is_supplier = True

            #Sucursal(Company)
            suc = i[14]
            #print 'SUC %s'%suc
            #Evita problemas de sucursales inexistentes
            if (suc > 41):
                continue;
                
            if (suc < 10):
                suc = '0' + str(suc)

            suc = str(suc)
            company_id = res_company_obj.search(cr, uid, [('name', '=like', suc + '-%')])[0]

            res_company = res_company_obj.browse(cr, uid, company_id)
            #print i[1]
            #Se llena el objeto
            #Cuando no exista el Cliente se debe guardar dos veces (padre y contacto)
            id_openerp = 0
            if(parent_id != None):
                print 'Crea el Contacto'
                #Se crea el Contacto
                partner_id = res_partner_obj.create(cr, uid,{
                            'name': '%s %s'%(res_company.name[len(suc)+1:], i[0]),#'CTE-%s-%s-%s'%(i[14],i[0],res_company.name[len(suc)+1:]),
                            'street':i[2].strip(),
                            'vat':RFC,
                            #'ref':'CTE-%s-%s-%s'%(i[14],i[0],res_company.name[len(suc)+1:]),
                            'ref':'CTE-%s-%s'%(res_company.name[len(suc)+1:], i[0]),
                            'zip':i[3],
                            'email':i[10].strip(),
                            'phone':i[4],
                            'mobile':i[5],
                            'fax':i[6],
                            'credit_limit':i[7],
                            'l10n_mx_street4':i[11].strip(), #Int
                            'l10n_mx_street3':i[12], #Ext
                            'street2':i[13].strip(), #Col
                            'type':'invoice',
                            'parent_id': parent_id,
                            #'user_id': vendedor_row,
                            #'section_id': section_row, DESCOMENTAR EN SU MOMENTO
                            'company_id': None,
                            'customer': is_customer,
                            'supplier': is_supplier
                            }
                            ,context=context)
                print 'Id Generado del Contacto %s'%partner_id
                id_openerp = partner_id
                sync_morsa_log_obj.create(cr, uid, {
                                                    'morsa_code':i[0], #id morsa
                                                    'openerp_code': partner_id, #id openerp
                                                    'name': i[1], #name
                                                    'message': 'Contact'
                                                    }, context=context)
            else:
                print 'Crea el Padre y Contacto'
                #Se crea el Padre
                partner_id = res_partner_obj.create(cr, uid,{
                            'name': i[1],
                            'street':i[2].strip(),
                            'vat':RFC,
                            #'ref':'CTE-%s-%s-%s'%(i[14],i[0],res_company.name[len(suc)+1:]) if parent_id is not None else '',
                            'ref': '',
                            'zip':i[3],
                            'email':i[10].strip(),
                            'phone':i[4],
                            'mobile':i[5],
                            'fax':i[6],
                            'credit_limit':i[7],
                            'l10n_mx_street4':i[11].strip(), #Int
                            'l10n_mx_street3':i[12], #Ext
                            'street2':i[13].strip(), #Col
                            'type':'invoice',
                            #'parent_id': parent_id,
                            #'user_id': vendedor_row,
                            #'section_id': section_row,
                            'company_id': None,
                            'customer': is_customer,
                            'supplier': is_supplier
                            }
                            ,context=context)
                print 'Id Generado Partner Padre %s'%partner_id
                #create log
                sync_morsa_log_obj.create(cr, uid, {
                                                    'morsa_code':i[0], #id morsa
                                                    'openerp_code': partner_id, #id openerp
                                                    'name': i[1], #name
                                                    'message': 'Partner '
                                                    }, context=context)
                
                #Se crea el Contacto
                contact_id = res_partner_obj.create(cr, uid,{
                            'name': '%s %s'%(res_company.name[len(suc)+1:], i[0]),# if parent_id is not None else i[1],
                            'street':i[2].strip(),
                            'vat':RFC,
                            #'ref':'CTE-%s-%s-%s'%(i[14],i[0],res_company.name[len(suc)+1:]) if parent_id is not None else '',
                            'ref': 'CTE-%s-%s'%(res_company.name[len(suc)+1:], i[0]),
                            'zip':i[3],
                            'email':i[10].strip(),
                            'phone':i[4],
                            'mobile':i[5],
                            'fax':i[6],
                            'credit_limit':i[7],
                            'l10n_mx_street4':i[11].strip(), #Int
                            'l10n_mx_street3':i[12], #Ext
                            'street2':i[13].strip(), #Col
                            'type':'invoice',
                            'parent_id': partner_id,
                            #'user_id': vendedor_row,
                            #'section_id': section_row,
                            'company_id': None,
                            'customer': is_customer,
                            'supplier': is_supplier
                            }
                            ,context=context)
                print 'Id Generado del Contacto %s'%contact_id
                sync_morsa_log_obj.create(cr, uid, {
                                                    'morsa_code':i[0], #id morsa
                                                    'openerp_code': contact_id, #id openerp
                                                    'name': i[1], #name
                                                    'message': 'Contact'
                                                    }, context=context)
                #print 'CTE-%s-%s-%s'%(i[14],i[0],res_company.name[len(suc)+1:])
                id_openerp = contact_id
            #Actualiza registro en MORSA
            query = ("Update Clientes Set pasado_erp = 'S', id_openerp = %s "
                     "Where numcte = %s;"%(id_openerp, i[0]));
            try:
                print query
                cursorUpdate.execute(query)
            except Exception, e:
                conexion.rollback()
                raise osv.except_osv(_("Sym GMM"), _("I can't update table 'clientes'") + "\n[%s %s]\n%s"%(i[0],i[1],str(e)))
        #Commit
        conexion.commit()
        #Cierra Conexion
        cursorUpdate.close()
        cursor.close()
        
        return True

    def action_sync_product(self, cr, uid, ids, context=None):
        conexion = self.pool.get('sync.morsa.conexion')._get_conexion("conexion.csv", "")
        cursor = conexion.cursor()
        #Query datos MORSA
        query = ("SELECT codigo_art, nombre_art, p_lista "
                "FROM articulos "
                "Where pasado_erp = 'N' limit 10;");
        cursor.execute(query)
        resultados= cursor.fetchall()
        cursorUpdate = conexion.cursor()
        
        #Objetos
        res_product_obj = self.pool.get('product.product')
        res_template_obj = self.pool.get('product.template')

        #Recorremos elementos
        y=1
        for i in resultados:
            #0 codigo_art, 1 nombre_art
            #Se llena el objeto
            product_id = res_product_obj.create(cr, uid,{
                        'default_code':i[0],
                        'name': i[1],
                        #'category_id':i[],
                        'sale_ok':1,
                        'purchase_ok':1,
                        'list_price': i[2],
                        'type':'product',
                        'cost_method':'average'
                        }
                        ,context=context)
            print 'Id Generado Product %s'%product_id
            #Actualiza registro en MORSA
            query = ("Update articulos Set pasado_erp = 'S', id_openerp = %s "
                     "Where codigo_art = '%s';"%(product_id, i[0]));
            try:
                cursorUpdate.execute(query)
            except Exception, e:
                conexion.rollback()
                print str(e)
                raise osv.except_osv(_("Sym GMM"), _("I can't update table 'articulos'\n[%s %s]")%(i[0],i[1]))

        #Commit
        conexion.commit()
        #Cierra cursor
        cursorUpdate.close()
        cursor.close()
        return True

    def action_sync_update_partner(self, cr, uid, ids, context=None):
        #Datos de Conexion
        conexion = self.pool.get('sync.morsa.conexion')._get_conexion("conexion.csv", "")
        
        print 'Conexion exitosa'
        
        cursor = conexion.cursor()
        #Query datos MORSA
        query = ("SELECT numcte, nombre, direccion, cod_postal, telefono, tel_dos, fax, "
                "limite_cred, rfc, vigente, correo_ventas, num_int, num_exterior, colonia, "
                "sucursal, agente1, id_openerp, cte_prov "
                "FROM clientes "
                "Where pasado_erp = 'S'");
        cursor.execute(query)
        resultados= cursor.fetchall()
        cursorUpdate = conexion.cursor()

        #Objetos
        res_country_obj = self.pool.get('res.country')
        res_partner_obj = self.pool.get('res.partner')
        res_user_obj = self.pool.get('res.users')
        crm_case_section_obj = self.pool.get('crm.case.section')
        res_company_obj = self.pool.get('res.company')
        
        #~ #Obtenemos el Id Pais México
        #~ country_id = res_country_obj.search(cr, uid, [('name', '=', 'México')])[0]
        
        id_openerp = 0
        is_customer = True
        is_supplier = False
        #Recorremos elementos
        for i in resultados:
            #0 numcte, 1 nombre, 2 direccion, 3 cod_postal, 4 telefono, 5 tel_dos, 6fax,
            #7 limite_cred, 8 rfc, 9 vigente, 10 correo_ventas, 11 num_int, 12 num_exterior, 13 colonia,
            #14 sucursal, 15 agente1, 16 id_openerp, 17 cte_prov
            
            partner_id = i[16]
            print i[1]
            #Verifica si es Cliente o Proveedor
            if (i[16] == "C"): # C : Cliente
                is_customer = True
                is_supplier = False
            elif (i[16] == "P"): # P : Proveedor
                is_customer = False
                is_supplier = True
            elif (i[16] == "A"): # A : Ambos
                is_customer = True
                is_supplier = True

            #Se llena el objeto
            if(partner_id != None):
                #Se guarda el hijo porque ya tiene padre
                print 'Se actualiza el Contacto %s'%partner_id
                res_partner_obj.write(cr, uid, partner_id, {
                            #'name': 'CTE-%s-%s-%s'%(i[14],i[0],res_company.name[len(suc)+1:]) if parent_id is not None else i[1],
                            'street':i[2].strip(),
                            #'vat':RFC,
                            #'ref':'CTE-%s-%s-%s'%(i[14],i[0],res_company.name[len(suc)+1:]) if parent_id is not None else '',
                            'zip':i[3],
                            'email':i[10].strip(),
                            'phone':i[4],
                            'mobile':i[5],
                            'fax':i[6],
                            'credit_limit':i[7],
                            'l10n_mx_street4':i[11].strip(), #Int
                            'l10n_mx_street3':i[12], #Ext
                            'street2':i[13].strip(), #Col
                            'supplier':is_supplier
                            },
                            context=context)
                print 'Id Actualizado Contacto %s'%partner_id
                print 'Se actualiza el Padre del Contacto %s'%partner_id
                id_openerp = partner_id
                partner = res_partner_obj.browse(cr, uid, partner_id)
                print 'Antes del fuera de rango'
                print partner
                res_partner_obj.write(cr, uid, partner.parent_id.id, {
                            'name': i[1],
                            },
                            context=context)
                print 'Id Actualizado Padre'
                print partner.parent_id.id
            else:
                print 'No existe el Cliente'
            #Actualiza registro en MORSA
            query = ("Update Clientes Set id_openerp = %s "
                     "Where numcte = %s;"%(id_openerp, i[0]));
            try:
                if(id_openerp > 0):
                    cursorUpdate.execute(query)
            except Exception, e:
                conexion.rollback()
                raise osv.except_osv(_("Sym GMM"), _("I can't update table 'clientes'") + "\n[%s %s]\n%s"%(i[0],i[1],str(e)))
        #Commit
        conexion.commit()
        #Cierra Conexion
        cursorUpdate.close()
        cursor.close()
        
        return True

    def action_sync_update_product(self, cr, uid, ids, context=None):
        conexion = self.pool.get('sync.morsa.conexion')._get_conexion("conexion.csv", "")
        cursor = conexion.cursor()
        #Query datos MORSA
        query = ("SELECT codigo_art, nombre_art, p_lista, id_openerp "
                "FROM articulos "
                "Where pasado_erp = 'S' limit 10;");
        cursor.execute(query)
        resultados= cursor.fetchall()
        cursorUpdate = conexion.cursor()
        
        #Objetos
        res_product_obj = self.pool.get('product.product')
        res_template_obj = self.pool.get('product.template')

        #Recorremos elementos
        y=1
        for i in resultados:
            #0 codigo_art, 1 nombre_art, 3 id_openerp
            #Se llena el objeto
            product_id = res_product_obj.write(cr, uid, i[3], {
                        'default_code':i[0],
                        'name': i[1],
                        #'category_id':i[],
                        'sale_ok':1,
                        'purchase_ok':1,
                        'list_price': i[2],
                        'type':'product',
                        'cost_method':'average'
                        }
                        ,context=context)
            print 'Id Actualizado Product %s'%product_id
            #Actualiza registro en MORSA
            #~ query = ("Update articulos Set pasado_erp = 'S' "
                     #~ "Where codigo_art = '%s';"%i[0]);
            try:
                cursorUpdate.execute(query)
            except Exception, e:
                conexion.rollback()
                print str(e)
                raise osv.except_osv(_("Sym GMM"), _("I can't update table 'articulos'\n[%s %s]")%(i[0],i[1]))

        #Commit
        conexion.commit()
        #Cierra cursor
        cursorUpdate.close()
        cursor.close()
        return True
