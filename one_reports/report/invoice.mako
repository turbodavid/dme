<html>
    <head>
    </head>
    <body>
        %for o in objects :
            <% setLang(user.lang) %>
            <div class="DivWordWrap Centrar Ancho1000">
                <table style="width: 100%;">
                    <tr>
                        <td rowspan="3" style="width: 250px;">
                            ${helper.embed_image('jpeg',str(o.company_id.logo),180,auto)}
                        </td>
                    </tr>
                    <tr>
                        <td colspan="4" style="font-family: Arial, Helvetica, sans-serif; font-size: 15pt; font-weight: bold; text-align: center;">${o.company_id.name}</td>
                    </tr>
                    <tr>
                        <td colspan="4" style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; font-weight: bold; text-align: center;" class="auto-style1">${o.company_id.website}</td>
                    </tr>
                    <tr>
                        <td rowspan="4" style="widht:500px">
                            <table>
                                <tr style="vertical-align: top;">
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; font-weight: bold; width:200px;">Domicilio fiscal
                                    </td>
                                    <td rowspan="2" style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; width: 300px; vertical-align: top;">
                                        ${get_emitter_data(o.company_id.address_invoice_parent_company_id, 'street')} No. Ext ${get_emitter_data(o.company_id.partner_id, 'no_ext')} ${get_emitter_data(o.company_id.address_invoice_parent_company_id, 'no_int')}
                                        ${get_emitter_data(o.company_id.address_invoice_parent_company_id, 'suburb')}
                                        ${get_emitter_data(o.company_id.address_invoice_parent_company_id, 'city')}
                                        ${_("State")} ${get_emitter_data(o.company_id.partner_id, 'state')} C.P. ${get_emitter_data(o.company_id.partner_id, 'zip')}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">${o.partner_id.ref or ''}</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
                        <td rowspan="3" style="width: 200px; text-align: center; vertical-align: top;"><b>Oficinas Ciudad de México</b>
                            <br />
                            Nuevo León 270 Piso 501 Condesa
                            Del. Cuauhtémoc, México, DF. CP.06140
                        </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
                        <td rowspan="2" style="width: 200px; text-align: center; vertical-align: top;"><b>Oficinas Querétaro</b>
                            <br />
                             Fray Sebastián de Aparicio 28 Planta Alta Climatorio
                            Santiago de Querétaro, Querétaro, 76030   
                        </td>
                    </tr>
                    <tr>
                        <td style="width: 200px; text-align: center;vertical-align: top;">
                            <table style="vertical-align: top; text-align: center;">
                                <tr>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; font-weight: bold;">Comprobante fiscal digital
                                    </td>
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
                    <tr>
						<td></td>
						<td></td>
						<td></td>
						<td></td>
                    </tr>
                    <tr>
								<td style="font-weight: bold; font-size: 12pt; font-family: Arial, Helvetica, sans-serif; text-align: center;">Tels. (667) 7157095, (667) 7164927</td>
                        <td style="font-weight: bold; font-size: 12pt; font-family: Arial, Helvetica, sans-serif; text-align: center;">Tels. (55) 43332084 - 87</td>
                        <td style="font-weight: bold; font-size: 12pt; font-family: Arial, Helvetica, sans-serif; text-align: center;">Tels. (442) 3845095</td>
                    </tr>
                    <tr>
						<td style="font-family: Arial, Helvetica, sans-serif; font-size: 9pt;" colspan="4">RÉGIMEN FISCAL: ${o.company_id.partner_id.regimen_fiscal_id and o.company_id.partner_id.regimen_fiscal_id.name or 'No identificado'}
						</td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold; background-color: #C0C0C0; color: #FFFFFF;">
                        <td colspan="2">
                            FACTURADO A:
                        </td>
                        <td style="text-align: center;">FECHA</td>
                        <td style="text-align: center;">EXPEDIDO EN</td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt;">
                        <td colspan="2" rowspan="4"  style="vertical-align: top;">
                            ${get_partner_data(o.partner_id, 'name')}
                            <br />
                            ${get_partner_data(o.partner_id, 'street')} Col. ${get_partner_data(o.partner_id, 'suburb')} No. ${get_partner_data(o.partner_id, 'no_ext')} ${get_partner_data(o.partner_id, 'no_int')}
                            ${get_partner_data(o.partner_id, 'city')}, ${get_partner_data(o.partner_id, 'state')}, C.P. ${get_partner_data(o.partner_id, 'zip')},${get_partner_data(o.partner_id, 'county')}, RFC: ${get_partner_data(o.partner_id, 'vat')}
                        </td>
                        <td style="text-align: center;">${o.date_invoice_tz or 'N/A'}</td>
                        <td style="text-align: center;">${o.address_issued_id and o.address_issued_id.city or 'No identificado'}, ${o.address_issued_id and o.address_issued_id.city and o.address_issued_id.state_id and o.address_issued_id.state_id.name or 'No identificado' }</td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold; background-color: #C0C0C0; color: #FFFFFF;">
                        <td style="text-align: center;">MÉTODO DE PAGO</td>
                        <td style="text-align: center;">MONEDA Y TIPO DE CAMBIO</td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">              
                        <td style="text-align: center;">
                            <table style="text-align: center; font-family: Arial, Helvetica, sans-serif; font-size: 10px;">
                                <tr>
                                    <td>
                                    	%if o.payment_type:
                                           %for payment in o.payment_type:	
                                               ${payment.name}
                                           %endfor
                                       %endif
                                       %if not o.payment_type:
                                           ${_("NA")}
                                       %endif
                                    </td>
                                </tr>
                            </table>
                        </td>
			<td style="text-align: center;">${o.currency_id.name or 'No identificado'} ${o.rate}</td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold; background-color: #C0C0C0; color: #FFFFFF;">
                        <td style="text-align: center;">CUENTA</td>
                        <td style="text-align: center;">FORMA DE PAGO</td>
                    </tr>
                    <tr>
                        <td colspan="2">
                            <table>
                                <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
                                    <td  style="font-weight: bold;">Enviar a:</td>
                                    <td colspan="5">${o.partner_id.email or ''}</td>
                                </tr>
                                <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
                                    <td style="width: 100px; font-weight: bold;">Condición:</td>
                                    <td style="width: 200px;">CRÉDITO</td>
                                    <td style="width: 100px;font-weight: bold;">O.C.</td>
                                    <td style="width: 100px;">${o.origin or ''}</td>
                                    <td style="width: 100px;font-weight: bold;">Vend.</td>
                                    <td style="width: 100px;">${o.user_id.name or ''}</td>
                                </tr>
                            </table>
                        </td>
                        <td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt;text-align: center;">${o.partner_bank_id.acc_number  or 'No identificado'}</td>
                        <td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold;text-align: center;">${_('Payment on a single display')}</td>
                    </tr>
                   <tr>
                        <td colspan="4">
                            <hr noshade />
                            <table>
                                <tr style="border-width: medium; font-family: Arial, Helvetica, sans-serif; font-size: 9pt; font-weight: bold; border-top-style: solid; border-bottom-style: solid;">
                                    <td style="width: 150px;">Cantidad
                                    </td>
                                    <td style="width: 100px;">Unidad
                                    </td>
                                    <td style="width: 150px;">Clave
                                    </td>
                                    <td style="width: 500px;">Descripción
                                    </td>
                                    <td style="width: 100px;text-align: right;">P/U
                                    </td>
                                    <td style="width: 150px; text-align: right;">Importe
                                    </td>
                                </tr>
                                <tr>
                                    <td colspan="6">
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
                                        ${ l.product_id and l.product_id.default_code or 'No identificado'}
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
                                    <td colspan="6">
                                        <hr noshade />
                                    </td>
                                </tr> 
                                <tr>
                                    <td colspan="2" rowspan="4">
                                        ${helper.embed_image('jpeg',qrcode(o),140)}
                                    </td>
                                    <td colspan="2" rowspan="4" style="text-align: left;">
                                        <b>SON: ${o.amount_to_text}</b>
                                    </td>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; font-weight: bold;text-align: right;">${_("SUBTOTAL")}: $</td>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; text-align: right;">${formatLang(o.amount_untaxed) or '0.0'|entity}</td>
                                </tr>
                                %for tax in get_taxes(o):
                                <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
                                    <td style="font-weight: bold;text-align: right;">${tax[0]}: $</td>
                                    <td style="text-align: right;">
										${formatLang(tax[1]) or '0.0'|entity}
                                    </td>
                                </tr>
                                %endfor
                                <tr>
                                    <td colspan="2">
                                        <hr noshade />
                                    </td>
                                </tr> 
                                <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; vertical-align: top;">
                                    <td style="font-weight: bold;">${_("TOTAL")}: $</td>
                                    <td style="text-align: right;">
                                        ${ formatLang(o.amount_total) | entity }
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt;">
                        <td colspan="4">
                            ${_("This document is a printed representation of a CFDI")}:
                        </td>
                    </tr>
                     <tr style="font-family: Arial, Helvetica, sans-serif; font-size:10pt;">
                        <td style="font-weight: bold;">
                           ${_("Número de Factura (UUID)")}:
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
                    BANAMEX MXN
                </td>
                <td>
                    Cta. 7705347/441
                </td>
                <td> Clabe:</td>
                <td>002730044177053476</td>
            </tr>
            <tr style="font-weight: bold; font-size:12pt;">
                <td>
                    BANAMEX USD
                </td>
                <td>
                    Cta. 9197403/441
                </td>
                <td> Clabe:</td>
                <td>002730044191974036</td>
            </tr>
            <tr>
                <td colspan="4">
                    <br />
                </td>
            </tr>
            <tr>
                <td colspan="3" style="font-weight: bold;text-align:right;">
                    PAGARÉ
                </td>
                <td>
                    ${o.internal_number}
                </td>
            </tr>
            <tr>
                <td colspan="4">
                    <br />
                </td>
            </tr>
            <tr>
                <td colspan="4">
                    <div style="width: 915px; word-wrap: break-word;">
						Por este PAGARE reconozco deber y me obligo a pagar en esta ciudad de Culiacan, Sinaloa o en cualquier otra donde se me requiera de pago a <b>${o.company_id.name}</b>, a su orden el día <b>${o.date_due}</b>, la Cantidad de <b>(${o.amount_to_text})</b>
                    </div>
                </td>
            </tr>
            <tr>
                <td colspan="4"></td>
                    <br/>
            </tr>
            <tr>
                <td colspan="4">
                    <div style="width: 915px; word-wrap: break-word;">
						Valor recibido a mi entera satisfacción. Este PAGARE es Mercantil y esta regido por la Ley General de Títulos y Operaciones de Crédito en su Art.173, parte final, y sus correlativos por no ser PAGARE domiciliado. De no verificarse el pago de la cantidad que este PAGARE expresa el día de su vencimiento, abonare el CREDITO el % mensual por todo el tiempo que este insoluble sin perjuicio al cobro mas gastos que por ello se originen. <b>${o.company_id.name}</b> se reserva el derecho de cobrar el 20% sobre el importe de cada cheque devuelto en los términos del Art. 193 de la Ley General de Títulos y Operaciones de Crédito.
                    </div>                
                </td>
            </tr>
            <tr>
                <td colspan="4">
					LA REPRODUCCION NO AUTORIZADA DE ESTE COMBROBANTE CONSTITUYE UN DELITO EN LOS TERMINOS DE LAS DISPOSICICIONES FISCALES.
                </td>
                    <br/>
                    <br/>
            </tr>
            <tr>
                <td colspan="2" rowspan="2">
                    ${get_partner_data(o.partner_id, 'name')}
                    <br />
                    ${get_partner_data(o.partner_id, 'street')} ${get_partner_data(o.partner_id, 'street')} No. ${get_partner_data(o.partner_id, 'no_ext')} ${get_partner_data(o.partner_id, 'no_int')}
                    <br />
                    ${get_partner_data(o.partner_id, 'city')}, ${get_partner_data(o.partner_id, 'state')}, ${get_partner_data(o.partner_id, 'county')}
                </td>
                <td colspan="2"></td>
            </tr>
            <tr>
                <td colspan="2" style="text-align:center;">
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
