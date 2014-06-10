{
    "name": "Email message customized",
    "version": "0.5",
    "author": "Matmoz d.o.o. (Didotech Group)",
    "website": "http://www.matmoz.si",
    "category": "Vertical Modules/Parametrization",
    "description":
        """Customized email message, unlocked some fields,
            html wysiwyg and WYSIWYG editor for emails""",
    "depends":
            [
                "mail",
                "base",
                "web_wysiwyg",
                "web_display_html"
            ],
        "init_xml": [],
        "demo_xml": [],
        "update_xml": ["email_wysiwyg_data.xml"],
        "installable": True
}
