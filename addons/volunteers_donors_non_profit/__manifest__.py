# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full
# copyright and licensing details.

{
    'name': 'Volunteers and Donors Management',
    'version': '10.1.2',
    'price': 39.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Operations/Project',
    'summary': 'Volunteers and Donors Management',
    'description': """
Volunteers Donors Non Profit
Volunteers and Donors Management in Odoo
Non Profit Organization Management
Volunteer Management
Donor Management
This app allows you to manage your volunteers and donors in Odoo and allows you to create projects and tasks with volunteers and activities volunteers can do on dates. It also allows you to select volunteer and donor details on CRM of lead / pipelines.
Allow you to create and manage Volunteers and Donors in Odoo. Please note that we have used the Odoo res.partner model to allow you to add volunteers and donors.
Allow you to add Volunteers Types ,Volunteer Skills.
Allow you to add Donor Types.
Project form of Odoo now will allow also to select volunteers of that project and activities of volunteers by dates.
Project pdf report with volunteers details.
Task Form View of Odoo with volunteers.
CRM Lead/Pipeline form with Donor and Volunteer details.
Allow you to share tasks to volunteer on the portal of your website (Odoo standard out of box feature).

""",
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img.png'],
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/volunteers_donors_non_profit/183',#'https://youtu.be/t9Ec8V03r2A',
    'depends': [
        'crm',
        'print_project_report',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/donor_type_view.xml',
        'views/res_partner_view.xml',
        'views/volunteer_skills_view.xml',
        'views/volunteer_type_view.xml',
        
        'views/crm_lead_view.xml',
        'views/volunteer_working_details_view.xml',
        'views/project_project_view.xml',
        'views/project_report.xml',
        'views/campaign_templates.xml',
        'views/custom_payment_receipt_report.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'volunteers_donors_non_profit/static/src/css/volunteer_management.css',
            'volunteers_donors_non_profit/static/src/js/volunteer_management.js',
            'https://checkout.razorpay.com/v1/checkout.js'
        ],
        
    },
    
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
