<html>
    <head>
		<style type="text/css">
			${css}
		</style>
    </head>
    <body>
        %for o in objects :
            <% setLang(user.lang) %>
            <div class="DivWordWrap Centrar Ancho1000">
                <table style="width: 100%;">
                    <tr>
                        <td rowspan="3" style="width: 250px">
                            ${helper.embed_image('jpeg',str(o.company_id.logo),180,auto)}
                        </td>
                    </tr>
                    <tr>
                        <td colspan="4" style="font-family: Arial, Helvetica, sans-serif; font-size: 15pt; font-weight: bold; text-indent: 150px;">TECNIKA GLOBAL, S.A. DE C.V.
                        </td>
                    </tr>
                    <tr>
                        <td colspan="4" style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; font-weight: bold; text-indent: 245px;" class="auto-style1">TECNIKA.COM.MX</td>
                    </tr>
                  <!--   <tr>
                        	<td rowspan="5" style="widht:500px">
                            
		                                <tr style="vertical-align: top;">
		                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; font-weight: bold; width:200px;">Domicilio fiscal
		                                    </td>
		                                    <td rowspan="2" style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; width: 300px; vertical-align: top;">
		                                        ${get_emitter_data(o.company_id.address_invoice_parent_company_id, 'street')} No. Ext ${get_emitter_data(o.company_id.partner_id, 'no_ext')} Int ${get_emitter_data(o.company_id.address_invoice_parent_company_id, 'no_int')}
		                                        ${_("City")} ${get_emitter_data(o.company_id.address_invoice_parent_company_id, 'city')} 
		                                        ${_("State")} ${get_emitter_data(o.company_id.partner_id, 'state')}
		                                    </td>
		                                </tr>
		                    </td>
		                </tr>
                        	<tr>
                               <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt">${o.partner_id.ref or 'Sin Referencia'}</td>
                            </tr> -->
                            </table>
                            </div>
                 	<tr>
                    	<td colspan="3">
							
                    		<table>
                    			<tr>
                    					
			                    	<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt;">
			                        	<table style="width: 100%;">
			                        			<tr>
							                        <td style="width: 180px; text-align: center; vertical-align: top;"><b>Culiacán</b>
							                            <br />
							                            CALLE: PALIZA No.402 SUR COL. MIGUEL ALEMAN,
							                            CP.80200, CULIACAN, SINALOA, MEXICO.
							                            (667)7124444
							                        </td>
							                        <td style="width: 180px; text-align: center; vertical-align: top;"><b>Los Mochis</b>
							                            <br />
							                            GUILLERMO PRIETO #102 NTE.
							                            COL. CENTRO, LOS MOCHIS, SINALOA, MEXICO.
							                            (668)8188050
							                        </td>
							                        <td style="width: 180px; text-align: center; vertical-align: top;"><b>Mazatlán</b>
							                            <br />
							                            JUVENTINO ROSAS #108
							                            COL. REFORMA, MAZATLAN, SINALOA, MEXICO.
							                            (669)9300200
								                        </td>
							                        <td style="width: 180px; text-align: center; vertical-align: top;"><b>Guamúchil</b>
							                            <br />
							                            N. BRAVO Y V. GUERRERO #77-F
							                            COL. CENTRO, GUAMUCHIL, SINALOA, MEXICO.
							                            (673)7323170
							                        </td>
							                        <td style="width: 180px; text-align: center; vertical-align: top;"><b>Ciudad de México</b>
							                            <br />
							                            C. EMPRESA #146 INT. 003 ESQ. CADIZ,
							                            COL. EXTREMADURA INSURGENTES, DEL. BENITO JUAREZ,
							                            01(55)66508840
						                        	</td>
						                        	<td style="width: 180px; text-align: center; vertical-align: top;">
							                            <table style="vertical-align: top; text-align: center;">
							                                <tr>
							                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold;">Comprobante fiscal digital</td>
							                                </tr>
							                                <tr>
							                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold;">SERIE Y FOLIO</td>
							                                </tr>
							                                <tr>
							                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 12pt; font-weight: bold;">${o.internal_number}</td>
							                                </tr>
							                                <tr>
							                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; font-weight: bold;">${get_emitter_data(o.company_id.address_invoice_parent_company_id, 'vat')}</td>
							                                </tr>
							                            </table>
			                       					 </td>
						                    	</tr>
			                        	</table>
			                        </td>
			                    </tr>
			                </table>
			            </td>
			                        
                    </tr>
                    <table>
                    <tr>
                        <td colspan="2">
                            <table>
                                <tr>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 9pt;">RÉGIMEN FISCAL
                                    </td>
                                    <td nowrap style="font-family: Arial, Helvetica, sans-serif; font-size: 9pt;">
                                        ${o.company_id.partner_id.regimen_fiscal_id and o.company_id.partner_id.regimen_fiscal_id.name or 'No identificado'}
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold; background-color: #C0C0C0; color: #FFFFFF;">
                        <td colspan="2" style="width:800px;">
                            FACTURADO A:
                        </td>
                        <td style="width:200px;text-align: center">FECHA</td>
                        <td style="width:200px;text-align: center">EXPEDIDO EN</td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
                        <td colspan="2" rowspan="4"  style="vertical-align: top;">
							<b>
							%if o.partner_id.function:
								${o.partner_id.function}
							%else:
								%if o.partner_id.parent_id:
									${o.partner_id.parent_id.name}
								%else:
									${o.partner_id.name}
								%endif
							%endif
							<br/>
							${o.partner_id.street or ''} No. ${o.partner_id.l10n_mx_street3 or ''} ${o.partner_id.l10n_mx_street4 or ''} COL. ${o.partner_id.street2 or ''}</br>
							${o.partner_id.city_id.name or ''}, ${o.partner_id.state_id.name or ''}, C.P.${o.partner_id.zip or ''}, RFC ${o.partner_id.vat_split or ''}
                        	</b>
                        </td>
                        <td style="text-align: center">${o.date_invoice_tz or 'N/A'}</td>
                        <td style="text-align: center">${o.address_issued_id and o.address_issued_id.city and o.address_issued_id.state_id and o.address_issued_id.state_id.name or 'No identificado' }</td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold; background-color: #C0C0C0; color: #FFFFFF;">
                        <td style="width:200px;text-align: center">MÉTODO DE PAGO</td>
                        <td style="width:200px;text-align: center">MONEDA Y TIPO DE CAMBIO</td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
                        <td style="text-align: center">
							%if o.payment_type:
								%for payment in o.payment_type:	
									${payment.name}
								%endfor
							%endif
							%if not o.payment_type:
								${_("NA")}
							%endif
                        </td>
                        <td style="text-align: center">
                            <table style="text-align: center; font-family: Arial, Helvetica, sans-serif; font-size: 10px;">
                                <tr>
                                    <td style= "position:relative; left: 55pt;">
                                        ${o.currency_id.name  or 'No Identificado'} ${o.rate}
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold; background-color: #C0C0C0; color: #FFFFFF;">
                        <td style="text-align: center">CUENTA</td>
                        <td style="text-align: center">FORMA DE PAGO</td>
                    </tr>
                    <tr>
                        <td colspan="2">
                            <table>
                             
                                <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
                                    <td style="width: 40px; font-weight: bold;">Condición:</td>
                                    <td style="width: 70px">${o.payment_term.name or ''}</td>
                                    <td style="width: 40px;font-weight: bold">P.V.</td>
                                    <td style="width: 200px;">${o.origin or ''}</td>
                                     <td style="width: 40px;font-weight: bold">O.C.</td>
                                    <td style="width: 200px;">${o.name or ''}</td>
                                    <td style="width: 40px;font-weight: bold">Vend.</td>
                                    <td style="width: 160px">${o.user_id.name}</td>
                                </tr>
                            </table>
                        </td>
                        <td style="width:200px; font-family: Arial, Helvetica, sans-serif; font-size: 8pt;text-align: center;">${o.partner_bank_id.acc_number  or 'No Aplica'}</td>
                        <td style="width:200px; font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold;text-align: center;">${_('Payment on a single display')}</td>
                    </tr>
				</table> <!--PRuebas-->
				
				<div class="act_as_table">
					<div class="act_as_row">
						<div class="act_as_cell" style="width:90px; border-width: 2px; font-family: Arial, Helvetica, sans-serif; font-size: 12pt; font-weight: bold; border-top-style: solid; border-bottom-style: solid;">
							<b>Cantidad</b>
						</div>
						<div class="act_as_cell" style="width:60px; border-width: 2px; font-family: Arial, Helvetica, sans-serif; font-size: 12pt; font-weight: bold; border-top-style: solid; border-bottom-style: solid;">
							<b>Pieza</b>
						</div>
						<div class="act_as_cell" style="width:150px; border-width: 2px; font-family: Arial, Helvetica, sans-serif; font-size: 12pt; font-weight: bold; border-top-style: solid; border-bottom-style: solid;">
							<b>Clave</b>
						</div>
						<div class="act_as_cell" style="width:600px;border-width: 2px; font-family: Arial, Helvetica, sans-serif; font-size: 12pt; font-weight: bold; border-top-style: solid; border-bottom-style: solid;">
							<b>Descripcion</b>
						</div>
						<div class="act_as_cell" style="border-width: 2px; font-family: Arial, Helvetica, sans-serif; font-size: 12pt; font-weight: bold; border-top-style: solid; border-bottom-style: solid; text-align: right">
							<b>P/U</b>
						</div>
						<div class="act_as_cell" style="border-width: 2px; font-family: Arial, Helvetica, sans-serif; font-size: 12pt; font-weight: bold; border-top-style: solid; border-bottom-style: solid; text-align: right">
							<b>Importe</b>
						</div>
					</div>
					%for l in o.invoice_line:
					<div class="act_as_row">
						<div class="act_as_cell" style="font-size: 10pt;">
							${l.quantity or 'No identificado'} 
						</div>
						<div class="act_as_cell" style="font-size: 10pt;">
							${(l.uos_id and l.uos_id.name) or 'No identificado' }
						</div>
						<div class="act_as_cell" style="font-size: 10pt;">
							${ l.product_id and l.product_id.default_code or 'No identificado'}
						</div>
						<div class="act_as_cell" style="font-size: 10pt;">
							${ l.name or 'No identificado'}
						</div>
						<div class="act_as_cell" style="text-align: right; font-size: 10pt;">
							${ formatLang(l.price_unit_without_taxes) |entity }
						</div>
						<div class="act_as_cell" style="text-align: right; font-size: 10pt;">
							${ formatLang(l.price_subtotal, digits=2) }
						</div>
					</div>
					%endfor
				</div>
				<table style="width: 100%;"><!--preubs-->
					<tr>
							<td colspan="2">
									<tr>
										<td colspan="6">
											<hr noshade />
										</td>
									</tr>
									<tr>
										<td colspan="2" rowspan="4">
											${helper.embed_image('jpeg',qrcode(o),140)}
										</td>
										<td colspan="2" rowspan="2" style="text-align: center; font-size: 8pt;">
											<b>Observaciones</br>${o.comment or ''}</b>
										</td>
										<td NOWRAP style="width:120px; font-family: Arial, Helvetica, sans-serif; font-size: 9pt; font-weight: bold; text-align: left; ">${_("SUBTOTAL")}: $</td>
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 9pt; text-align: right;">${formatLang(o.amount_untaxed,digits=2) or '0.0'|entity}</td>
									</tr>
									<tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
										<td style="width:120px;font-weight: bold;">IVA: $</td>
										<td style="text-align: right;">
											%for tax in get_taxes(o):
												${formatLang(tax[1],digits=2) or '0.0'|entity}
											%endfor
										</td>
									</tr>
									<tr>
										<td colspan="2" rowspan="2" style="text-align: center;">
											<b>${o.amount_to_text}</b>
										</td>
										<td colspan="2">
											<hr noshade />
										</td>
									</tr> 
									<tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; vertical-align: top;">
										<td style="width:150px;font-weight: bold;">${_("TOTAL")}: $</td>
										<td style="text-align: right;">
											${ formatLang(o.amount_total,digits=2) | entity }
										</td>
									</tr>
							</td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
                        <td colspan="4">
                            ${_("This document is a printed representation of a CFDI")}
                        </td>
                    </tr>
                     <tr style="font-family: Arial, Helvetica, sans-serif; font-size:10pt;">
                        <td style="font-weight: bold;">
                            ${_("INVOICE NUMBER")}(UUID):
                        </td>
                         <td colspan="3">
                            ${o.cfdi_folio_fiscal or 'N/A'}
                         </td>
                    </tr>
                     <tr style="font-family: Arial, Helvetica, sans-serif; font-size:10pt;">
                        <td style="font-weight: bold;">
                            ${_("DATE AND TIME OF CERTIFICATION")}:
                        </td>
                         <td colspan="3">
                            ${(o.invoice_sequence_id.approval_id.type != 'cbb') and o.cfdi_fecha_timbrado or 'N/A'}
                         </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size:10pt;">
                        <td style="font-weight: bold;">
                            ${_("DIGITAL STAMP ISSUER")}
                        </td>
                         <td colspan="3">
                             <div style="width: 650px; word-wrap: break-word;">
                                ${ o.sello or 'No identificado' }
                            </div>                           
                         </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size:10pt;">
                        <td colspan="2" style="font-weight: bold;">
                          ${_("CERTIFICATE NO. SERIAL ISSUER")}:
                        </td>
                         <td colspan="2" style="font-weight: bold;">
                             ${_("CERTIFICATE NO. SERIAL SAT")}:
                         </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size:10pt;">
                        <td colspan="2">
                            ${o.no_certificado or 'N/A'}
                        </td>
                         <td colspan="2">
                             ${ o.cfdi_no_certificado or 'N/A' }
                         </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size:10pt;">
                        <td colspan="4" style="font-weight: bold;">
                           CADENA ORIGINAL DEL COMPLEMENTO DE CERTIFICACION DIGITAL DEL SAT:
                        </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size:10pt;">
                        <td colspan="4">
                            <div style="width: 915px; word-wrap: break-word;">
                                ${ o.cfdi_cadena_original or 'N/A' }
                            </div>
                        </td>
                    </tr>
                   <tr style="font-family: Arial, Helvetica, sans-serif; font-size:10pt;">
                        <td colspan="4" style="font-weight: bold;">
                           ${_("STAMP DIGITAL SAT")}:
                        </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size:10pt;">
                        <td colspan="4">
                            <div style="width: 915px; word-wrap: break-word;">
                                 ${ o.cfdi_sello or 'No identificado' }
                            </div>
                        </td>
                    </tr>                    
                </table>
         </div>
        %endfor
    </body>
    <footer>
        <table style="width: 100%; font-family: Arial, Helvetica, sans-serif; font-size:10pt;">
            <tr style="font-weight: bold; font-size:12pt;">
                <td>
                    Datos Para Pago Electronico
                </td>
            </tr>
            <tr style="font-weight: bold; font-size:12pt;">
                <td>
                    BANAMEX
                </td>
                <td>
                    Cta. 17671 Sucl. 4404
                </td>
                <td> Clabe:</td>
                <td>002730440400176718</td>
            </tr>
            <tr style="font-weight: bold; font-size:12pt;">
                <td>
                    SANTANDER
                </td>
                <td>
                    Cta. 65-504017732
                </td>
                <td> Clabe:</td>
                <td>014730655040177329</td>
            </tr>
            <tr style="font-weight: bold; font-size:12pt;">
                <td>
                    BANAMEX DOLARES
                </td>
                <td>
                    Cta. 9000495 Sucl. 4170
                </td>
                <td> Clabe:</td>
                <td>002730417090004951</td>
            </tr>
