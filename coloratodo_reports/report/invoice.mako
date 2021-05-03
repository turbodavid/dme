<html>
    <head>
    </head>
    <body>
        %for o in objects :
            <% setLang(user.lang) %>
            <div class="DivWordWrap Centrar Ancho1000">
                <table style="width: 100%;">
                    <tr>
                        <td style="width: 150px">
                            ${helper.embed_image('jpeg',str(o.company_id.logo),180,auto)}
                        </td>                        
                        <td style="text-align: center; width: 450px">
                            <table>
                                <tr>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 12pt; font-weight: bold; text-align: center;">${o.company_id.name}</td>
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
                                                    %if o.type == 'out_invoice':
                                                        UUID - FACTURA
                                                    %else:
                                                        UUID - NOTA DE CREDITO
                                                    %endif
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt;border-bottom:1pt solid black;">
                                                    ${o.cfdi_folio_fiscal or 'N/A'}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt;font-weight: bold;border-bottom:1pt solid black;">
                                                    Fecha y Hora de Certificación
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt;border-bottom:1pt solid black;">
                                                    ${(o.invoice_sequence_id.approval_id.type != 'cbb') and o.cfdi_fecha_timbrado or 'N/A'}
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
                            <table style="border: 1px solid black; width:830px">
                                <tr>
                                    <td>
                                        <table>
                                            <tr>
                                                <td style="font-weight:bold; ">
                                                    NOMBRE:
                                                </td>
                                                <td>
                                                %if o.partner_id.parent_id.name:
                                                    ${o.partner_id.parent_id.name}
                                                %else:
                                                    ${o.partner_id.name}
                                                %endif
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-weight:bold; ">
                                                    DOMICILIO:
                                                </td>
                                                <td>
                                                  ${o.partner_id.street or ''} No. ${o.partner_id.l10n_mx_street3 or ''} ${o.partner_id.l10n_mx_street4 or ''} COL. ${o.partner_id.street2 or ''}
                                                  ${o.partner_id.city_id.name or ''}, ${o.partner_id.state_id.name or ''}, C.P.${o.partner_id.zip or ''}, RFC ${o.partner_id.vat_split or ''}
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
                                    <td style="width: 150px">CANT.
                                    </td>
                                    <td style="width: 100px">UNIDAD
                                    </td>
                                    <td style="width: 500px">CONCEPTO
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
                   <tr style="font-family: Arial, Helvetica, sans-serif; font-size:7pt">
                        <td colspan="4">
                            <table style="border: 1px solid black; width:830px">
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
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size:7pt">
                        <td colspan="4">
                            <table style="border: 1px solid black; width:830px">
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
                     <tr style="font-family: Arial, Helvetica, sans-serif; font-size:7pt">
                        <td colspan="4">
                            <table style="border: 1px solid black; width:830px">
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
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size:7pt">
                        <td colspan="4">
                            <table style="border: 1px solid black; width:830px">
                                 <tr>
                                     <td style="font-weight: bold;font-size:8pt;">
                                        Cantidad con Letra:
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <div style="word-wrap: break-word; width: 800px;">
                                            ${o.amount_to_text}
                                        </div>
                                    </td>
                                </tr>
                            </table>     
                        </td>
                    </tr>
                    <tr>
                        <td colspan="4">
                            <table>
								<tr>
									<td rowspan="5">
                                        ${helper.embed_image('jpeg',qrcode(o),140)}
                                    </td>
                                    <td align="center" rowspan="5" style="font-family: Arial, Helvetica, sans-serif; font-size: 6.6pt; font-weight: bold; width:550px;text-align: justify;">
                                        <div style="width: 300px;">
											Por este pagare reconozco deber y me obligo a pagar en esta ciudad
											Guamuchil, Sinaloa o en cualquier otra donde se me requiera
											de pago a <b>${o.company_id.name}</b> a su orden al dia <b>${o.date_due}</b>,
											la cantidad de <b>(${o.amount_to_text})</b>. Valor recibido a mi 
											entera satisfaccion. Este PAGARE es mercantil y esta regido por la Ley
											General de Titulos y Operaciones de Credito en su ART.173, parte final
											y sus correlativos por no ser PAGARE domiciliado.<br>
											<br>
											<br>
											<div style="text-align: center; font-size; 2pt: font-family: Arial, Helvetica, sans-serif;">
												<hr style="background-color: black; height: 1px;" />
												NOMBRE Y FIRMA
											</div>
                                        </div>
                                    </td>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; text-align: right;">Importe: $</td>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; text-align: right;">
                                    	<%
                                    		total = 0.0
                                    	%>
                                    	%for l in o.invoice_line:
                                    	<%
                                    		total = total + (l.price_unit * l.quantity)
                                    	%>
                                    	%endfor
                                    	${formatLang(total) or '0.0' | entity} 
                                    </td>
								</tr>
                                <tr>                                    
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; text-align: right;">Descuento:$</td>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; text-align: right; width: 50px;">
                                    	<%
                                    		descuento = 0.0
                                    	%>
                                    	%for x in o.invoice_line:
                                    	<%
                                    		descuento =  descuento + ((x.price_unit * x.quantity) * (x.discount/100))
                                    	%>
                                    	%endfor
                                    	${formatLang(descuento) or '0.0' | entity}
                                    </td>
                                </tr>
                                <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;text-align: right;">
                                    <td>Subtotal: $</td>
                                    <td style="text-align: rigth; width: 50px">
										${formatLang(o.amount_untaxed) or '0.0' | entity}
                                    </td>
                                </tr>
                                <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;text-align: right; 60px">
                                    <td>Iva 16%: $</td>
                                    <td style="text-align: right;">
										%for tax in get_taxes(o):
											${formatLang(tax[1]) or '0.0' | entity}
										%endfor
                                    </td>
                                </tr>
                                <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; vertical-align: top;text-align: right;">
                                    <td style="font-weight: bold;">TOTAL: $</td>
                                    <td style="text-align: rigth; width: 50px">
                                        ${ formatLang(o.amount_total) | entity }
                                    </td>
                                </tr>
                            </table>
                        </td>                        
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size:8pt">
                        <td colspan="4">
                            <table style="border: 1px solid black; width:830px">
                            %if o.type == 'out_invoice':
                                 <tr>
                                     <td style="font-weight: bold;" colspan="5">
                                        En caso de transferencia o depósito, favor de utilizar siempre esta referencia en el banco de su elección:
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
                            %endif
                            </table>     
                        </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size:8pt">
                        <td colspan="4">
                            <table style="border: 1px solid black; width:830px">
                                 <tr>
                                     <td style="font-weight: bold; width:200px;">
                                        No. Certificado Digital SAT:
                                    </td>
                                    <td colspan="2">
                                        ${ o.cfdi_no_certificado or 'N/A' }
                                    </td>
                                </tr>
                                <tr>
                                     <td style="font-weight: bold; width:200px;">
                                        Forma de Pago:
                                    </td>
                                    <td colspan="2">
                                        PAGO EN UNA SOLA EXHIBICION
                                    </td>
                                </tr>
                                <tr>
                                     <td style="font-weight: bold; width:200px;">
                                        No. Certificado Digital:
                                    </td>
                                    <td colspan="2">
                                        ${o.no_certificado or 'N/A'}
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
											${_("NA")}
										%endif
									</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: bold; width:200px;">
                                        Cuenta Bancaria:
                                    </td>
                                    <td>
                                        ${o.partner_bank_id.acc_number or ''}
                                    </td>
                                </tr>
                              <tr style="font-family: Arial, Helvetica, sans-serif; font-size:8pt;">
                                    <td colspan="3" style="font-weight: bold;text-align:center">
                                        
                                    </td>
                                </tr>
                            </table>     
                        </td>
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
