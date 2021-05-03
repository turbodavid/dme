# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#
#	 Coded By:
#	 	Cindy Yukie Ley Garcia cindy.ley@dmesoluciones.com
#	 	Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com
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
from openerp.osv import osv, fields
from openerp.tools.translate import _
class dm_solar_reports(osv.Model):
	_name = "dm.solar.reports"
	_auto = False # No genera los campos automaticos

	def init(self, cr):
		uid = 1 # Admin
		#===========================
		# Actualizamos res_country
		#===========================
		#crea objeto de pais
		#country_obj = self.pool.get('res.country')
		#obtiene el pais México se manda 1 que representa el UID Admin en init no se conoce
		#ids = country_obj.search(cr, uid, [('code', '=', 'MX'), ], limit=1)
		#Actualizamos el formato display_address a nivel registro
		#country_obj.write(cr, uid, ids, {'address_format': ' %(street)s %(l10n_mx_street3)s %(l10n_mx_street4)s %(street2)s %(city)s %(state_name)s %(zip)s'})

		#===========================
		# Actualizamos res_company
		#===========================
		#crea objeto company
		company_obj = self.pool.get('res.company')
		#obtiene todos las compañias
		ids = company_obj.search(cr, uid, [])
		for id in ids:
			company_obj.write(cr, uid, [id], {'rml_header': """ 
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
			"""})
