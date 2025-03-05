{
    'name': 'Custom Event',
    'version': '1.0',
    'summary': 'Odoo 17 event customizations',
    'depends': ['web', 'event','website_event'],  # Add dependencies
    'data': [
        'views/event_form_inherit.xml',  # Add your view inheritance here
        'views/event_custom_form.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_event/static/src/js/*',
        ]
    },
    'installable': True,
    'application': False,
}
