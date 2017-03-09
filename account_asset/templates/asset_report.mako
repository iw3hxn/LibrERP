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
    <strong> Registro Cespiti anno ${fy_name}</strong>
    %if type=='simulated':
    <strong> - SIMULATO PER USO INTERNO - </strong>
    %endif
    %if state=='draft':
    <strong> - PER USO INTERNO - CESPITI IN STATO BOZZA </strong>
    %endif
    <table style="width:100%; font-size: xx-small;" cellspacing="0">
        <thead>
        <tr>
            <th class="left_without_line">Rif.</th>
            <th class="left_without_line">Descrizione</th>
            <th class="left_without_line">Anno acquisizione</th>
            <th class="left_without_line">Data acquisizione</th>
            <th class="left_without_line">Supplier Invoice</th>
            <th class="right_without_line">Costo storico di acquisto</th>
            <th class="right_without_line">Rivalutazioni o svalutazioni</th>
            <th class="right_without_line">Eliminazione / Vendita</th>
            <th class="right_without_line">Fondo di amm.to fine esercizio precedente</th>
            <th class="right_without_line">Coefficiente di ammortamento</th>
            <th class="right_without_line">Quota annuale di ammortamento</th>
            <th class="right_without_line">Fondo di amm.to fine esercizio in corso</th>
            <th class="right_without_line">Residuo ammortizzabile</th>
        </tr>
        </thead>
        <tbody>
        <%ctgs = ctg_total(category_ids)%>
        %for ctg in category_ids:
        %for object in objects:
        %if object.category_id.id == ctg:
        <%depr_amount= asset_depreciation_amount(object)%>
          <tr>
            <td class="left_with_line">
            ${object.code or ''| entity}
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
            ${formatLang(asset_fy_increase_decrease_amount(object)) or ''| entity} <br/>
            </td>
            <td class="right_with_line">
            ${formatLang(asset_remove_amount(object)) or ''| entity}
            %if object.date_remove[:4] <= fy_name:
            ${object.date_remove or ''| entity}
            %endif
            </td>
            <td class="right_with_line">
            ${formatLang(depr_amount[object.id]['depreciated_value']) or ''| entity}
            </td>
            <td class="right_with_line">
            ${formatLang(depr_amount[object.id]['factor']) or ''| entity}
            </td>
            <td class="right_with_line">
            ${formatLang(depr_amount[object.id]['amount']) or ''| entity}
            </td>
            <td class="right_with_line">
            ${formatLang(depr_amount[object.id]['depreciated_value'] + depr_amount[object.id]['amount']) or ''| entity}
            </td>
            <td class="right_with_line">
            ${formatLang(depr_amount[object.id]['remaining_value']) or ''| entity}
            </td>
          </tr>
        %endif
        %endfor

          <tr>
            <td class="left_with_line"></td>
            <td class="left_with_line">
            <strong>Totali</strong>
            <strong>${ctgs[ctg]['name'] or ''| entity}</strong>
            </td>
            <td class="left_with_line"></td>
            <td class="left_with_line"></td>
            <td class="left_with_line"></td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs[ctg]['purchase_value']) or ''| entity}</strong>
            </td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs[ctg]['increase_decrease_value']) or ''| entity}</strong>
            </td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs[ctg]['remove_value']) or ''| entity}</strong>
            </td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs[ctg]['value_depreciated']) or ''| entity}</strong>
            </td>
            <td class="right_with_line"></td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs[ctg]['value_depreciation']) or ''| entity}</strong>
            </td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs[ctg]['value_depreciated'] + ctgs[ctg]['value_depreciation']) or ''| entity}</strong>
            </td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs[ctg]['value_residual']) or ''| entity}</strong>
            </td>
          </tr>

        %endfor

          <tr>
            <td class="left_with_line"></td>
            <td class="left_with_line">
            <strong>Totali</strong>
            </td>
            <td class="left_with_line"></td>
            <td class="left_with_line"></td>
            <td class="left_with_line"></td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs['total']['purchase_value']) or ''| entity}</strong>
            </td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs['total']['increase_decrease_value']) or ''| entity}</strong>
            </td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs['total']['remove_value']) or ''| entity}</strong>
            </td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs['total']['value_depreciated']) or ''| entity}</strong>
            </td>
            <td class="right_with_line"></td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs['total']['value_depreciation']) or ''| entity}</strong>
            </td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs['total']['value_depreciated'] + ctgs['total']['value_depreciation']) or ''| entity}</strong>
            </td>
            <td class="right_with_line">
            <strong>${formatLang(ctgs['total']['value_residual']) or ''| entity}</strong>
            </td>
          </tr>
        </tbody>
    </table>

</body>
</html>
