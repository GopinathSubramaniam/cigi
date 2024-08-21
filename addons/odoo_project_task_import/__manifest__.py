# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Import Projects and Tasks from Excel ',
    'version': '9.2',
    'price': 9.0,
    'currency': 'EUR',
    'depends': [
        'project',
    ],
    'license': 'Other proprietary',
    'category': 'Projects/Projects',
    'summary': 'Allow you to import projects and tasks from Selected Excel File.',
    'description': """
project import
task import
tasks import
import project
import task
import tasks
project task import
import project task

            """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_project_task_import/694',#'https://youtu.be/slimW9Ky3jU',
    'data': [
       'security/ir.model.access.csv',
       'wizard/project_task_import_wizard_view.xml',
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
