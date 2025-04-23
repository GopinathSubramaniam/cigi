# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2024 ZestyBeanz Technologies.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
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
    'name': 'Accounting Entry Allocation',
    'version': '17.0.0.0.2',
    'summary': 'This module manage entries allocation to future dates(For eg- Prepaid Expense Allocation )',
    'description': """This module manage entries allocation to future dates(For eg- Prepaid Expense Allocation )""",
    'category': 'Accounting',
    'author': 'ZestyBeanz Technologies.',
    'website': 'www.zbeanztech.com',
    'depends': ['account'],
    'data': [
         'security/ir.model.access.csv',
          'wizard/account_entry_allocation_wiz_view.xml',
         'views/account_account_view.xml',
          'views/account_move_view.xml',
          'views/res_company_view.xml',
        ],
    'assets': {
       
    },
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}













