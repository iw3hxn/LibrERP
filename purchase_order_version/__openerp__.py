# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Alejandro Núñez Liz$
#    $Omar Castiñeira Saavedra$
#    Copyright (C) 2013-2014 Didotech srl (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Purchase order versions ",
    "description": """
        Módulo que permite la creación de versiones de pedidos de ventas.
        Añade a los pedidos de ventas el campo activo, así como la referancia a la versión original del pedido de venta y el listado de versiones anteriores.
        Botón para realizar una nueva versión del pedido de venta, todo en la vista formulario.
        Modifica el análisis de ventas para poder filtrar por pedidos de venta activos ( por defecto ) e inactivos.
        
        El filtro por pedido de venta activo, no funciona en la web.
        """,
    "version": "3.4.14.10",
    "author": "Pexego, Didotech SRL",
    "website": "http://www.pexego.es",
    "category": "Sales/Version",
    "depends": [
        'base',
        'sale',
        'core_extended'
    ],
    "init": [],
    "demo": [],
    "data": [
        'views/purchase_order_view.xml',
#        'report/sale_report_view.xml',
    ],
    "installable": True,
    'active': False
}
