<html>
<head>
</head>
<body>
    %for o in objects :
    <% setLang(user.lang) %>
    <div style="vertical-align: top">
        <table style="width: 100%;">
            <tr>
                <td rowspan="4">
                    ${helper.embed_image('jpeg',str(o.company_id.logo),180,auto)}
                </td>
                <td></td>
            </tr>
            <tr>
                <td style="font-family: Arial; font-size: 22pt; vertical-align: top;font-weight: bold;text-align: center;">
                    ${o.company_id.name}               
                </td>
            <tr>
            <tr>
                <td style="font-family: Arial; font-size: 16pt; vertical-align: top;font-weight: bold;text-align: center;">
                    ${o.journal_id.partner_address_id.name}
                </td>
            </tr>
            <tr>
                <td colspan="2" style="font-family: Arial; font-size: 12pt;font-weight: bold;text-align: right;">
                    MONEDA:  ${o.currency_id.name}
                </td>
            </tr>
           <tr>
                <td colspan="2">
                    </br>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <table>
                        <tr>
                            <td style="font-family: Arial; font-size: 18pt; font-weight: bold; background-color:#C0C0C0;width: 300px;text-align: center;">
                                P A G A R E
                            </td>
                            <td style="font-family: Arial; font-size: 14pt;width: 100px;text-align: center;">
                                NO
                            </td>
                            <td style="font-family: Arial; font-size: 14pt; font-weight: bold; background-color:#C0C0C0;width: 100px;text-align: center;">
                                1
                            </td>
                            <td style="font-family: Arial; font-size: 14pt; font-weight: bold;width: 200px;text-align: right;">
                                BUENO POR:
                            </td>
                            <td style="font-family: Arial; font-size: 14pt; font-weight: bold; background-color:#C0C0C0;width: 200px;text-align: right;">
                                $ ${amount_total(o.amount_total)}
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td colspan="2" style="font-family: Arial; font-size: 14pt; text-align: justify;">
                    En ${o.journal_id.partner_address_id.city_id.name or ''},${o.journal_id.partner_address_id.state_id.name or ''} a ${date_to_text(o.date_invoice)}
                    <div style="word-wrap: break-word; width: 900px;">
                    Debo (emos) y pagare (mos) incondicionalmente por este Pagaré a la orden de SERVICIOS AGROPECUARIOS DE LA COSTA, S.A. DE C.V. en ${o.journal_id.partner_address_id.street or ''} ${o.journal_id.partner_address_id.l10n_mx_street3 or ''} ${o.journal_id.partner_address_id.l10n_mx_street4 or ''} ${o.journal_id.partner_address_id.street2 or ''}, ${o.journal_id.partner_address_id.l10n_mx_city2 or ''}, ${o.journal_id.partner_address_id.city_id.name or ''}, ${o.journal_id.partner_address_id.state_id.name or ''} el ${o.date_due} la cantidad de $ ${amount_total(o.amount_total)} ( SON: ** ${convert_to_words(o)} ** )
                    </div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    </br>
                </td>
            </tr>
            <tr>
                <td colspan="2" style="font-family: Arial; font-size: 14pt; text-align: justify;">
                    <table style="border: 1px solid black;">
                        <tr>
                            <td>
                                <div style="word-wrap: break-word; width: 900px;">
                                Valor recibido a mi (nuestra) entera satisfaccion. Este pagaré generara intereses ordinarios a razón del 16% mensual, contados a partir de su suscripcion hasta el dÌa de su vencimiento, y desde el dia siguiente de su fecha del vencimiento de este documento hasta el dia de su liquidacion total, causara intereses moratorios al tipo de 8 % mensual, pagadero en esta ciudad conjuntamente con el principal.
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    </br>
                </td>
            </tr>
            <tr>
                <td colspan="2" style="font-family: Arial; font-size: 14pt; text-align: justify;">
                    <table>
                        <tr>
                            <td style="font-family: Arial; font-size: 14pt; font-weight:bold;">
                               NOMBRE:
                            </td>
                            <td style="font-family: Arial; font-size: 14pt;">
                                ${o.partner_id.name}
                            </td>
                            <td rowspan="4">
                                <table>
                                    <tr>
                                        <td style="font-family: Arial; font-size: 14pt; font-weight:bold; text-align: center;vertical-align: top;">
                                            Acepto(amos) y pagare(mos) a su vencimiento
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            </br>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="font-family: Arial; font-size: 14pt;text-align: center;">
                                            ____________________________
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="font-family: Arial; font-size: 14pt; font-weight:bold;text-align: center;">
                                            FIRMA(S)
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td style="font-family: Arial; font-size: 14pt; font-weight:bold;">
                               DIRECCIÓN:
                            </td>
                            <td style="font-family: Arial; font-size: 14pt;">
                                ${o.partner_id.street or ''} ${o.partner_id.l10n_mx_street3 or ''} ${o.partner_id.l10n_mx_street4 or ''} ${o.partner_id.street2 or ''}
                            </td>
                        </tr>
                        <tr>
                            <td style="font-family: Arial; font-size: 14pt; font-weight:bold;">
                               POBLACIÓN:
                            </td>
                            <td style="font-family: Arial; font-size: 14pt;">
                                ${o.partner_id.l10n_mx_city2 or ''}, ${o.partner_id.city or ''}, ${o.partner_id.state_id.name or ''}
                            </td>
                        </tr>
                        <tr>
                            <td style="font-family: Arial; font-size: 14pt; font-weight:bold;">
                               TEL.:
                            </td>
                            <td style="font-family: Arial; font-size: 14pt;">
                                ${o.partner_id.phone or ''}
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
             <tr>
                <td colspan="2">
                    </br>
                </td>
            </tr>
            <tr>
                <td colspan="2" style="text-align:center;">
                    <table style="border: 1px solid black;width:900px;">
                        <tr>
                           <td style="font-family: Arial; font-size: 14pt; font-weight:bold;">
                                Datos Personales y firma(s) del(os) Obligado Solidario y/o Aval(es)
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            %if o.partner_id.child_ids != []:
            <tr>
                <td colspan="2">
                    <table style="border: 1px solid black;width:900px;">
                         %for c in o.partner_id.child_ids:
                         <tr>
                            <td style="font-family: Arial; font-size: 14pt; font-weight:bold;">
                               NOMBRE:
                            </td>
                            <td style="font-family: Arial; font-size: 14pt;">
                                ${c.name}
                            </td>
                         </tr>
                        <tr>
                            <td style="font-family: Arial; font-size: 14pt; font-weight:bold;">
                               DIRECCIÓN:
                            </td>
                            <td style="font-family: Arial; font-size: 14pt;">
                                ${c.street or ''} ${c.l10n_mx_street3 or ''} ${c.l10n_mx_street4 or ''} ${c.street2 or ''}
                            </td>
                        </tr>
                        <tr>
                            <td style="font-family: Arial; font-size: 14pt; font-weight:bold;">
                               POBLACIÓN:
                            </td>
                            <td style="font-family: Arial; font-size: 14pt;">
                                ${c.l10n_mx_city2 or ''}, ${c.city or ''}, ${c.state_id.name or ''}
                            </td>
                        </tr>
                        <tr>
                            <td style="font-family: Arial; font-size: 14pt; font-weight:bold;">
                               TEL.:
                            </td>
                            <td style="font-family: Arial; font-size: 14pt;">
                                ${c.phone or ''}
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2" style="font-family: Arial; font-size: 14pt;text-align: center;">
                                ____________________________
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2" style="font-family: Arial; font-size: 14pt; font-weight:bold;text-align: center;">
                                FIRMA(S)
                            </td>
                        </tr>
                        %endfor
                    </table>
                </td>
            </tr>
            %endif
            %if o.partner_id.child_ids == []:
            <tr>
                <td colspan="2">
                    <table style="border: 1px solid black;width:900px;">
                         <tr>
                            <td style="font-family: Arial; font-size: 14pt; font-weight:bold;">
                               NOMBRE:
                            </td>
                            <td style="font-family: Arial; font-size: 14pt;">
                            </td>
                         </tr>
                        <tr>
                            <td style="font-family: Arial; font-size: 14pt; font-weight:bold;">
                               DIRECCIÓN:
                            </td>
                            <td style="font-family: Arial; font-size: 14pt;">
                            </td>
                        </tr>
                        <tr>
                            <td style="font-family: Arial; font-size: 14pt; font-weight:bold;">
                               POBLACIÓN:
                            </td>
                            <td style="font-family: Arial; font-size: 14pt;">
                            </td>
                        </tr>
                        <tr>
                            <td style="font-family: Arial; font-size: 14pt; font-weight:bold;">
                               TEL.:
                            </td>
                            <td style="font-family: Arial; font-size: 14pt;">
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2" style="font-family: Arial; font-size: 14pt;text-align: center;">
                                ____________________________
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2" style="font-family: Arial; font-size: 14pt; font-weight:bold;text-align: center;">
                                FIRMA(S)
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            %endif
            <tr>
                  <td colspan="2" style="text-align: center;">
                   <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALkAAABECAIAAABSwwPMAAAAAXNSR0IArs4c6QAAAARnQU1BAACx
                        jwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAadEVYdFNvZnR3YXJlAFBhaW50Lk5FVCB2My41
                        LjEwMPRyoQAAKQJJREFUeF7tfAVAVdna9jczd/pOeGeuhEqICuII2N3YLSqNpGK3qKiMIiIqSoNI
                        d3c3SncJCiLS3Z3+zw7OgITozHjv/33nmSWz91rvetfaez37jXX2Of/zlgkmJgYmV5iYKJhcYWKi
                        YHKFiYmCyRUmJgomV5iYKJhcYWKi+O/lysAQ9Pf3FxUV+fv76+jonDx5UkREZPny5TNmzPjll1++
                        +OKL/xmOr7/++tdff+Xj41u7dq2kpKSqqqqtrW1WVlZPTw+tjgQ9DBMTxn8dV+iVHBjo7OyMj483
                        MjJSUlJaunQpDw/PtGnTWFhYJk2a9MMPP3z77bdfffXVSKIAn332GerR+t133/3444/gDTs7Ozc3
                        9+LFi8Ezb2/v5uZmegwmYz4E/y1coZduYKC+vt7NzQ2LumjRIizw5MmT//nPf47KiXcAcoBDYAaM
                        zffffz+yC2pAnalTpwoJCV28eDE7O5sakZ4BE+/Df5gr1GoBbW1tfn5+R48exULCfvz000+ff/45
                        vcgjAKPy22+/7d27F0uup6fn7u4eHR2dlpaWmZkJBgAZGRmpqamo9PX1tbKyunv37vHjx7ds2cLB
                        wQGrA/z888+zZs26cOFCeXk5NQF6QkyMjf8YV6gVQiCCdUVIsWzZMi4uLjz3WEiaEcOBpvXr16uo
                        qNjb2yclJeXm5iKCqa6ubmpqgrfq7e19Z71xisqurq7W1lbYqoqKisLCQkQtQUFBGhoa4A0IB3cG
                        7wavRM6FSZf34FNzhVoVAAsZEhJy6NAhfn5+eI2xrAjcEOJTU1PThISE/Pz8qqqq9ra2/n5SBaEM
                        /wilbwdQ1dff193b3dHd3d7b0zHQ34NKcryhf952d/fU1tUWFBSEh4fD2MBnTZ8+XVtbu6+vjxBg
                        Ymx8Uq4QyzUw0N3d7ePjs3//fngBxCI0KYYD0aisrKyDgwNcCexHS0tLfz/WEoQAT/p7utvqa4vf
                        vErKSfdPfmb/NNgw1Od+oNstf+cbfk7XfZ2u+Tlf93f+PdhLMypQPzHaOifNv/R1WntLLfhEKiEA
                        spaWloaFhe3ZswfDwU/ByKGenisTI/CJuEItD9wBooddu3bNnDnzm2++oXkxBIhJt2/fjhAEGRAo
                        0t7eTvEDDGluqijKT0yPd40M1Pd3ueFtd8nN6oyz+VGHx4q2RoesDaSs9CQsdcUsdcRRrHTErPBX
                        X9LGUMbeRN7Z7Ki79VlfJ9WoAN2cVP+aqsJ+0ooASKRhrjQ1NUHcBw8eMOkyDj4FV3D38RAjAgUP
                        YPCRsNDUGALkO8rKygEBAXl5eQ0NDeSaYUF7airzsbrh/g+x0u7WZ5xMD9sayljpilvpin1EsTGQ
                        cTI75mV/KSpQr+xNBmWrML/a2loLCws+Pj4YPCZXxsLfyBXisSWRk5Nz+PBhXl7eL7/8kqbGELCy
                        siKdiYyMgCHpJbbL0LG/pakqNzMo3E/bx17FxeyYjb4MYTOI9RYlDAZhNnCAv1QRtdQhLYquKApx
                        SvwdxhK6EGKEHtgbL9sLSc9sO9ubKLo0NzcbGBquWrUKxg9zpq+BiSH4u7hCsQSZsJGR0fLly3/4
                        4QeaGkMAj6OgoIAIt6ysjHzEsWr9NZUFSTF2AS5qrhYnbeBZKIqAH7qisAruVqcDXH+P8NN+FmIU
                        H2meEGUVF2H2LMQ43PeBn/M1JzNlS10whiAEwaqhLBmtOJooQlVLUzU52f76hgbMB0ESTujLYGII
                        /haukLd+ADGHhIQEMuFR0+AVK1Yg+y149YpKQMCS6vI8LL+v01WEIFhyrCXMg8NjpUD3WwmRlnmZ
                        waWvU6rK8uqqCxvqSpobK1uaq1uba1uaa3DcUFdcW1VQUZJVkBsdH2npYXORtECDpmg4RRgF+kHH
                        cF/tzvZGTAFZEhL4ffv2wQPSVwKANlRhgFEzpHL4GcCQGF49FMMbycPhJB0uMIjRaz8B/nqu4KZ3
                        dXUZGxsvWbJk1AB20qRJly5dSkpK6ujoIEgy0F9T8RIWwtfxqp2xHOFcdMVczI8jhXmeHlBWlFZb
                        XdjaUtPTDWHGEo68WeQdRJ7T2w0OVZblZiZ7IvglPdF7DAzMVeJTGyqqRairpKRUUlJCa337tq+3
                        t3MIwGyyso9xjF446Ors7O0j9nhwjKburi4iYxsEXdndTZ8PgtA4iJ7BVoRrTU3wjDSoIQAMQZL4
                        fwtXcElVVVVnz57l4eGhqTEc8EdOTk5IVqnrb2+rT0/w8HO6Zmcsj4DD2kA6yF09M8kLgWdjfWl3
                        V9vbgT4opbVPDKTi/s6O5rI3mZH+OgiEx7cuaHIwVaouf0l2HPDz80MYjgNKm7ODvYKcjKLcIUXy
                        b052DprMTR8rysmGBAWRPQasLS3RGhgYgOOwkGAl2UMop44pPzY2bGoiLNbTqChFVMrJnjlxwvzJ
                        49aWFlTW1FQryEESaoliaW724kXeDdUrhyQl5KQl79y+WVVZCTHqip49jYZMfGzMf44qfylXcEnZ
                        2dliYmKwHDQ1huDzzz+XkpKKjY3t6uokXE5/X3FhGuIMpyfKFrqi4Eqk/6P8nPDaqledHcStJG/J
                        n7gxUNHf11BbHBv2eNAZjV10xJ6FPqbsFh5rJM+MRcIac7KzqFw4r6F+E6W0uKSpsXH1siWc7Kyq
                        l1UgUFJcvHr5UsiYGBviVOPWTS421tPHj4kfEFm6cN6jB/egVvu+Ficb64mjylJiB5cvWmBp9gSS
                        8bGx6LV/905Ks5enu7SkuCA/H9ReuXgRdGmor4cYAG6JHRDhYGe5pXYdp/9/c4W6JH9//02bNn39
                        9dc0O4YAYezly5dzc3NJwb62ltrUOBcf+8vEpogOHuvDMaEm+TmRjXXF3Z1tA/2EMR8KepgPAXFL
                        iX/9TQ3lge7qlGsbqyA8cjI90tlB2AAADpTo+/YtUv1lC+fzcExNSUrKy31eUJAPJ+Xl4cY9hXX6
                        NPbtmzdC4Ma1q1xTWAmuGBFcOSQpzjWFLTMjw9PdDfzYtmkDnovDCnJc7GypqSm+3t6ohIGB67U0
                        M+Nkm6z78AE0o7wqyOfhnMo/kycu9lnR69dJiQnwXJgEfPRjYyPe6VwLheZuWLOKclXUNX5i/AVc
                        wdQRoOjp6S1cuHDUrfoff/wRTyqSHcqcwL9E+D10NFViLJWdoayPw+VAt5shXpoR/o+Q1yQ/s8tO
                        DUDY0dvT9SdvDQbFiDb60ozhxiqInSGM4Xx9falBK8rLpnNM4Z7KjtVVVpC3t7Pt6+sVP7Bvzszp
                        ovtFZs+Y7u/nM+83/j3bt3KwsTw2MsLlLVs0fwbnVPBGWVGRi43lysULuOQ1y5dOnzYFS378yGFU
                        amtpYZxL589ysrHs3rbliIL8udOn2tpaT584Nmcmj5yMpKmJUV1dHewHppGclLh8yUIZSXG1a1dn
                        cE57nkM4QerSPjH+LFcwb4So6urqyHdoagzHt99+q6WlVU+Y034EnnmZQb5O12BOiKiTLOSmCJnl
                        Il7Rl3KzPhvup52R6F7yOrWpsbKvrwdj0IN9FDBDhKf+LjeI4caNczMSXCGMeWZlZeF/6Po0OhLL
                        uWXDes3b6prq6mFhIc9zsmfzcB87omRsYIimbRs3LJkvZGdtTXLFsL6uDkQRnMMHzyW+X0RN9erL
                        vDyELLO4OebyzVq1dNG8OfxqqqqvX70CV8AwrP0d9ZtQbqCrixFfvnjhYGerrKiwfMH8uxrqqIFD
                        lBEX5Z7KpqfzyNjQACOaGBmRc/sP4E9xBZNGAH/79m1WVlaaGsPxxRdfqKio1NbWYgF6ejoyk5Cb
                        nKLXhmaJKLEtZncx3Pd+0jO7l1mhJa9TELK0t9b3wxPR4/wpkA9nf1q8C8HIIcwYWeLCTSm7QqUh
                        6PrksTFIcOt3taqqSkSaePS17mjwcEyBm0iIi4Pf4WJn1Xv0MCE+nlhFY8O0lBSYDXgcBLMQKC0t
                        wfBZmRmQBHvERPbycnOhCcq7OrsE+HlXLltSVVmBbKCutra9vT0rMxP3Mz01FRZrzfJlMEiwTzM4
                        ps3k5jiwd/eeHdvh3cQP7Cfn+B+gy8dzBdOF84ZzYWNjo6kxHJ999pmcnBzyT4ooWC0nM2XKltga
                        yoIfEf4PU2IdXuaElxal1VUXtrXW9ff1UKtFj/GXgLixA0UFiaT1Gu/DgZhQhCnUR9MEUVAunj8D
                        EiAgfaCl+UDrbnlZ6doVy3Zv39rR0d5QV887nXPbRuHyivKkxETyiTd0dnTEgZmpCSP8hCo3VxfE
                        JabGRhHhYSDBtcuXEYgUFBRg4RfPE6Q0JybEOzs5YCDN27cQwM7k4jh1/Fje85yVSxdt37zJ0d7O
                        yQHFXkpMbC7vzJrqGnKGnxofzxX4ZnNz82nTptHUGIG1a9fm5eXhqnp7OtMTPdytz/o4XokK1E2N
                        dXyZHVZSlFpXU9RBbbGTC0Pr/XtQVf6C9nQjKMIoSdG2JFMHd3EGBrQ078hKSRxVVDh59AgW73l2
                        tsIhKWdyY7e/rx9BBgJYHMN3QMzfz9fTwx0HKUmJtAaSK96enoekxBGrwmao/6529uRJGNqM9HRI
                        KsrKnDyqDOVPn0bFPHt65dKFw/Ky8oekf7+mmpWV6e3lKSstEejvR2yrQBGyBz9f9HpB3lV6gE+I
                        j+QK5hoSEsLHx0fzYgTglUJDQynh1pba3PRg0n6k19cWd3Y0IdOBir+bH0NBckV0dLtCekP8zcsM
                        JbgyZFYv8nLhEVDSUlMz0tLq6+pxjL8Ut7Fmra0tEGttbYUAXAmcTnpqClVJAYJlJaVobWlpwXFp
                        SUl6SmpzczNCV4ZmlIaGehib4uIimKjEhATE1JhGfv7LtNSUrs5OWheZz0O4rr6ePv+0+GCukPwe
                        yMzMXL16Nc2LEfjHP/6hoaEBD0V16epsQ6GeV/RtamzEXcgfAtxHShKtePiQWqekpBQWFhJJIwmq
                        CYsBYVhv+DWIMZreB0Ks+FXymPEKvfsiUVdTSCocppPoPAR07Yh6CnTbGK0UaIkhMvT58F501YhK
                        +mgCGNl9IqB6jYqP4QrWTFRUdKyXHYHNmzdDhu4wHOju5OR0cDiQd1BN2dnZly5dEhER2b59u7i4
                        uKamJhkX0/cIpxDG0NLS0mfOnHFxcent7SW1jgcqts1K8SZCpVHzIJIrblan4SvpPoNAT5AyMiLc
                        wszMysL8WXQUtb0Bp5CdleXq7PTExAjRCbxMObEj8Acqyst9fbyePDZBdOzm4gQn1dPT7WBvFxIc
                        TNkkyCB09fH2gnIcU6NBrburC7QN1hCyeGAQ8bi6OKMVp3gC3VydHextyS1NYj/Xwc6GLLYoNTXV
                        kREROMh/+ZIaCBkoTsNCQ4pevx6UpOUbGxu9PD0YNU6IiuztqHFHxYdxBZPr7u5WVVUddcONwo8/
                        /gjvw7jad4B6SUlJiM2ZMwdskCDx6tUrNGFVcAzNS5culZGRmTdvnrCwMJlsE6pwp4SEhNBx/fr1
                        qP/uu+8EBQWjyJyCVDwmIIB1ifDTfpcig4X6UDouwmykJgyK9d63c4fo/n0SB0WkxUVBgrbWVisL
                        M0QVB/ftQXiBym3CGy6cOZ2TQ38xIC42FqfbNm0Q3bcXEQkkH2lrl5WWrFi6SPWyCkkUYlZpKckb
                        168VOyAyyPgBOK/1q1cqysuilawhxHKf56xbtWLtqhWNjQ04jXn6FKcrly5ubiaStWPKSquXLzmi
                        KE8WhbKyMoVDMiuXLLqqcqmvl7DKCfFxOL2ueiU6MhIym9atWblk4WEFWWTmyOwwgS0b1lLdz506
                        iUKNOyo+mCu+vr7//ve/SVaMDlABfKI7jADuPj8/P8SuXLnyfBCU/Js3b0AUmCsHB4cXL154kcCI
                        VEeklGAhOqIyOjp62bJlOL58+TJDYCyAKN1dbc7mx96hCKPAqNjoS1SUPh+pCk/eonlCvNzcnh5u
                        Pl6eBro6SG7x8C2ZL7hr+1Y7G+voqMigwIBrKio8U6ecOHoYF/K6sFBsv4gAH6+62nVfb+/I8HDY
                        CR9v7+jICA62yXc11CmjArerrCjPPZUNKQ+6ENN8O5CTnY006uQxZcZMcLuQFqESfZOSEkEmWUlx
                        pPGc7KyNDY19vb2L5wsumicQEhREFURCQnP4Z3JOE+TnS05KhB6YQ072yffu3oFdCQkKXCQkgFws
                        ODAgJDjo9atXXFNYD+7bTfV9Gh2FQo07Kj6AKxgYEdmaNWsIRoyBH374IT4+fuRNp4B62AmYBEie
                        O3fOnQS4QrWWlpb+/PPPaFJTU0tOTsbTxtCDA7AHTSBTRUUFApoVK1aAVRcvXhxrLAYgUPYmY/RI
                        hSo6Yn7O13p6CJNO9xkEyRVBXm4u2Hzc667OLgCP5iwujqDAQCwkZNCprLRs6YJ5qCwrLTUy0Odk
                        Z8FjDVZRSgA4DjMTEw52FngTnKKjtYUF73SuI8TeP6udrTU5zQEXpNzsk/UePSLcB4nKygpoRmoN
                        neZPTJF2zeLmmDNrBucUgis1VVXTp01BXg1f5uPlBb+De4hUfM+ObcsXLziqpIi4WPXyJfRFggb9
                        nR0dv/HOxPyJwQYG4JjIHYEDVPf6ujoUeuDR8GFcQZKMuJUgxRjYuXMn7gsk6T7DgfqkpCQq0Jkx
                        YwZ8ChyNo6Mj1Up5t9mzZ//666+7d+/W09ND2E81oaOHhwd6gSsqKipwXt9///3kyZORi401FgMD
                        A33RQQZEpvMORf4oEgW5kdAzUhViBQuzJ1KioluF1587dSLm2bPGhgbuqewLBed2d9MfPuAPDnZs
                        3oj7/jw7Bx4Ha5OSnDxUG44vnTsHrmRlZuA0G5nB8iXQidN5c/gV5Q6RIgM3VFXBlUB/fwZXnBzs
                        oO32zZsglpy01M4tmzdvWLdjyyaKK8Snj2ws4IqSvKySnGxUZAQcDUbR1NDQefiAfwZPVEQ4HCU0
                        wGJBP+gOg3TssBIx2MAAQWs2lu2bhcnucnCvKPTAo+EDuIKVmz9/PkmJ0QESYEUxCbrDCKDJwsIC
                        kpMmTcKSA3AiqampjFZEsvb29qdOnZo6dSo8HYQZTerq6ugIfnzxxRcYCHZFW1ubegOGkhkLTQ1l
                        DqaHR7UrZBYNo3Kjs5P81ipjiQaBOoSQyGMN9XRguqXERREl8PFwC87hq6qsoMTRraiwELZ9Lu/M
                        qopKZSUFDvbJEWFhpAIa0LN353aYBOSAcKanjx8FJ/Zs3/rY2Gjh3N/mz51DvbogsmcXFxtLwct8
                        QvPA257uHlGRvXNnzyrIz9+4bs1cvlkwXU4O9vIyUhRXrCwswINrV1QQEaMgIUd0BW/l5upaXlYq
                        vGa1lNhB0JqPh6uF/FpuaEgw/Bf50TeBsyePgyumJkZUd8SLAD3j0TBRrkA1/MU43wUEpk2bBj5B
                        ku4zAmg6f/48JJcsWQIXQ4Gy5ADMO/JkyMBPwXJAbM+ePVQTKsXExFCDYAiRCrhCRUXjjEUBypNj
                        7EGU0e2KjpitkezrfMppUmUYXr7Is7GySk9NjY+LheVfvXRJX18vYTmmsN659XtqSnJB/stnz55e
                        On92Fjen2rWrCCedHR2wovLSUmGhodlZmQgaAgP8QTih3/hXL1va39fv7+szewa3yO4d8jLSinKy
                        +3Zux7P+9Gk01knwt9kzOKYmJyQiycKteJ6dDXNy/IgS1J47fRLLLCl2EBEJgyvwdOCKrbUV5HNz
                        EW/1E59HsrNkZmTgiqwtLXmncyIk2rhuNe4DaowNDWB1kKDhGNi+SXj61CkwTugOk0NV0lc+GibK
                        FVjjHTt2EIwYG1i/8QdDK9JpSCLTQeYMUN/5o5oQ0iopKVlbW7u6ukIMvASxGB3nzp2LjnZ2dm5u
                        bjBLnJycMEjjDIcWtNZUFrggqqV3UN4tljriz0KNiUgFLCE60H0HMRAcFLhn5/ZTx48ePawkvHaN
                        oZ4e1gOZBbwGvD5WUeXCucPycru2bVa7plpaWoIR4fJVVS5tWL3yoMje48qHTygfuXzhQmVFOXhw
                        XPlITU2NjKTEzq2bEeqmJieBbYg3YVcePriPWEeQf/YCgd8unT+HYm1pgVB6gcDcuJhnWGnE0csW
                        LYgm876TR5Vh2GCiwDYBfl74FMjf07yDJPyQlMRCQQE04Voa6uthlgRm86lcOI9ewI1rqoL8vHgA
                        cIzYZeWSxRj60rmz6I4UmpKhL300TJQrRUVFVBoyDhDNjD8YrnnBggUsLCyzZs2CEwGkpKQoyuPv
                        /fv3Eb4ICAgsXLiQh4fn4MGDGRmEdwfga1CDjpnkp2twUqysrGfPnmVs942CgYGO9iYiVR57X9/X
                        6XpjfSkGp7u8AziXoteuzk46D7Wxlh5urowfWMjLzXWwtX14/x5WyNhAPzDAD1Ew1QRUV1e7ujij
                        VfO2uv6jR/BH1VVVBno64WGhFRXlhvp6wYGBtCjxAUiPiZGhr493ZUWFga4uxKgCDnl5eJiaGBOv
                        Yw4MvHr1ytrKsrenF7Py8/Ex0NPFYoNADHkne3vcRNiYJyYmuJnE9Mn38Qz09GJjYsihBmBRINne
                        3objjvY2UJ/RPSKc2OYAqEsfFRPliq2tLc2IsZGWljb+YDBODx8+vDcECGypKQJIsmAzNDQ0rl+/
                        bmRklJ+fj0qqY1tbG5gEeeoLGciucayvrw+3RQmMAKT6ctICrHUlx8qAXJ4cffMqCURhjDISaHoH
                        49dToKveB8qM0ScTxgS7EKrHlhy/aSxMiCtQceLECZoRYwAxBGOPdSyQkxkFY7VS9QB9TmLkKQAO
                        FRQUxMXFUWRCdW1VgavlKetHxJeG3mEJip2RXGaiB/Haw5BRJg6yz5Dp0f8nJkYf0RhTOTnJ0VqH
                        15GE+qNq7F6jVY6KdwQn3A+YKFfWr19Pk2IMILyAdxj9Sv4GYKCWlpaXL19GRUUh0Ll7966ysjIy
                        Iyq4bm9rivDXJnb0qa+cDVKESHyIF/elY8NNu7voj6jGB9Ja+AJvT8+Q4KAXpKdHJbyMl4c7ozzP
                        yamqqoQAAlu4KsSzcBxpqalEq6dHUEBATnYW5RcAhDXhYSFwbQgRIBwXE9PW1ko1vSkq8nL3CA8N
                        ZTiRyIgwKMEDUFpaGuDnhyTI29Mj9/lzhjbIJCUm+Hp7Iegmz4maxIT4waH9EV8joEZlVWUlLoTx
                        Wh3+VqLG/Y+rQF6NQigZAxPlyjgfKVMAVyifTff5GwDloEJubm5kZCTiYi0tLQUFhZUrVyK7/uab
                        b3bv3p2eTjjB3t6uzGRv4tW7IYaEKuCKjYFMdJBhG/E9eDKeHReQuXrpguCc2Qf37d2zgwhyX+Tl
                        oR5rIDSHb/vmjdLioiiIXRC4IJ7ds2Pbrm1bThxTRo567vQpoTmzJUUP7tq29YiCPDgHbcg41K6r
                        7tmxdf/e3ShbNwojl7axNCc+3Hn71tLcTIifb8OaVeROLhHeYYiFAgI4/f36Nejft2sHarTva8Gb
                        U9NDJCR2YB8ydiqypriiJHcIMbKirMz+PbuU5GXBLVSCakL8s60GY0r89fP1xnAIzHEJUmKi7q6u
                        KGgaC+/hCqw0qXaAm5ubJsUYgA9C4EnN4y8EFCKFBj8iIiJgP27fvi0tLY006pdffqEHJl/8lpCQ
                        IN+Vwe3tLcqPd3is9M6rKmTaLGajD6LotzbXEBaFmOp7Zgt1m9av5Z7Kjlj1yqWLnGwsWCd0untH
                        g5N9spamRmhIMEpURMQMzmmLhQT8/XxgWnQfPYSJ3bhuDR8Pd6Cfn5rqVXS8eUMVF6IkLyfAz3fz
                        xjUYodiYZzZWlsJrVyGXSUtLwZWePnGMi20y8uTbN9V6e3sRSs/k5lyyYF5ifDxSXxAxPDTkiYmx
                        s6MjZVdgS4wM9GdwTkWe7OJMRH6YW29vz9IFQgsFiQRKQ/0mhn5MvjSOWBvHIeT3VNAXf+/fvcPJ
                        Nllf9xFxFcHBYBsKed2j4z1caW9rGHhLWDAqZR0fjNff/ySQ9ZSUlCAlDg4OBj8Q7YIfixYtGvWL
                        rmxsbOS3v4oxdH9fT9mbDA/b8+RXmt/hiqi9kXxUoH5Lc3X/hF+9g3ng5eGePXN6bk4OUhIOdhb1
                        m2roKyl6AFwx0H1ELXne89x5v/GvWroYCVFBfj6WsL2tbfaM6csWL4AdsrIwR8dL588gA+dkZz15
                        TJnaQiTRb2FmipV+oEX8oofwujXTOaYoKynMn8ufnZkJ94GOsjJS8XFxc3lnIgFGpl1RXg5JqjNs
                        1ZL5QhIHRQRmzzp2WBE14EpNTfX0aVPWrlgGYt2/q7l4ngAsCq5YWVGBi50NJooQIrmiICsD/eZP
                        THEViQkJpMrxbst7uFJd/gLXAxU7d+6kF2dsCAsLI2Ghe34sMBaev/DwcGRMMjIyyJ+pX42D8Xhn
                        JxCWDAyGpSFjFBiUntLXad4Ol6nvvv/BFfJVJkcTxbhws7aWOvKGkDd1AsjMyMDdxEqcPq68duXy
                        HZs3xjx7iuRrvsBvM7mnyUiIyctIwWwgOtG+pyV2QAQO4vzpU6mpKS/z8sCApQvnXb5wfsfmTVuF
                        14cGB2mTTzYCDmJ8AsREYp89ReVVlUvw4LO4ORcKCb7IzV2+eMGpY0ftbKzQhHS9rbVV/ebvIrt3
                        7t6+VePmzVLitVTipWCwChwKDvA/sHcPnE4j+Zk8uItem9evPX70yJJ5Qts3CSNtBL3Wr1ohwMfb
                        NRhTwoutWrYElu+QlIScjJTWHQ1iNn+GK4UvYpF8YiVu3bpFL9HY+Oqrrzw9PSnz+NHAdHt6ehB2
                        waOFhYUhLjEwMFBTUzt8+LCAgADj06jvvvtu3bp1rq6u1EPW3dlWlB/nYXuBIgrDnKCANC5mysnP
                        7Lo6kSJ92NxcnJ042Cbjdgvy84EfwYGBGKz4TREXO8ualcsjIyJQwKfenh7EpzAhutoPYDmOHlHy
                        8fYEyWAJbqhexTKAKJinueljVOo90mZsC7W3tT/Q0uRiZ7Uwe5KelgZ6iZGvXus9egRPJCV+EKse
                        FhIMdra3t6elpoBAqLF48gThqquz4/Sp7MsXzYcT2b9nN8ZFFIXpmT95DD26Dx8kJSVevawCG2Np
                        ZoY8YBY3x66tmxlsQNLKwzF12yZhOFAUKuZltI6K93AlO9WPSixjY2PHeWeFAZiBDHKDme7/sSCn
                        TQMW+/nz525ubuLi4tTvlM6cOVNOTi578Ick21vrczOCHM2OkraETnxwTP1mgqf12cwkTwS8kIRe
                        eoD3AoIDbzVuEf7eytzs0rnzs2dwxzx9imq4drj5vbt2pqYko9TV1sXHxjo72qempGBdOaewykpK
                        PnxAmJAAfz9qhhSys7PgMtauXBYY4J+ZkY61d7K3XyQ0d9umDciAXJwIXl6/egWSNdXVwmtWQxXY
                        UFpcHBYa4uHmBnlDPV1wQl/n0auCV+tXr4SpkBYjgmv8RcAE7wZGqlw4h6Ed7Kwz0tMhzz2FHTaJ
                        eNuBnUV8vwgmnJKSXFtTE/MsGmLSEqLUVTD2EunLHw3v4UpqnHNvTwfuGqiNiJJmxLhAPpKcnDze
                        jurEACNZXl6ekJBgY2MjKir6008/QTlSnk2bNpmbm8PZ4cL6iW+hlqTGONoayljqSAy1KDi2NTjk
                        73K9MDfmY/ZRSK5cOHN68TzBhPi4VwUFSE/OnjoBd2NrbY0gYIvwOqQbSnKyyYlJcECb1q1ROCSD
                        pGbrpg3+Pj43rlxZLCSI2IUxLjnbARMjo22bN24WXndEUV7xkAziXwnR/eFhxJ6pob4+1CIrxjFg
                        Z2O9eL4gBu3u7gaBoF9R7tDm9etgQhDKPNDSWrpwvoerC1a9rrYW3Nq9Y9uWjRs6OtoPK8gtmidw
                        7IjiqePHdm7ZLC0mBlqGhgQhV9q2URgThp74uFhHe1sMB6eJGpTnz/+0XclJD6guR35BXKqzs/N7
                        t/kprF69Gs7o9evXH8oYjIJbU1ZWlpaW5u3traKisnjxYsrvILCF0VJVVS0uJsJY3Pmurtby4qxw
                        34fED3CQ77bRWyn4qyPm9ORIVKBeXfXgR2IfSBWKKy6OjoZ6evV1xBfhvL08jQz0mpubnkZH4Xml
                        ioGebllpCdYKkvfv3n304EHM02g83J5u7mjt7GgfOjB1G7FORvp6Guq3EHiCGehOTA/mKiQY2kBK
                        UnKgtaUZwxEf0/QPVJSX2dva3NPUQA2imfb2tsdGRmamj3t6uqnFhTwSYHRvaKi3sbKi5mZqbOTl
                        6VFZUY7Jw4gZ6qJSj5pzcVERrgIHlCRKTQ3xPRKAUDcG3sOVuurC+EgL6tfVsPCw/KP+TMZITJo0
                        6ciRI+7u7ikpKYitkP5RWwLvAGpBDgSnpaWlcDQxMTFgJCiydu1a6pUoACxBpIJ4hXqLCoA5aWwo
                        e54Z5Gp5ErSwGLQldNGT9LI9n57g1k0EKATowT4cVPdRQbSOK0BjBEnp+iF4p544noBiClRfgD6n
                        MLJmyETocxJj1YyK93Clv7872FOzvuYNpaiiomLXrl2j5q6j4ssvv4RhOHHihJGRkZ+fX3R0NNY7
                        MTExKSkJzgXMQL6DQERHR+fs2bNItXh4eJDdUH2R9bCwsCxYsEBRURFioBpBkv5eJL0lr9MiAnTI
                        780TvobhenDq8Fgp2OMOEiI6Mab++/OADlIRoXKoRrKebmLUDD2mj8bAWAKD9XTjULF3ZzAcQyUZ
                        GFk5qtj78B6uIAnKz4mICTFuJ3/5CIABkJeXnzFjxqg//jYOsPYwNtOnT+fj45szZ86sWbPY2Ni+
                        /fZbunkQEPvXv/7Fy8sL04LkC86IynT6+npammsqirNjw01tjeRhTsgv+/wRoNgby3nZXkyJsSf2
                        hAjQl8DEX4X3c6Wnuz3IQzMzyYP6WRQAzgieYsuWLVxcXBNJjiYCJDiIW0GRNWvWnDt3zsfHhxGZ
                        9/R0NjdWwpbEhJs6PD48uH3CKGK2BjKetudjwx5XlefC9qALHpqxHz0mPhLv5QrQX1OZ72Z1JivZ
                        p621jloMACm7tbU1sh5+fn5WVlaEFwz3MRHAflDvzMLvzJs3Dw5ITU0tODh48INi4lcVOtubGure
                        FL6IifB7YGMgDVpYDDEkKNYGUu6WpyIDdSvLwBLCSaHjx5hXJiaA93OF5Evfi6wwpyfHEqKskKOS
                        P91GA2EEIo979+6Ji4sjNJk9ezY3N/eUKVNAgl9++QVO5+eff4ZPwTFqUA9TBO8zd+7c5cuXS0pK
                        qqure3l5IWOiHA0WGxFJV2crDElFSXZqnBOxD6tL/AAHEZRQyQ7JEhsDKVeLk6E+Wm8KEvv7qF9a
                        I6bLJMrfh/dwhQK5hH2ZyV7OT476OKoW5EY1NpSTXzsdhra2toyMDOS6pqamd+7cuXr16oULFxC0
                        Xrx4Ebnu3bt3TUxMEMkipC0sLKTelh0E8bPHXZ0tzU2V1ZUvnqf5h3hq2hgcIvlB5cOMIo64xM3y
                        dLjP/aKX8X19XaQt+VM7xUxMEBPjCmlbQJcXWaHuVmds9Q/5Ol7NTvVDRo14E3EMuStK5NXvgOg7
                        BENOkab09fZ0dnY0tTbXNNa9QeaSnuAS7KlhayRLbLnSJgRcoYqYtZ6ko+kRT5sL8ZHm5aU56A0t
                        tDqmLfkkmBBXKJDL0l9d8SLU6x4MjI2epJ2JXIi3VkaiW3FhckPN66bGytaWGqQhnR3N8CPdXe3w
                        VohMe7pROrq72lDf3tbY2lLb1FheW1Xw+mVsapxzqLeWi9kxK2rXlf41/T+CEmt9SXtjBReLE4Hu
                        6jlpfqAmZUgIhjDxafEBXCGeXpIvvX09hS9iA9xuOpkpE5vr5McucBmIfwM91KOC9BKirFPjXLJS
                        fXIzAl9mh73MCs1ND8xI8kh8ah0dpB/g9jvx6076UoTxIP0LuU1CfSBM/eq1uK2BtMNjJVeL437O
                        N1JjHSrL8qh9ehL0VKhJMfHJ8CFcIUGv0qD5B9pb614Rv1Zt4e9y3c5YjtpxH+QB4T5IEpCF+Ml8
                        sp6qJOoPosbeWNHH4Up0kEF2ind5cVZ3V+sfzoUcj0mN/wYwucLERPHBXGHi/yyYXGFiomByhYmJ
                        gskVJiYKJleYmCiYXGFiYnj79v8B5J9Bf7QJExMAAAAASUVORK5CYII=" alt="esr" />
               </td>
            </tr>
            <tr>
               <td colspan="2" style="font-family: Arial; font-size: 16pt; font-weight:bold;text-align: center;">
                    CONFIANZA * COMPROMISO * VALOR
                </td>
            </tr>
        </table>
    </div>
    %endfor
</body>
</html>
