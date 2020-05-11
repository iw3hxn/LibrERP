## -*- coding: utf-8 -*-

<html>
<head>
    <style type="text/css">
            ${css}
        pre {
            font-family: helvetica;
            font-size: 12;
        }
    </style>
    <h1>${_("Inventory List")}</h1>
</head>
<body>
<style type="text/css">
    table {
        width: 100%;
        page-break-after: auto;
        border-collapse: collapse;
        cellspacing: "0";
        font-size: 10px;
    }

    td {
        margin: 0px;
        padding: 3px;
        border: 1px solid lightgrey;
        vertical-align: top;
    }

    th {
        border: 1px solid lightgrey
    }

    pre {
        font-family: helvetica;
        font-size: 15;
    }
</style>
    <%
        open = 0.0
        amount = 0.0
        sorted_objects = sorted(objects,key=lambda o: o.name )
    %>

<table>

    <thead>
    <tr>
        <th style="text-align:left;white-space:nowrap">${_("Number")}</th>
        <th style="text-align:left;white-space:nowrap">${_("Date")}</th>
    </tr>
    </thead>
    <tbody>
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
                    <th style="text-align:center;white-space:nowrap">${_("Code")}</th>
                    <th style="text-align:center;white-space:nowrap">${_("Name")}</th>
                    <th style="text-align:center;white-space:nowrap">${_("Lot")}</th>
                    <th style="text-align:center;white-space:nowrap">${_("Default Supplier")}</th>
                    <th style="text-align:center;white-space">${_("Quantity counted")}</th>
                    <th style="text-align:center;white-space">${_("Quantity computed")}</th>
                    <th style="text-align:center;white-space">${_("Diff")}</th>
                    <th style="text-align:center;white-space:nowrap">${_("Unit")}</th>
                    <th style="text-align:center;white-space">${_("Value")}</th>
                    <th style="text-align:center;white-space">${_("Total Value counted")}</th>
                    <th style="text-align:center;white-space">${_("Total Value computed")}</th>
                </tr>
                </thead>
                <tbody>
                    <%
                        loc_name = ''
                        total_product_qty = 0.0
                        total_product_qty_calc = 0.0
                        total_value = 0.0
                        total_value_computed = 0.0
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

                        <tr>

                            <td style="text-align:left;white-space:nowrap">${line.product_id.default_code or ''}</td>
                            <td style="text-align:left;white-space">${line.product_id.name}</td>
                            <td style="text-align:left;white-space:nowrap">${lot_name}</td>
                            <td style="text-align:left;white-space:nowrap">${line.product_id.prefered_supplier and line.product_id.prefered_supplier.name or ''}</td>
                            <td style="text-align:right;white-space:nowrap">${formatLang(line.product_qty)}</td>
                            %if line.product_qty < 0:
                                <td style="background-color: red;text-align:right;white-space:nowrap">${line.product_qty_calc}</td>
                            % else:
                                <td style="text-align:right;white-space:nowrap">${line.product_qty_calc}</td>
                            %endif
                            <td style="text-align:right;white-space:nowrap">${line.product_qty - line.product_qty_calc}</td>
                            <td style="text-align:left;white-space:nowrap">${line.product_uom.name}</td>
                            <td style="text-align:right;white-space:nowrap">${formatLang(line.product_value)}</td>
                            <td style="text-align:right;white-space:nowrap">${formatLang(line.total_value)}</td>
                            <td style="text-align:right;white-space:nowrap">${formatLang(line.total_value_computed)}</td>

                        </tr>
                        <%
                            total_product_qty+=line.product_qty
                            total_product_qty_calc+=line.product_qty_calc
                            total_value+=line.total_value
                            total_value_computed+=line.total_value_computed
                        %>
                    %endfor
                <tr>
                    <td></td>
                    <td></td>
                    <td style="text-align:left;white-space:nowrap">${_("Totals")}</td>
                    <td></td>
                    <td style="text-align:right;white-space:nowrap">${formatLang(total_product_qty)}</td>
                    <td style="text-align:right;white-space:nowrap">${formatLang(total_product_qty_calc)}</td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td style="text-align:right;white-space:nowrap">${formatLang(total_value)}</td>
                    <td style="text-align:right;white-space:nowrap">${formatLang(total_value_computed)}</td>
                </tr>
                </tbody>
            </table>

        %endfor
    </tbody>
</table>
</body>

</html>
