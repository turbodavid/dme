# -*- coding: utf-8 -*-
import sys
import getopt, csv, xml.etree.cElementTree as ET
import base64

#archivos de lectura
_ACCOUNT_ACCOUNT = 'account.account.csv'
_ACCOUNT_ACCOUNT_TYPE = 'account.account.type.csv'

_NAME = 'bamc'
_CTA_BANCARIA = '1102-001-0001' #Cuenta Bancaria: Banamex Cta.6051481

#CUENTAS PLANTILLA
_CTA_A_COBRAR = '1104-001' # Cuenta a Cobrar: CLIENTES BAMC.-General
_CTA_A_PAGAR = '2101-001' # Cuenta a Pagar: PROVEEDORES BAMC.-General
_CAT_GASTOS = '4700' # Cuenta categoría gastos: COSTO DE ADQUISICION
_CAT_INGRESOS = '5600-001' #Cuenta de la categoría de ingresos: VENTAS TOTALES.- Ventas


#Configuracion VEPINSA###############################################
# _NAME = 'vepinsa'
# _CTA_BANCARIA = '2-1-4-0' #Cuenta Bancaria: SCOTIABANK, S.A. CTA.5271541
#
# #CUENTAS PLANTILLA
# _CTA_A_COBRAR = '4-1-0-0' # Cuenta a Cobrar: CLIENTES NACIONALES
# _CTA_A_PAGAR = '45-1-0-0' # Cuenta a Pagar: PROVEEDORES NACIONALES
# _CAT_GASTOS = '80-1-0-0' # Cuenta categoría gastos: XANTOFILAS AMARILLA
# _CAT_INGRESOS = '75-1-0-0' #Cuenta de la categoría de ingresos: VENTAS GRAVADAS TASA GENERAL NACIONAL

# #Configuracion MAYFE###############################################
# _NAME = 'mayfe'
# _CTA_BANCARIA = '102-000-100' #Cuenta Bancaria: BANCOS E INSTITUCIONES FINANCIERAS
#
# #CUENTAS PLANTILLA
# _CTA_A_COBRAR = '105-001-000' # Cuenta a Cobrar: CUENTA POR COBRAR CLIENTES
# _CTA_A_PAGAR = '201-001-000' # Cuenta a Pagar: PROVEEDORES NACIONALES
# _CAT_GASTOS = '501-001-000' # Cuenta categoría gastos: COSTO DE VENTA
# _CAT_INGRESOS = '401-001-000' #Cuenta de la categoría de ingresos: VENTAS NACIONALES
############################################################################

#Configuracion GMM###############################################
#_NAME = 'gmm'
#_CTA_BANCARIA = '111-3-1-1-1-01' #Cuenta Bancaria: BANCOS E INSTITUCIONES FINANCIERAS

#CUENTAS PLANTILLA
#_CTA_A_COBRAR = '112-1-1' # Cuenta a Cobrar: CUENTA POR COBRAR CLIENTES
#_CTA_A_PAGAR = '211-1-1' # Cuenta a Pagar: PROVEEDORES NACIONALES
#_CAT_GASTOS = '510-1-1' # Cuenta categoría gastos: COSTO DE VENTA
#_CAT_INGRESOS = '410-1-1' #Cuenta de la categoría de ingresos: VENTAS NACIONALES
############################################################################

#Configuracion AgroOrganicos###############################################
#_NAME = 'agrorganicos'
#_CTA_BANCARIA = '112001' #Cuenta Bancaria: BANCOS E INSTITUCIONES FINANCIERAS
#CUENTAS PLANTILLA
#_CTA_A_COBRAR = '121000' # Cuenta a Cobrar: CUENTA POR COBRAR CLIENTES
#_CTA_A_PAGAR = '221000' # Cuenta a Pagar: PROVEEDORES NACIONALES
#_CAT_GASTOS = '511001' # Cuenta categoría gastos: COSTO DE VENTA
#_CAT_INGRESOS = '410101' #Cuenta de la categoría de ingresos: VENTAS NACIONALES
############################################################################

#Configuracion O N E###############################################
#Configuracion CONyMAT###############################################
#_NAME = 'conymat'
#_CTA_BANCARIA = '1002 01 0001' #Cuenta Bancaria: BANCOS E INSTITUCIONES FINANCIERAS
#CUENTAS PLANTILLA
#_CTA_A_COBRAR = '1101' # Cuenta a Cobrar: CUENTA POR COBRAR CLIENTES
#_CTA_A_PAGAR = '2001 01' # Cuenta a Pagar: PROVEEDORES NACIONALES
#_CAT_GASTOS = '5001 01' # Cuenta categoría gastos: COSTO DE VENTA
#_CAT_INGRESOS = '4001 01 0001' #Cuenta de la categoría de ingresos: VENTAS NACIONALES
############################################################################

