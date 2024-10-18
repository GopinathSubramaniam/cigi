{
    'name': 'Custom Event',
    'version': '1.0',
    'summary': 'Odoo 17 event customizations',
    'depends': ['event','website_event'],  # Add dependencies
    'data': [
        'views/event_form_inherit.xml',  # Add your view inheritance here
    ],
    'installable': True,
    'application': False,
}
