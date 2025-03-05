{
    'name': 'Custom Contact',
    'version': '1.0',
    'summary': 'Odoo 17 contact customizations',
    'depends': ['web', 'contacts'],  # Add dependencies
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
    ],
    
    'installable': True,
    'application': False,
}
