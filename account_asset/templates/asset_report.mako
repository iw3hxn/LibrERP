<html>
<head>
    <style type="text/css">
        ${css}
        .left_with_line {
            text-align:left; vertical-align:text-top; border-top:1px solid #000; padding:5px
        }
        .right_with_line {
            text-align:right; vertical-align:text-top; border-top:1px solid #000; padding:5px
        }
        .left_without_line {
            text-align:left; vertical-align:text-top; padding:5px
        }
        .right_without_line {
            text-align:right; vertical-align:text-top; padding:5px
        }
    </style>
</head>
<body>
    <% setLang(objects[0].company_id.partner_id.lang or "en_US") %>
    <strong> Registro Cespiti ${type} anno ${fy_name}</strong>
    <table style="width:100%; font-size: xx-small;" cellspacing="0">
        <thead>
        <tr>
            <th class="left_without_line">Categoria</th>
            <th class="left_without_line">Descrizione</th>
            <th class="left_without_line">Anno acquisizione</th>
            <th class="left_without_line">Data acquisizione</th>
            <th class="left_without_line">Supplier Invoice</th>
            <th class="right_without_line">Costo storico di acquisto</th>
            <th class="right_without_line">Rivalutazioni o svalutazioni</th>
            <th class="right_without_line">Eliminazione</th>
            <th class="right_without_line">Fondo di amm.to fine esercizio precedente</th>
            <th class="right_without_line">Coefficiente di ammortamento</th>
            <th class="right_without_line">Quota annuale di ammortamento</th>
            <th class="right_without_line">Residuo ammortizzabile</th>
        </tr>
        </thead>
        <tbody>
        %for object in objects:
          <tr>
            <td class="left_with_line">
            ${object.category_id.name or '' | entity}
            </td>
            <td class="left_with_line">
            ${object.name or ''| entity}
            </td>
            <td class="left_with_line">
            ${asset_start_year(object) or ''| entity}
            </td>
            <td class="left_with_line">
            ${formatLang(object.date_start, date=True) or ''| entity}
            </td>
            <td class="left_with_line">
                %for invoiced_line in invoiced_asset_lines(object):
                    %if invoiced_line:
                        N. ${invoiced_line['supplier_invoice_number'] or ''| entity} - Date: ${invoiced_line['invoice_date'] or ''| entity}
                        <br/>
                        Partner: ${invoiced_line['partner_name'] or ''| entity}
                    %endif
                %endfor
            </td>
            <td class="right_with_line">
            ${object.purchase_value or ''| entity}
            </td>
            <td class="right_with_line">
            ${object.increase_value or ''| entity} <br/>
            ${- object.decrease_value or ''| entity}
            </td>
            <td class="right_with_line">
            ${object.remove_value or ''| entity}
            ${object.date_remove or ''| entity}
            </td>
            <td class="right_with_line">
            ${object.value_depreciated or ''| entity}
            </td>
            <td class="right_with_line">
            ${object.method_number_percent or object.method_number or ''| entity}
            </td>
            <td class="right_with_line">
            ${asset_fy_depreciation_amount(object) or ''| entity}
            </td>
            <td class="right_with_line">
            ${object.value_residual or ''| entity}
            </td>
          </tr>
        %endfor
        </tbody>
    </table>

</body>
</html>
