# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2016-2018 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
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
    "name": """HR Attendance with Telegram Bot""",
    "summary": """Telegram Integration""",
    "category": "Telegram",
    "version": "3.0.3.0",

    "author": "Didotech SRL",
    "website": "https://www.didotech.com",
    "description": """
        Add function for sign in / out:
        * get_coordinates_distance
        * telegram_sign_in
        * telegram_sign_out
    """,
    "depends": [
        "telegram",
        "hr_attendance",
        "hr_attendance_position"
    ],
    "data": [
        "data/commands.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "external_dependencies": {
        "python": ['telepot'],
        "bin": []
    },
}
