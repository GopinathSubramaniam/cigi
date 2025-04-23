# -- coding: utf-8 --
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2024 ZestyBeanz Technologies(<http://www.zbeanztech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, models
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super(SaleOrderLine, self).create(vals_list)
        if res.event_id and res.event_id.analytic_distribution:
            res.analytic_distribution = res.event_id.analytic_distribution
        return res
    
    def write(self, vals_list):
        res = super(SaleOrderLine, self).write(vals_list)
        if 'event_id' in vals_list and self.event_id and self.event_id.analytic_distribution:
            self.analytic_distribution = self.event_id.analytic_distribution
        return res