#Configuracion O N E###############################################
#_NAME = 'one'
#_CTA_BANCARIA = '1113' #Cuenta Bancaria: BANCOS E INSTITUCIONES FINANCIERAS
#CUENTAS PLANTILLA
#_CTA_A_COBRAR = '1122001000' # Cuenta a Cobrar: CUENTA POR COBRAR CLIENTES
#_CTA_A_PAGAR = '2122001000' # Cuenta a Pagar: PROVEEDORES NACIONALES
#_CAT_GASTOS = '6111001000' # Cuenta categoría gastos: COSTO DE VENTA
#_CAT_INGRESOS = '5111001000' #Cuenta de la categoría de ingresos: VENTAS NACIONALES
############################################################################

#Configuracion T E C N I K A###############################################
#_NAME = 'tecnika'
#_CTA_BANCARIA = '102' #Cuenta Bancaria: BANCOS E INSTITUCIONES FINANCIERAS
#CUENTAS PLANTILLA
#_CTA_A_COBRAR = '1050001000' # Cuenta a Cobrar: CUENTA POR COBRAR CLIENTES
#_CTA_A_PAGAR = '2001001000' # Cuenta a Pagar: PROVEEDORES NACIONALES
#_CAT_GASTOS = '5010001000' # Cuenta categoría gastos: COSTO DE VENTA
#_CAT_INGRESOS = '4010001000' #Cuenta de la categoría de ingresos: VENTAS NACIONALES
############################################################################

#Configuracion S A C S A###############################################
#_NAME = 'sacsa'
#_CTA_BANCARIA = '102-01-0000' #Cuenta Bancaria: BANCOS E INSTITUCIONES FINANCIERAS
##CUENTAS PLANTILLA
#_CTA_A_COBRAR = '105-01-0000' # Cuenta a Cobrar: CUENTA POR COBRAR CLIENTES
#_CTA_A_PAGAR = '201-01-0000' # Cuenta a Pagar: PROVEEDORES NACIONALES
#_CAT_GASTOS = '501-01-0000' # Cuenta categoría gastos: COSTO DE VENTA
#_CAT_INGRESOS = '401-01-0000' #Cuenta de la categoría de ingresos: VENTAS NACIONALES
############################################################################

#Configuracion M O R S A###############################################
#_NAME = 'morsa'
#_CTA_BANCARIA = '111-3-1-1-1-10' #Cuenta Bancaria: BANCOS E INSTITUCIONES FINANCIERAS

#CUENTAS PLANTILLA
#_CTA_A_COBRAR = '112-1-1' # Cuenta a Cobrar: CUENTA POR COBRAR CLIENTES
#_CTA_A_PAGAR = '211-1-1' # Cuenta a Pagar: PROVEEDORES NACIONALES
#_CAT_GASTOS = '510-1-1' # Cuenta categoría gastos: COSTO DE VENTA
#_CAT_INGRESOS = '410-1-1' #Cuenta de la categoría de ingresos: VENTAS NACIONALES
############################################################################

_ACCOUNT_TEMPLATE_XML = 'account_template_' + _NAME  +'.xml'
_ACCOUNT_TYPE_XML = 'account_type_' + _NAME + '.xml'

def main():
	#readFile()
	makeFile()
	makeFileTypes()

def readFile():
	reader = csv.reader(open(_ACCOUNT_ACCOUNT_TYPE, 'rb'))
	for index,row in enumerate(reader):
		print "==========================================="
		print 'Cuenta :' + str(index + 1)
		for column in row:
			print column
		print '\n'

def findCount(idC):
	#print 'findCount IdC:', idC
	parent = ''
	readerCounts = csv.reader(open(_ACCOUNT_ACCOUNT, 'rb'))
	for index,row in enumerate(readerCounts):
		#print row[0]
		if (row[0].decode('UTF-8')== idC):
			#print 'encontre:', row[1].decode('UTF-8')
			parent = row[1]
			break
		else:
			continue
	return parent

def makeFileTypes():
	reader = csv.reader(open(_ACCOUNT_ACCOUNT_TYPE, 'rb'))
	openerp = ET.Element("openerp")
	data = ET.SubElement(openerp, "data")
	diccionario = {1:"name",2:"code",3:"close_method"}
	#print diccionario[1]
    
    #Se comento todo el ciclo ya que no es necesario agregar "Tipo de Cuenta"
	for index,row in enumerate(reader):
		if(index== 0):
			continue
		else:			
			record = ET.SubElement( data, "record")
			model = row[0].decode('UTF-8')
			positionp= model.find('.')
			modelend = model[positionp+1:]
			#print modelend
			record.set( "id" , modelend )	
			record.set("model", "account.account.type")
			position = 1
			for i in range(0,3):
				field = ET.SubElement(record, "field")
				field.set("name",diccionario[position])
				txt= row[position]
				txtend= txt.decode('UTF-8')
				field.text = txtend.lower()
				position= position+1
	archivo = ET.ElementTree(openerp)
	archivo.write('plantilla/' + _ACCOUNT_TYPE_XML, encoding='UTF-8')

