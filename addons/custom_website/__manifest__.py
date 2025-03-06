{
    'name': 'Custom Website',
    'version': '1.0',
    'summary': 'Odoo 17 website chagnes',
    'depends': ['web', 'website'],  # Add dependencies
    'data': [
        'views/template.xml'
    ],
    'installable': True,
    'application': False,
}
