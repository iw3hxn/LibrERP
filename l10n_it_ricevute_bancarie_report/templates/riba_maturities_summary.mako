<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body class="font_8" style="margin:0px;padding:0px;">
    
    <p class="w100 centered" style="font-size: 20px;"><b>${_("RIBA LIST MATURITIES SUMMARY")}</b></p>
    
    <table class="basic_table" style="font-size: 10px;">
    <%total=0%>
    <%res = group_riba_by_date(objects)%>
    %for due_date in sorted(res.keys()):
        <tr style="background-color: #cecece;">
            <td colspan="6" style="font-size: 14px;">${_("Due date:")} ${due_date}</td>
        </tr>
        <tr>
            <td>${_("LIST")}</td>
            <td>${_("ROW nr")}</td>
            <td>${_("CUSTOMER")}</td>
            <td>${_("RIF")}</td>
            <td>${_("DUE DATE")}</td>
            <td>${_("AMOUNT")}</td>
        </tr>
        <%group_amount=0%>
        %for l in res[due_date]:
            %if l.due_date == due_date:
                <%group_amount+=l.amount%>
                <tr>
                    <td>${l.distinta_id.name or ''}</td>
                    <td>${l.sequence or ''}</td>
                    <td>${l.partner_id.name or ''}</td>
                    <td>${l.invoice_number or ''}</td>
                    <td align="right">${l.due_date or ''}</td>
                    <td align="right">${l.amount or ''}</td>
                </tr>
            %endif
        %endfor
        <tr>
            <td colspan="5" align="right"><b>${_("DUE DATE TOTAL:")}</b></td>
            <td><b>${formatLang(group_amount)}</b></td>
            <%total+=group_amount%>
        </tr>
    %endfor
    <tr>
        <td colspan="4">&nbsp;</td>
        <td><b>${_("TOTAL:")}</b></td>
        <td><b>${formatLang(total)}</b></td>
    </tr>

    </table>
</body>
</html>
