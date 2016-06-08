<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body class="font_10" style="margin:0px;padding:0px;">

<br/>
<center><H1>SCADENZARIO</H1></center>
	<div class="clear"></div>

    <table id="content" class="font_9 w100">
        <tr>
			<!--td class="w10">Sezionale</td-->
			<td class="w35 bordi_arrotondati"><p style="text-align:left;">Partner</p></td>
			<td class="w10 bordi_arrotondati"><p style="text-align:left;">Scadenza</p></td>
			<td class="w10 bordi_arrotondati"><p style="text-align:left;">Fattura</p></td>
			<td class="w15 bordi_arrotondati"><p style="text-align:left;">Pagamento</p></td>
			<td class="w10 bordi_arrotondati"><p style="text-align:right; font-weight: bold;">Residuo</p></td>
			<td class="w10 bordi_arrotondati"><p style="text-align:right; font-weight: bold;">Dare</p></td>
			<td class="w10 bordi_arrotondati"><p style="text-align:right; font-weight: bold;">Avere</p></td>
		</tr>

		<% tot_importo = 0 %>
		<% tot_dare = 0 %>
		<% tot_avere = 0 %>
		<% data_scadenza = '0000-00-00' %>
		%for line in objects:
		%if line:    
			%if data_scadenza != (line.date_maturity or line.date):
				%if data_scadenza != '0000-00-00':
					<tr><td colspan=8><hr style="width:100%"></td></tr>
					<tr>
						<!--td class="w10">&nbsp;</td-->
						<td class="w35">&nbsp;</td>
						<td class="w10">&nbsp;</td>
						<td class="w10">&nbsp;</td>
						<td class="w15"><b>TOTALE SCADENZA</b></td>
						<td class="w10"><p style="text-align:right;"><b>${formatLang(parziale_importo, digits=get_digits(dp='Account'))}</b></p></td>
						<td class="w10"><p style="text-align:right;"><b>${formatLang(parziale_dare, digits=get_digits(dp='Account'))}</b></p></td>
						<td class="w10"><p style="text-align:right;"><b>${formatLang(parziale_avere, digits=get_digits(dp='Account'))}</b></p></td>
					</tr>
					<tr><td colspan=8>&nbsp;</td></tr>
				%endif
				<% parziale_importo = 0 %>
				<% parziale_dare = 0 %>
				<% parziale_avere = 0 %>
				<% data_scadenza = (line.date_maturity or line.date) %>
			%endif

			<tr>
				<!--td class="w10"><p style="text-align:left;">${line.invoice.journal_id and line.invoice.journal_id.code or ''}</p></td-->
				<td class="w35"><p style="text-align:left;">${line.partner_id.name or ''}</p></td>
				<td class="w10"><p style="text-align:left;">${line.date_maturity or line.date}</p></td>
				<td class="w10"><p style="text-align:left;">${line.invoice.supplier_invoice_number or line.name or ''} - ${line.invoice.number or ''}</p></td>
				<td class="w15"><p style="text-align:left;">${line.invoice.payment_term and line.invoice.payment_term.name or ''}</p></td>
				<td class="w10"><p style="text-align:right;">${formatLang(line.amount_residual or 0.00, digits=get_digits(dp='Account'))}</p></td>
				<td class="w10"><p style="text-align:right;">${formatLang(line.debit or 0.00, digits=get_digits(dp='Account'))}</p></td>
				<td class="w10"><p style="text-align:right;">${formatLang(line.credit or 0.00, digits=get_digits(dp='Account'))}</p></td>
			</tr>
			%if line.debit == 0.0:
				<%tot_importo -= line.amount_residual %>
				<% parziale_importo -= line.amount_residual %>
			%else:
				<%tot_importo += line.amount_residual %>
				<% parziale_importo += line.amount_residual %>
			%endif
			<% tot_dare += line.debit %>
			<% tot_avere += line.credit %>
			<% parziale_dare += line.debit %>
			<% parziale_avere += line.credit %>
		%endif
        %endfor
		<tr><td colspan=8><hr style="width:100%"></td></tr>
		<tr>
			<!--td class="w10">&nbsp;</td-->
			<td class="w35">&nbsp;</td>
			<td class="w10">&nbsp;</td>
			<td class="w10">&nbsp;</td>
			<td class="w15"><b>TOTALE SCADENZA</b></td>
			<td class="w10"><p style="text-align:right;"><b>${formatLang(parziale_importo, digits=get_digits(dp='Account'))}</b></p></td>
			<td class="w10"><p style="text-align:right;"><b>${formatLang(parziale_dare, digits=get_digits(dp='Account'))}</b></p></td>
			<td class="w10"><p style="text-align:right;"><b>${formatLang(parziale_avere, digits=get_digits(dp='Account'))}</b></p></td>
		</tr>
		<tr><td colspan=8>&nbsp;</td></tr>

        <tr><td colspan=8><hr style="width:100%"></td></tr>
		<tr style="height:100%">
			<!--td class="w10">&nbsp;</td-->
			<td class="w35">&nbsp;</td>
			<td class="w10">&nbsp;</td>
			<td class="w10">&nbsp;</td>
			<td class="w15"><b>TOTALE COMPLESSIVO</b></td>
			<td class="w10"><p style="text-align:right; font-weight: bold;">${formatLang(tot_importo, digits=get_digits(dp='Account'))}</p></td>
			<td class="w10"><p style="text-align:right; font-weight: bold;">${formatLang(tot_dare, digits=get_digits(dp='Account'))}</p></td>
			<td class="w10"><p style="text-align:right; font-weight: bold;">${formatLang(tot_avere, digits=get_digits(dp='Account'))}</p></td>
		</tr>
    </table>
    
	<div class="clear">&nbsp;</div>
	

</body>
</html>
