<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    <page>
        %for o in objects :
            <% setLang(user.lang) %>
            <div class="contenedor_principal">
         	    ${get_emitter_data(o.company_emitter_id.address_invoice_parent_company_id, 'name')}
            </div>
        %endfor    
    </page>
</body>   
</html> 
    