<!--
            <tr>
                <td colspan="4">
                    <br />
                </td>
            </tr>
-->
            <tr>
                <td colspan="3" style="font-weight: bold;text-align:right;">
                    PAGARÉ
                </td>
                <td>
                    ${o.internal_number}
                </td>
            </tr>
<!--
            <tr>
                <td colspan="4">
                    <br />
                </td>
            </tr>
-->
            <tr>
                <td colspan="4">
                    <div style="width: 100%; word-wrap: break-word; text-align: justify;">
                        POR ESTE PAGARE DEBO (EMOS) Y PAGARÉ(MOS) INCONDICIONALMENTE A LA ORDEN DE TECNIKA GLOBAL, S.A. DE C.V. EN CULIACAN, SINALOA EL DIA <b>${get_date_invoice(o)}</b> LA CANTIDAD DE: <b>${o.amount_to_text}</b>
                    </div>
                </td>
            </tr>
            <tr>
                <td colspan="4"></td>
                    <br/>
            </tr>
            <tr>
                <td colspan="4">
                    <div style="width: 100%; word-wrap: break-word; text-align: justify;">
                        QUE RECONOZCO ADEUDARLE, VALOR RECIBIDO A MI (NUESTRA) ENTERA SATISFACCION. QUEDA EXPRESAMENTE CONVENIDO QUE DE NO PAGARSE A SU VENCIMIENTO ESTE DOCUMENTO HASTA EL DIA DE SU LIQUIDACION, CAUSARA INTERESES MORATORIOS AL TIPO DE 10% MENSUAL PAGADERO EN ESTA CIUDAD JUNTAMENTE CON EL PRINCIPAL. Y QUE SOMETO A LA COMPETENCIA DE LOS TRIBUNALES Y JUECES DE ESTA CIUDAD CULIACAN, SINALOA A <b>${get_date_invoice(o)}</b>
                    </div>                
                </td>
            </tr>
            <tr>
                <td colspan="4"></td>
<!--
                </br>
                </br>
-->
            </tr>
            <tr>
                <td colspan="2" rowspan="2">
                    %if o.partner_id.function:
						${o.partner_id.function}
					%else:
						${o.partner_id.parent_id.name}
					%endif
                    <br />
						${o.partner_id.street} No. ${o.partner_id.l10n_mx_street3 or ''} ${o.partner_id.l10n_mx_street4 or ''} COL. ${o.partner_id.street2}</br>
						${o.partner_id.city_id.name}, ${o.partner_id.state_id.name}, C.P.${o.partner_id.zip}, RFC ${o.partner_id.vat_split}  
                </td>
                <td colspan="2"></td>
            </tr>
            <tr>
                <td colspan="2" style="text-align:center">
                     <hr />
                     NOMBRE Y FIRMA
                </td>
            </tr>
        </table>
    </footer>
     %if o.state == 'cancel':
    <div class="contenedor_cancelado">
        <div class="contenedor">
            ${_("CANCELED")}
        </div>
     </div>
     
    %endif    
</html>
