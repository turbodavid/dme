<html>
    <head>
    </head>
    <body>
        %for o in objects :
            <% setLang(user.lang) %>
            <div class="DivWordWrap Centrar Ancho1000">
                <table style="width: 100%;">
                    <tr>
                        <td style="width: 150px;">
                            ${helper.embed_image('jpeg',str(o.company_id.logo),180,auto)}
                        </td>                        
                        <td style="text-align: center; width: 450px;">
                            <table>
                                <tr>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 12pt; font-weight: bold; text-align: center;">
                                    	${o.company_id.name}
                                    </td>
                                </tr>
                                <tr style="vertical-align: top;">
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; width: 300px; vertical-align: top;">
                                        ${o.journal_id.partner_address_id.street or ''} ${o.journal_id.partner_address_id.l10n_mx_street3 or ''} ${o.journal_id.partner_address_id.l10n_mx_street4 or ''} COL. ${o.journal_id.partner_address_id.street2 or ''}, C.P. ${o.journal_id.partner_address_id.zip}
                                        ${o.journal_id.partner_address_id.city_id.name or ''}, ${o.journal_id.partner_address_id.state_id.name or ''} TELÉFONO(S) ${o.journal_id.partner_address_id.phone}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 9pt;">
                                        ${o.company_id.partner_id.regimen_fiscal_id and o.company_id.partner_id.regimen_fiscal_id.name or 'No identificado'}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 9pt;">
                                        R.F.C.: ${get_emitter_data(o.company_id.address_invoice_parent_company_id, 'vat')}
                                    </td>
                                </tr>
                            </table>
                        </td>
                        <td style="text-align: center; width: 250px;" colspan="2">
                            <table>
                                <tr>
                                    <td>
                                        <table style="vertical-align: top; text-align: center;border: 1px solid black;">
                                            <tr>
                                                <td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt;font-weight: bold;border-bottom:1pt solid black;">
                                                    UUID
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt;border-bottom:1pt solid black;">
                                                    ${o.cfdi_folio_fiscal or 'N/A'}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt;font-weight: bold;border-bottom:1pt solid black;">
                                                    Lugar y Fecha de Expedición
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt;border-bottom:1pt solid black;">
                                                    ${o.address_issued_id and o.address_issued_id.city and o.address_issued_id.state_id and o.address_issued_id.state_id.name or 'No identificado' }, A: ${o.date_invoice_tz or 'N/A'}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; color:red;">
                                                    ${o.internal_number}
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt;">
                        <td colspan="4">
                            <table style="border: 1px solid black; width:830px;">
                                <tr>
                                    <td>
                                        <table>
                                            <tr>
                                                <td style="font-weight:bold; ">
                                                    NOMBRE:
                                                </td>
                                                <td>
                                                    ${get_partner_data(o.partner_id, 'name')}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-weight:bold; ">
                                                    DOMICILIO:
                                                </td>
                                                <td>
                                                    ${get_partner_data(o.partner_id, 'street')} No. ${get_partner_data(o.partner_id, 'no_ext')} Int. ${get_partner_data(o.partner_id, 'no_int')}, ${get_partner_data(o.partner_id, 'suburb')},
                                                    ${get_partner_data(o.partner_id, 'city')}, ${get_partner_data(o.partner_id, 'state')}, ${get_partner_data(o.partner_id, 'county')}, C.P. ${get_partner_data(o.partner_id, 'zip')}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-weight:bold; ">
                                                    R.F.C.:
                                                </td>
                                                <td>
                                                    ${get_partner_data(o.partner_id, 'vat')}
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            <br />
                        </td>
                    </tr>
                   <tr>
                        <td colspan="4">
                            <table style="border: 1px solid black;">
                                <tr style="border-width: medium; font-family: Arial, Helvetica, sans-serif; font-size: 9pt; font-weight: bold; border-top-style: solid; border-bottom-style: solid;">
                                    <td style="width: 150px;">CANT.
                                    </td>
                                    <td style="width: 100px;">UNIDAD
                                    </td>
                                    <td style="width: 500px;">CONCEPTO
                                    </td>
                                    <td style="width: 100px;text-align: right;">P.UNITARIO
                                    </td>
                                    <td style="width: 150px; text-align: right;">IMPORTE
                                    </td>
                                </tr>
                                <tr>
                                    <td colspan="5">
                                        <hr noshade />
                                    </td>
                                </tr> 
                                 %for l in o.invoice_line:
                                <tr style="border-width: medium; font-family: Arial, Helvetica, sans-serif; font-size: 9pt;">
                                    <td>
                                        ${l.quantity or 'No identificado'} 
                                    </td>
                                    <td>
                                        ${(l.uos_id and l.uos_id.name) or 'No identificado' }
                                    </td>
                                    <td>
                                        ${ l.name or 'No identificado'}
                                    </td>
                                    <td style="text-align: right;";>
                                        ${ formatLang(l.price_unit) |entity }
                                    </td>
                                    <td style="text-align: right;";>
                                        ${ formatLang(l.quantity * l.price_unit) or formatLang(l.price_subtotal) }
                                    </td>
                                </tr>
                                %endfor
                                <tr>
                                    <td colspan="5">
                                        <br/>
                                        <br/>
                                        <br/>
                                        <br/>
                                        <br/>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                   <tr style="font-family: Arial, Helvetica, sans-serif; font-size:7pt;">
                        <td colspan="4">
                            <table style="border: 1px solid black; width:830px;">
                                <tr>
                                    <td style="font-weight: bold;">
                                        Observaciones:
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <div style="word-wrap: break-word; width: 700px;">
                                            ${o.comment or ''}
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                   </tr>
                   <tr style="font-family: Arial, Helvetica, sans-serif; font-size:7pt;">
                        <td colspan="4">
                            <table style="border: 1px solid black; width:830px">
                                <tr>
                                     <td style="font-weight: bold;font-size:8pt;">
                                        Cadena original del complemento de certificación digital del SAT:
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <div style="word-wrap: break-word; width: 800px;">
                                            ${ o.cfdi_cadena_original or 'N/A' }
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size:7pt;">
                        <td colspan="4">
                            <table style="border: 1px solid black; width:830px;">
                                <tr>
                                    <td style="font-weight: bold;font-size:8pt;">
                                        Sello Digital del CFDI:
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <div style="word-wrap: break-word; width: 800px;">
                                             ${ o.sello or 'No identificado' }
                                        </div>
                                    </td>
                                </tr>
                            </table>     
                        </td>
                    </tr>
                     <tr style="font-family: Arial, Helvetica, sans-serif; font-size:7pt;">
                        <td colspan="4">
                            <table style="border: 1px solid black; width:830px;">
                                 <tr>
                                     <td style="font-weight: bold;font-size:8pt;">
                                        Sello Digital del SAT:
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <div style="word-wrap: break-word; width: 800px;">
                                            ${ o.cfdi_sello or 'No identificado' }
                                        </div>
                                    </td>
                                </tr>
                            </table>     
                        </td>
                    </tr>
                    <tr>
                        <td colspan="4">
                            <table>
                                <tr align="right">
                                    <td>
                                        ${helper.embed_image('jpeg',qrcode(o),140)}
                                    </td>
                                    <td>
                                    	${helper.embed_image('jpeg', o.company_id.cif_file, 260)}
                                    </td>
                                    <td style="font-size:9pt;">
                                    	<table>
                                    		<tr>
                                     			<td style="font-weight: bold; width:200px;">
                                        			No. Certificado Digital:
                                    			</td>
                                    			<td colspan="2" colspan="2" style="width: 250px;">
                                        			${o.no_certificado or 'N/A'}
                                    			</td>                                    
                                				</tr>
                                				<tr>
                                          	<td style="font-weight: bold; width:200px;">
																Fecha y Hora de Certificación
                                             </td>
                                             <td colspan="2" colspan="2" style="width: 250px;">
                                                  ${(o.invoice_sequence_id.approval_id.type != 'cbb') and o.cfdi_fecha_timbrado or 'N/A'}
                                              </td>
                                          </tr>
                                    		<tr>
                                     			<td style="font-weight: bold; width:200px;">
                                        			No. Certificado Digital SAT:
                                    			</td>
                                    			<td colspan="2" colspan="2" style="width: 250px;">
                                        			${ o.cfdi_no_certificado or 'N/A' }
                                    			</td>
                                				</tr>
                                				<tr>
                                     			<td style="font-weight: bold; width:200px;">
                                        			Condiciones:
                                    			</td>
                                    			<td colspan="2" style="width: 250px;">
                                        			PAGO EN UNA SOLA EXHIBICION
                                    			</td>
                                				</tr>
                               				<tr>
                                     			<td style="font-weight: bold; width:200px;">
                                        			Método de Pago:
                                    			</td>
                                    			<td>
                                        			%if o.payment_type:
														%for payment in o.payment_type:	
															${payment.code}-${payment.name}
														%endfor
													%endif
													%if not o.payment_type:
														${_("99-Otros")}
													%endif
                                    			</td>
                                    			<td>
                                        			${o.partner_bank_id.acc_number  or ''}
                                    			</td>
                                				</tr>
                                    	</table>
                                    </td>
                                </tr>
                            </table>
                        </td>                        
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif;">
                    		<table style="border: 1px solid black; width:830px;">
                    			<tr>
                    				<td style="font-weight: bold;text-align:center; font-size:8pt;">
                    					<table style="width: 600px;">
                    						<tr>
                    							<td style="font-size: 10pt; font-weight: bold;">
                    								<div style="word-wrap: break-word;">
                    									${o.amount_to_text}
                                        	</div>
                    							</td>
                    						</tr>
                    						<tr>
                    							<td>
                    								Este documento es una representación impresa de un CFDI
                    							</td>
                    						</tr>
                    					</table>
		                    		</td>
		                    		<td align="right">
		                        	<table style="width: 230px;">
		                        		<tr>
		                        			<td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; font-weight: bold; text-align: right;">SubTotal: $</td>
		                        			<td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; text-align: right;">${formatLang(o.amount_untaxed) or '0.0'|entity}</td>
		                        		</tr>
		                        		%for tax in get_taxes(o):
		                    				<tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
		                        			<td style="font-weight: bold;text-align: right;">${tax[0]}: $</td>
		                        			<td style="text-align: right;">${formatLang(tax[1]) or '0.0'|entity}</td>
		                    				</tr>
		                    				%endfor
		                    				<tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;text-align: right;">
		                        			<td style="font-weight: bold;">Retenciones: $</td>
		                        			<td style="text-align: right;">
		                            		%for tax in get_taxes_ret(o):
		                                		${formatLang(tax[1]) or '0.0'|entity}
		                            		%endfor
		                        			</td>
		                    				</tr>
		                    				<tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; vertical-align: top;text-align: right;">
		                        			<td style="font-weight: bold;">TOTAL: $</td>
		                        			<td style="text-align: right;">${ formatLang(o.amount_total) | entity }</td>
		                    				</tr>
		                        	</table>
		                        </td>
                    			</tr>
                    			<tr>
                    				<td colspan="4">
                    					<table>
                    						<tr>
			                    				<td colspan="3" style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; vertical-align: top;text-align: left; font-weight: bold;">
			                    					Datos para pago Electrónico
			                    				</td>
			                    			</tr>
			                    			<tr>
			                    				<td colspan="3" style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; vertical-align: top;text-align: left;">
			                    					${o.company_id.name}
			                    				</td>
			                    			</tr>
			                    			%for b in o.company_id.bank_ids:
			                    			<tr>
			                    				<td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; vertical-align: top;text-align: left;">
			                    					${b.bank_name}
			                    				</td>
			                    				<td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; vertical-align: top;text-align: left;">
			                    					Cta: ${b.acc_number}
			                    				</td>
			                    				<td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; vertical-align: top;text-align: left;">
			                    					Clabe: ${b.clabe}
			                    				</td>
			                    			</tr>
			                    			%endfor
                    					</table>
                    				</td>
                    			</tr>
                    		</table>
						  </tr>
                </table>
            </div>
        %endfor
    </body>
    %if o.state == 'cancel':
    <div class="contenedor_cancelado">
        <div class="contenedor">
            ${_("CANCELED")}
        </div>
     </div>
    %endif    
</html>