def makeFile():
	#reader = csv.reader(open(_ACCOUNT_ACCOUNT_TYPE, 'rb'))
	openerp = ET.Element("openerp")
	data = ET.SubElement(openerp, "data")
	#diccionario = {1:"name",2:"code",3:"close_method"}
	#print diccionario[1]
    
    #Se comento todo el ciclo ya que no es necesario agregar "Tipo de Cuenta"
# 	for index,row in enumerate(reader):
# 		if(index== 0):
# 			continue
# 		else:			
# 			record = ET.SubElement( data, "record")
# 			model = row[0].decode('UTF-8')
# 			positionp= model.find('.')
# 			modelend = model[positionp+1:]
# 			#print modelend
# 			record.set( "id" , modelend )	
# 			record.set("model", "account.account.type")
# 			position = 1
# 			for i in range(0,3):
# 				field = ET.SubElement(record, "field")
# 				field.set("name",diccionario[position])
# 				txt= row[position]
# 				txtend= txt.decode('UTF-8')
# 				field.text = txtend.lower()
# 				position= position+1
# 	archivo = ET.ElementTree(openerp)
# 	archivo.write('plantilla/' + _ACCOUNT_TYPE_XML, encoding='UTF-8')

	readerCounts = csv.reader(open(_ACCOUNT_ACCOUNT, 'rb'))
	diccionarioCounts = {1:"code",2:"eval",3:"ref",4:"type",5:"account_type_view",6:"name",7:"user_type",8:"sat_group_id",9:"nature"}
	for index,row in enumerate(readerCounts):
		if (index == 1):
			recordC0 = ET.SubElement(data, "record")
			idc0 = "cuenta" + _NAME + row[1].decode('UTF-8')
			recordC0.set("id",idc0)
			recordC0.set("model", "account.account.template")
			fieldc0= ET.SubElement(recordC0, 'field')
			fieldc0.set(diccionarioCounts[6], diccionarioCounts[1])
			fieldc0.text = row[1]
			fieldRe= ET.SubElement(recordC0, 'field')
			fieldRe.set(diccionarioCounts[6], 'reconcile')
			fieldRe.set(diccionarioCounts[2], row[2].decode('UTF-8'))
			fieldty0= ET.SubElement(recordC0, 'field')
			fieldty0.set(diccionarioCounts[6], diccionarioCounts[5])
			fieldty0.text=row[3].decode('UTF-8')
			fieldut0= ET.SubElement(recordC0, 'field')
			fieldut0.set(diccionarioCounts[6], diccionarioCounts[7])
			user_type= row[4].decode('UTF-8')
			#Va a poner la refencia tal cual tiene de UserType
			#positionut= user_type.find('.')
			#fieldut0.set(diccionarioCounts[3], user_type[positionut+1:])
			fieldut0.set(diccionarioCounts[3], user_type)
			fieldna= ET.SubElement(recordC0, 'field')
			fieldna.set(diccionarioCounts[6],diccionarioCounts[6])
			fieldna.text = row[5].decode('UTF-8')
			fieldsat_group0= ET.SubElement(recordC0, 'field')
			fieldsat_group0.set(diccionarioCounts[6],diccionarioCounts[8])
			fieldsat_group0.set(diccionarioCounts[3], row[6].decode('UTF-8'))
			fieldnature = ET.SubElement(recordC0, 'field')
			fieldnature.set(diccionarioCounts[6],diccionarioCounts[9])
			#fieldnature.text = row[7].decode('UTF-8')
			if(row[7].decode('UTF-8') == 'Deudora'):
				fieldnature.text= 'D'
			else:
				if(row[7].decode('UTF-8') == 'Acreedora'):
					fieldnature.text= 'A'
		else:
			
			if (index == 0):
				continue
			else:
				print 'ROW', row[8].decode('UTF-8')
				recordC = ET.SubElement( data, "record")
				idc = "cuenta" + _NAME + row[1].decode('UTF-8')
				recordC.set("id",idc)
				recordC.set("model", "account.account.template")
				field = ET.SubElement(recordC, 'field')
				field.set(diccionarioCounts[6], diccionarioCounts[1])
				field.text = row[1]
				fielde = ET.SubElement(recordC, 'field')
				fielde.set(diccionarioCounts[2],row[2])
				fielde.set(diccionarioCounts[6],'reconcile')
				fieldr = ET.SubElement(recordC, 'field')
				fieldr.set(diccionarioCounts[3],'cuenta' + _NAME + findCount(row[8].decode('UTF-8')))
				fieldr.set(diccionarioCounts[6],'parent_id')
				fieldv = ET.SubElement(recordC, 'field')
				fieldv.set(diccionarioCounts[6],diccionarioCounts[4])
				if (row[3].lower() == 'regular'):
					fieldv.text = 'other'
				else:
					fieldv.text = row[3].lower()
				fieldut = ET.SubElement(recordC, 'field')
				ref = row[4].decode('UTF-8')
				#positionr = ref.find('.')
				#fieldut.set("ref",ref[positionr+1:])
				fieldut.set("ref",ref)
				fieldut.set(diccionarioCounts[6],diccionarioCounts[7])
				fieldn = ET.SubElement(recordC, 'field')
				fieldn.set(diccionarioCounts[6],diccionarioCounts[6])
				fieldn.text = row[5].decode('UTF-8')
				fieldsat_group = ET.SubElement(recordC, 'field')
				fieldsat_group.set(diccionarioCounts[6],diccionarioCounts[8])
				if(row[6]):
					fieldsat_group.set(diccionarioCounts[3], row[6].decode('UTF-8'))
				#else:
				#	fieldsat_group.set(diccionarioCounts[3],'l10n_mx.g100')
				
				fieldnature= ET.SubElement(recordC, 'field')
				fieldnature.set(diccionarioCounts[6],"nature")
				if(row[7].decode('UTF-8') == 'Deudora'):
					fieldnature.text= 'D'
				else:
					if(row[7].decode('UTF-8') == 'Acreedora'):
						fieldnature.text= 'A'
			

	diccionarioTemp=	{1:"name",2:"ref",3:"account_root_id",4:"tax_code_root_id",5:"bank_account_view_id",6:"property_account_receivable",7:"property_account_payable",8:"property_account_expense_categ",9:"property_account_income_categ",10:"currency_id"}	
	
	recordTemplate = ET.SubElement(data, "record")
	recordTemplate.set('id', _NAME + '_chart_template')
	recordTemplate.set('model','account.chart.template')
	
	fieldname = ET.SubElement(recordTemplate,'field')
	fieldname.set(diccionarioTemp[1], diccionarioTemp[1])
	fieldname.text = 'Plan Contable de ' + _NAME

	field0 = ET.SubElement(recordTemplate,'field')
	field0.set(diccionarioTemp[1], diccionarioTemp[3])
	field0.set(diccionarioTemp[2],'cuenta' + _NAME + '0')	

	fieldt = ET.SubElement(recordTemplate,'field')
	fieldt.set(diccionarioTemp[1], diccionarioTemp[4])
	fieldt.set(diccionarioTemp[2],'l10n_mx.vat_code_tax')

	#Falta Definir bien las Cuentas Contables para la plantilla
	
    # Cuenta bancaria = INSTITUCIONES BANCARIAS E INSTITUCIONES FINANCIERAS
	fieldp = ET.SubElement(recordTemplate,'field')		
	fieldp.set(diccionarioTemp[1], diccionarioTemp[5])
	fieldp.set(diccionarioTemp[2],'cuenta' + _NAME + _CTA_BANCARIA)

    # Cuenta a cobrar = CUENTA POR COBRAR CLIENTES
	fieldex = ET.SubElement(recordTemplate,'field')
	fieldex.set(diccionarioTemp[1], diccionarioTemp[6])
	fieldex.set(diccionarioTemp[2],'cuenta' + _NAME + _CTA_A_COBRAR)
    
    # Cuenta a pagar = PROVEEDORES NACIONALES
	fieldex = ET.SubElement(recordTemplate,'field')
	fieldex.set(diccionarioTemp[1], diccionarioTemp[7])
	fieldex.set(diccionarioTemp[2],'cuenta' + _NAME + _CTA_A_PAGAR)

    # Cuenta categoría gastos = COSTOS DE VENTAS
	fieldex = ET.SubElement(recordTemplate,'field')
	fieldex.set(diccionarioTemp[1], diccionarioTemp[8])
	fieldex.set(diccionarioTemp[2],'cuenta' + _NAME + _CAT_GASTOS)
    
    # Cuenta de la categoría de ingresos = VENTAS NACIONALES
	fieldin = ET.SubElement(recordTemplate,'field')
	fieldin.set(diccionarioTemp[1], diccionarioTemp[9])
	fieldin.set(diccionarioTemp[2],'cuenta' + _NAME + _CAT_INGRESOS)

	fieldn = ET.SubElement(recordTemplate,'field')
	fieldn.set(diccionarioTemp[1], diccionarioTemp[10])
	fieldn.set(diccionarioTemp[2], 'base.MXN')	


	tree = ET.ElementTree(openerp)
	tree.write('plantilla/' + _ACCOUNT_TEMPLATE_XML, encoding='UTF-8')

if __name__ == "__main__":
    main()
