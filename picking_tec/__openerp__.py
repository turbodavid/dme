# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
#    Jesus Meza (jesus.meza@dmesoluciones.com)
############################################################################
#    Coded by: Jesus Meza (jesus.meza@dmesoluciones.com)
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

{
    "name" : "Stock Picking Out Tec.",
    "version" : "1.0",
    "author" : "DME Soluciones",
    "category" : "Report",
    "sequence": 15,
    "description" : """This module add some fields to Stock Picking Out Report.

Se requiere modificar el reporte en Configuración->Acciones->Informes, se debe buscar picking y en Vale de Entrega poner el reporte con la siguiente ruta: picking_tec/report/picking_tecnologico.rml""",
    "website" : "http://www.dmesoluciones.com/",
    "license" : "AGPL-3",
    "depends" : ["stock", "l10n_mx_invoice_amount_to_text",],
    "data" : ["stock_report_tec.xml"],
    "test": [],
    "installable" : True,
    "application": True,
    "active" : False,
}
