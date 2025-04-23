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
from odoo import models,fields
from odoo.exceptions import ValidationError



class AccountMove(models.Model):
    _inherit = 'account.move'

    source_move_id = fields.Many2one('account.move', string="Source Move", help="Original Move from which this was allocated")
    allocated_move_ids = fields.One2many('account.move', 'source_move_id', string="Allocated Entries")
    do_not_allocate = fields.Boolean(
        string='Do Not Allocate',
        help='Tick to bypass allocation requirement for this entry.',
        
    )
    
    
    def action_view_allocated_moves(self):
        """Opens the tree view of allocated moves related to this record."""
        action = {
            'name': 'Allocated Moves',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.allocated_move_ids.ids)],
            'context': {'default_parent_id': self.id},
        }
        return action
        
    def button_cancel(self):
        res = super(AccountMove, self).button_cancel()
        for move in self.allocated_move_ids:
            move.button_cancel()  
            move.write({'source_move_id': False})  
        self.write({'allocated_move_ids': [(5, 0, 0)]})
        return res

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        for move in self.allocated_move_ids:
            move.button_cancel()  
            move.write({'source_move_id': False})  
        self.write({'allocated_move_ids': [(5, 0, 0)]})
        return res
    def action_post(self):
        for move in self:
            if not move.do_not_allocate:
                unallocated_accounts = []
                for line in move.line_ids:
                    if line.allocate_entries and not move.allocated_move_ids:
                        account_info = f"[{line.account_id.code}] {line.account_id.name}"
                        if account_info not in unallocated_accounts:
                            unallocated_accounts.append(account_info)
                if unallocated_accounts:
                    error_message = (
                        "Allocation Required for the following Accounts:\n" +
                        "\n".join(unallocated_accounts)
                    )
                    raise ValidationError(error_message)
        return super(AccountMove, self).action_post()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    
    allocate_entries = fields.Boolean(string='Allocate Entries',related="account_id.allocate_entries")


    def action_allocate(self):
        """Open the allocation wizard with pre-filled data."""
        self.ensure_one()
        move = self.move_id 
        company = self.company_id
        allocation_journal = company.allocation_journal
        if not allocation_journal and company.parent_id:
            allocation_journal = company.parent_id.allocation_journal
        return {
            'type': 'ir.actions.act_window',
            'name': 'Allocate Journal Entries',
            'res_model': 'account.move.allocate.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('zb_account_entry_allocation.view_account_move_allocate_wizard').id,
            'target': 'new',
            'context': {
                'default_total_amount': abs(self.balance),
                'default_partner_id': self.partner_id.id,
                'default_company_id': move.company_id.id,
                'default_journal_id': allocation_journal.id if allocation_journal else False,
               
            }
        }
    