<html>
<head>
    <style type="text/css">
        ${css}	
    </style>
</head>

<body>
    <%
    def carriage_returns(text):
        return text.replace('\n', '<br />')
    %>
    
    %for partner in objects:
    <% setLang(partner.lang) %>
    
    <!-- cliente/fornitore -->
	<table class="customer_supplier_table" width="100%">
        <tr class="line">
        	<th style="border:none;">
        	%if partner.customer:
			    ${_("Cliente")}
			%endif
			%if partner.customer and partner.supplier:
			    ${_("/")}
			%endif
			%if partner.supplier:
			    ${_("Fornitore")}
			%endif
        	</th>
		    <th style="border:none;">${partner.ref or ''}</th>
		    <th style="border:none;">${_("Rag.Soc.")}:&nbsp;${partner.name}</th>
		    <th style="border:none;">${_("P.Iva")}:&nbsp;${partner.vat or ''}</th>           
        </tr>
    </table>     
    
    <!-- dati anagrafici -->
    <table class="general_data_table" width="100%">
        <tr class="line">
        	<th colspan="3">${_("Dati Anagrafici")}</th>    	
        </tr>
        <tr class="line">
        	<td style="border:none;"><strong>${_("Cognome")}:</strong>&nbsp;${partner.fiscalcode_surname or ''}</td> 
        	<td style="border:none;"><strong>${_("Nome")}:</strong>&nbsp;${partner.fiscalcode_firstname or ''}</td>    
        	<td style="border:none;"><strong>${_("Cod.Fiscale")}:</strong>&nbsp;${partner.fiscalcode or partner.vat or ''}</td>  
        </tr>
        <tr class="line">
        	<td style="border:none;"><strong>${_("Data Nascita")}:</strong>&nbsp;${partner.birth_date or ''}</td> 
        	<td style="border:none;" colspan="2"><strong>${_("Sesso")}:</strong>&nbsp;${partner.sex or ''}</td>      
        </tr>
        %for address in partner.address:
	        <tr class="line">
	        	<td style="border:none;" colspan="3"><strong>${_("Indirizzo")}:</strong>&nbsp;${address.street or ''}&nbsp;${address.street2 or ''}</td>   	
	        </tr>
	        <tr class="line">
	        	<td style="border:none;" colspan="3"><strong>${_("Località")}:</strong>&nbsp;${address.city or ''}</td>   	
	        </tr>
	        <tr class="line">
	        	<td style="border:none;"><strong>${_("C.A.P.")}:</strong>&nbsp;${address.zip or ''}</td>
	        	<td style="border:none;"><strong>${_("Prov.")}:</strong>&nbsp;${address.province.code or ''}</td>   
	        	<td style="border:none;"><strong>${_("Nazione")}:</strong>&nbsp;${address.country_id.code or ''}&nbsp;${address.country_id.name or ''}</td>      	
	        </tr>
	        <tr class="line">
	        	<td style="border:none;"><strong>${_("Telefono")}:</strong>&nbsp;${address.phone or ''}</td>
	        	<td style="border:none;"><strong>${_("Telefono")}:</strong>&nbsp;${address.mobile or ''}</td>   
	        	<td style="border:none;"><strong>${_("Fax")}:</strong>&nbsp;${address.fax or ''}</td>      	
	        </tr>	  
	        <tr class="line">
	        	<td style="border:none;" colspan="3"><strong>${_("Contatto E-Mail")}:</strong>&nbsp;${address.email or ''}</td>   	
	        </tr>      
        %endfor
    </table>
    
    <!-- dati generali -->        
    <table class="general_data_table" width="100%">
        <tr class="line">
        	<th >${_("Dati Generali")}</th>
        </tr>
    	<tr class="line">
        </tr> 
        %if partner.customer:
	        <tr class="line">
	        </tr> 
		%endif
        %if partner.supplier:
	        <tr class="line">
	        </tr> 
		%endif  
        <tr class="line">
        </tr> 
    </table>  
    
    <!-- pagamenti -->
    <table class="general_data_table" width="100%">
        <tr class="line">
        	<th colspan="2">${_("Pagamenti")}</th>
        </tr>
        <tr class="line">
        	<td style="border:none;" colspan="2"><strong>${_("Tipo Pagam.")}:</strong>&nbsp;${partner.property_payment_term.name or ''}</td>   	
        </tr>   
	    <tr class="line">
	    </tr> 
	    <tr class="line">
	    </tr>
	    

    </table>  

    <!-- banche -->
    <table class="general_data_table" width="100%">
        <tr class="line">
        	<th colspan="2">${_("Banche")}</th>
        </tr>
        %for bank in partner.bank_ids:
	        <tr class="line">
	        	<td style="border:none;"><strong>${_("Nome Banca")}:</strong>&nbsp;${bank.bank_name or ''}</td>   	
	        	<td style="border:none;"><strong>${_("Numero Conto")}:</strong>&nbsp;${bank.acc_number or ''}</td>   	    
        	</tr>
        %endfor                
    </table>  
    
    <!-- documenti -->
    <table class="general_data_table" width="100%">
        <tr class="line">
        	<th >${_("Documenti")}</th>
        </tr>
    	<tr class="line">
        	<td style="border:none;"><strong>${_("Agente")}:</strong>&nbsp;${partner.user_id.name or ''}&nbsp;</td>   	
        </tr>
    	<tr class="line">
        	<td style="border:none;"><strong>${_("Aspetto beni")}:</strong>&nbsp;${partner.goods_description_id.name or ''}&nbsp;</td>   	
        </tr>        
        <tr class="line">
        	<td style="border:none;"><strong>${_("Resa merce")}:</strong>&nbsp;${partner.carriage_condition_id.name or ''}&nbsp;</td>   	
        </tr>                
    </table>  	
    
    

    <!-- fatturato -->
<!--
    <table class="general_data_table" width="100%">
        <tr class="line">
        	<th colspan="6">${_("Fatturato")}</th>
        </tr>       
        <tr class="line">
	        <td style="border:none;"><strong>${_("Esercizio")}</strong></td>   	    	    
        	<td style="border:none;"><strong>${_("Mese")}</strong></td>   	    	    
			<td style="border:none;"><strong>${_("Fatturato")}</strong></td>   	    	    
			<td style="border:none;"><strong>${_("Fatt.Netto")}</strong></td>   	    	    
			<td style="border:none;"><strong>${_("Fatturato Tot.")}</strong></td>   	    	    
	        <td style="border:none;"><strong>${_("Fatt.Netto Tot.")}</strong></td>   	    	    
        </tr>           
    </table> 
-->

    <p style="page-break-after: always"/>
    <br/>
    %endfor
</body>
</html>
