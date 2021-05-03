<html>
    <head>
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
                        <td colspan="3" style="font-family: Arial, Helvetica, sans-serif; font-size: 13pt; font-weight: bold; text-align: center;">${o.company_id.name}</td>
                    </tr>
                    <tr>
                        <td colspan="3" style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; font-weight: bold; text-align: center;" class="auto-style1">${o.company_id.website}</td>
                    </tr>
                    <tr>
                        <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10px; width:250px;vertical-align: top;"><b>Domicilio Fiscal</b>
							<br />
							${get_emitter_data(o.company_id.address_invoice_parent_company_id, 'street')} No. Ext ${get_emitter_data(o.company_id.partner_id, 'no_ext')} Int ${get_emitter_data(o.company_id.address_invoice_parent_company_id, 'no_int')}
							${_("City")} ${get_emitter_data(o.company_id.address_invoice_parent_company_id, 'city')} 
							${_("State")} ${get_emitter_data(o.company_id.partner_id, 'state')}
							${o.partner_id.ref or 'Sin Referencia'}
                        </td>
                        <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10px; width:225px;vertical-align: top;text-align: center;"><b>Oficinas DF</b>
                            <br />
                            Nuevo León 270 Piso 501 Condesa
                            Del. Cuauhtémoc, México, DF. CP.06140
                        </td>
                         <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10px; width:225px;vertical-align: top;text-align: center;"><b>Oficinas Culiacán</b>
                            <br />
                            Paliza Sur 288 Jorge Almada
                            Culiacán, Sinaloa, 80200
                        </td>
                         <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10px; width:300px;vertical-align: top;text-align: center;"><b>Oficinas Querétaro</b>
                            <br />
                            Fray Sebastián de Aparicio 28 Planta Alta Climatorio
                            Santiago de Querétaro, Querétaro, 76030         
                        </td>
                    </tr>
                    <tr>
						<td colspan="4"></td>					
                    </tr>
                    
                    <tr>
                        <td></td>
                        <td style="font-weight: bold; font-size: 11px; font-family: Arial, Helvetica, sans-serif; text-align: center;">Tels. 55.43332084-87</td>
                        <td style="font-weight: bold; font-size: 11px; font-family: Arial, Helvetica, sans-serif; text-align: center;">Tels. 667.7157095, 7164927</td>
                        <td style="font-weight: bold; font-size: 11px; font-family: Arial, Helvetica, sans-serif; text-align: center;">Tels.442. 3845095</td>
                    </tr>
                    <tr><!--Regimen Fiscal-->
                        <td colspan="4">
                            <table>
                                <tr>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 9px;">RÉGIMEN FISCAL
                                    </td>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 9px;">
                                        ${o.company_id.partner_id.regimen_fiscal_id and o.company_id.partner_id.regimen_fiscal_id.name or 'No identificado'}
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr><!--Fin Regimen Fiscal-->
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold; background-color: #C0C0C0; color: #FFFFFF;"><!--Facturado Etiqueta-->
                        <td colspan="2">
                            FACTURADO A:
                        </td>
                        <td style="text-align: center">FECHA</td>
                        <td style="text-align: center">EXPEDIDO EN</td>
                    </tr><!--Fin Facturado Etiqueta-->
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt;"> <!--Facturado Datos-->
                        <td colspan="2" rowspan="4"  style="vertical-align: top;">
                            ${get_partner_data(o.partner_id, 'name')}
                            <br />
                            ${get_partner_data(o.partner_id, 'street')} ${get_partner_data(o.partner_id, 'street')} No. ${get_partner_data(o.partner_id, 'no_ext')} Int. ${get_partner_data(o.partner_id, 'no_int')}
                            ${get_partner_data(o.partner_id, 'city')}, ${get_partner_data(o.partner_id, 'state')}, ${get_partner_data(o.partner_id, 'county')}, RFC: ${get_partner_data(o.partner_id, 'vat')}
                        </td>
                        <td style="text-align: center">${o.date_invoice_tz or 'N/A'}</td>
                        <td style="text-align: center">${o.address_issued_id and o.address_issued_id.city and o.address_issued_id.state_id and o.address_issued_id.state_id.name or 'No identificado' }</td>
                    </tr><!--Fin Facturado Datos-->
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold; background-color: #C0C0C0; color: #FFFFFF;">
                        <td style="text-align: center">MÉTODO DE PAGO</td>
                        <td style="text-align: center">MONEDA Y TIPO DE CAMBIO</td>
                    </tr>
                    <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
                        <td style="text-align: center">${o.payment_type.name or 'No identificado'}</td>
                        <td style="text-align: center">
                            <table style="text-align: center; font-family: Arial, Helvetica, sans-serif; font-size: 10px;">
                                <tr>
                                    <td>
                                        ${o.currency_id.name  or 'No identificado'}
                                    </td>
                                    <td>
                                        1.0000
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
                                    <td  style="font-weight: bold;">Enviar a:</td>
                                    <td colspan="5">${o.partner_id.email}</td>
                                </tr>
                                <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
                                    <td style="width: 100px; font-weight: bold;">Condición:</td>
                                    <td style="width: 200px">[CRÉDITO]</td>
                                    <td style="width: 100px;font-weight: bold">O.C.</td>
                                    <td style="width: 100px">${o.origin}</td>
                                    <td style="width: 100px;font-weight: bold">Vend.</td>
                                    <td style="width: 100px">${o.user_id.name}</td>
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
                                    <td style="width: 150px">Cantidad
                                    </td>
                                    <td style="width: 100px">Unidad
                                    </td>
                                    <td style="width: 150px">Clave
                                    </td>
                                    <td style="width: 500px">Descripción
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
                                    <td colspan="2" rowspan="4" style="text-align: center;">
                                        <b>${o.amount_to_text}</b>
                                    </td>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; font-weight: bold;">${_("SUBTOTAL")}: $</td>
                                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt; text-align: right;">${formatLang(o.amount_untaxed) or '0.0'|entity}</td>
                                </tr>
                                <tr style="font-family: Arial, Helvetica, sans-serif; font-size: 10pt;">
                                    <td style="font-weight: bold;">${_("VAT")}: $</td>
                                    <td style="text-align: right;">
                                        %for tax in get_taxes(o):
                                            ${formatLang(tax[1]) or '0.0'|entity}
                                        %endfor
                                    </td>
                                </tr>
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
                </table>
            </div>
        %endfor
    </body>
    <footer>
    </footer>
     %if o.state == 'cancel':
    <div class="contenedor_cancelado">
        <div class="contenedor">
            ${_("CANCELED")}
        </div>
     </div>
    %endif    
</html>
