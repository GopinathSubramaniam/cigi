# -*- coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "Project Gantt View / Gantt View for Project",
    "summary": "This module provides  the Gantt View for Scheduling in Project Module",
    "version": "17.1",
    "description": """
        This module provides  the Gantt View for Scheduling in Project Module
        Gantt View
        Base Gantt View
        Base for Gantt View
        View Gantt
        Gantt
        Gantt Base for odoo
        odoo Gantt View  
        Project Gantt
        Project Gantt View
        Gantt view for Project
        Gantt Project View      
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/web_base_project_gantt_view.png"],
    "category": "Project",
    "depends": [
        "web",
        "project",
    ],
    "data": [
        "views/project_views.xml",
    ],
    "assets": {
        "web.assets_backend": [            
            "/web_base_project_gantt_view/static/src/lib/*.*",
            "/web_base_project_gantt_view/static/src/css/*.*",
            "/web_base_project_gantt_view/static/src/js/*.*",
        ],
    },
    "installable": True,
    "application": True,
    "price"                 :  14.00,
    "currency"              :  "EUR",
    "pre_init_hook"         :  "pre_init_check",
}
