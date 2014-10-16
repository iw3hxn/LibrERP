## -*- coding: utf-8 -*-
<html>
<head>
    <style type="text/css">
        ${css}
        pre {font-family:helvetica; font-size:12;}
    </style>
<h1>${_("Inventory List")}</h1>
</head>
<body>
    <style  type="text/css">
     table {
       width: 100%;
       page-break-after:auto;
       border-collapse: collapse;
       cellspacing="0";
       font-size:10px;
           }
     td { margin: 0px; padding: 3px; border: 1px solid lightgrey;  vertical-align: top; }
     th { border:1px solid lightgrey}
     pre {font-family:helvetica; font-size:15;}
    </style>
<%
   open = 0.0
   amount = 0.0

   sorted_objects = sorted(objects,key=lambda o: o.name )
%>
    
<table>

        <thead >
          <tr>
            <th style="text-align:left;white-space:nowrap">${_("Number")}</th>
            <th style="text-align:left;white-space:nowrap">${_("Date")}</th>
         </tr>
        </thead>
        <tbody >
%for inv in sorted_objects :
          <tr>
            <th style="text-align:left;white-space:nowrap">${inv.name}</th>
            <th style="text-align:left;white-space:nowrap">${inv.date}</th>
           </tr>

<table>
<p>

</p>
        <thead>
          <tr>
            <th style="text-align:left;white-space:nowrap">${_("Code")}</th>
            <th style="text-align:left;white-space:nowrap">${_("Name")}</th>
            <th style="text-align:left;white-space:nowrap">${_("Lot")}</th>
            <th style="text-align:left;white-space">${_("Quantity counted")}</th>
            <!--th style="text-align:left;white-space">${_("Quantity computed")}</th-->
            <!--th style="text-align:left;white-space">${_("Diff")}</th-->
            <th style="text-align:left;white-space:nowrap">${_("Unit")}</th>
            <th style="text-align:left;white-space">${_("Value")}</th>
            <th style="text-align:left;white-space">${_("Total Value")}</th>
         </tr>
        </thead>
        <tbody>
<%
loc_name = ''
%>
%for line in inv.inventory_line_loc_id:
%if line.location_id.name != loc_name:
<tr>
<td/>
<td><b>
${line.location_id.name}
</b>
</td>
</tr>
%endif
<%
loc_name =  line.location_id.name 
lot_name = ''
if line.prod_lot_id.prefix:
    lot_name += line.prod_lot_id.prefix +'-'
if line.prod_lot_id.name:
    lot_name += line.prod_lot_id.name
%>
<% product_list = get_products() %>
          <tr>
            <td style="text-align:left;white-space:nowrap">${line.product_id.default_code or ''}</td>
            <td style="text-align:left;white-space">${line.product_id.name}</td>
            <td style="text-align:left;white-space:nowrap">${lot_name}</td>
            <td style="text-align:right;white-space:nowrap">${line.product_qty}</td>
            <td style="text-align:right;white-space:nowrap">${line.product_qty_calc}</td>
            <!--td style="text-align:right;white-space:nowrap">${line.product_qty-line.product_qty_calc}</td-->
            <!--td style="text-align:left;white-space:nowrap">${line.product_uom.name}</td-->
            <td style="text-align:right;white-space:nowrap">${formatLang(product_list[line.product_id.id])}</td>
            <td style="text-align:right;white-space:nowrap">${formatLang(line.product_qty * product_list[line.product_id.id])}</td>
         </tr>
%endfor
        </tbody>
</table>

%endfor
        </tbody>
</body>

</html>
