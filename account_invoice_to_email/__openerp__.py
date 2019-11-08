{
    'name': 'Email template extension',
    'version': '1.0.0.0',
    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'category': 'Marketing',
    'description': '''
        Module that extends the normal email_template to autmatically add the fields in the email creation
    ''',
    'depends': ['email_template'],
    'demo_xml': [],
    'init_xml': [
    ],
    'data': [
        'data/email_template_extension_data.xml',
    ],
    'auto_install': False,
    'installable': True,
}