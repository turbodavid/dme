# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
############################################################################
#    Coded by: Yukie Ley (cindy.ley@dmesoluciones.com)
#    Coded by: Jorge Medina (jorge.medina@dmesoluciones.com)
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
    'name' : "DMSolar Reports",
    'version' : "1.0",
    'author' : "DME Soluciones",
    'website' : "http://www.dmesoluciones.com/",
    'category' : "Report",
    'summary': 'Reports, Quotations, Sales Orders, Purchases',
    'description': """
Module personalizado para DM Solar (reportes, campos, ventas, compras, almacen) 
===============================================================================

* **Selecciona la compañia y en la sección Encabezado/Pie de Página pega lo siguiente**

<header>
    <pageTemplate>
        <frame id="first" x1="1.3cm" y1="3.0cm" height="23.7cm" width="19.0cm"/>
         <stylesheet>
            <!-- Set here the default font to use for all <para> tags -->
            <paraStyle name="Normal" fontName="DejaVu Sans"/>
            <paraStyle name="main_footer" fontSize="8.0" alignment="CENTER"/>
            <paraStyle name="web_footer" fontSize="10.0" alignment="CENTER"/>
            <paraStyle name="main_header" fontSize="8.0" leading="10" alignment="LEFT" spaceBefore="0.0" spaceAfter="0.0"/>
         </stylesheet>
        <pageGraphics>
            <!-- Set here the default font to use for all <drawString> tags -->
            <setFont name="DejaVu Sans" size="8"/>
            <!-- You Logo - Change X,Y,Width and Height -->
            <image x="1.3cm" y="26.7cm" height="70.0" >[[ company.logo or removeParentNode("image") ]]</image>
            <fill color="black"/>
            <stroke color="red"/>

            <!-- page header -->
            <lines>1.3cm 26.7cm 20cm 26.7cm</lines>
            
            <!--page bottom-->
			<place x="1.3cm" y=".5cm" height="2.55cm" width="19.0cm">
				<para style="main_footer">[[ company.rml_footer ]] [[ company.street or "" ]] [[ company.l10n_mx_street3 or "" ]] [[ company.l10n_mx_street4 or "" ]] [[ company.street2 or "" ]] [[ company.city or "" ]] [[ company.l10n_mx_city2 or "" ]] [[ company.state_id.name or "" ]] [[ company.country_id.name or "" ]] [[ company.zip or "" ]]</para>
			</place>
            <lines>1.2cm 2.65cm 19.9cm 2.65cm</lines>
            <place x="1.3cm" y="0cm" height="2.55cm" width="19.0cm">
				<para style="web_footer"><font color="red">[[company.website]]</font></para>
            </place>
        </pageGraphics>
    </pageTemplate>
</header>



DAR PERMISOS
============
	(Configuracion/Usuarios/Usuarios)
	El administrador debe dar permisos para el módulo Dme_solar_reports para cada usuario que utilizaran el menú de Direccion de Recolección, seleccionando el checkbox en el usuario -> Permisos de acceso -> Otros
	""",
	'depends' : ["sale", "purchase",],
	'data' : ['views/sale_order.xml', 'views/purchase_order.xml', 'views/reports.xml', 'views/collection_address.xml',"security/groups.xml", "security/ir.model.access.csv","views/crm_helpdesk.xml", "views/dm_solar_reports_sequence.xml","views/crm_claim.xml", "views/collection_type.xml", "views/picking.xml"],#"views/res_partner.xml"],
    'installable': True,
    'auto_install': False,
}
