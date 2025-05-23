from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import json
import io
from odoo.tools import date_utils
import base64

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

DATE_DICT = {
    '%m/%d/%Y' : 'mm/dd/yyyy',
    '%Y/%m/%d' : 'yyyy/mm/dd',
    '%m/%d/%y' : 'mm/dd/yy',
    '%d/%m/%Y' : 'dd/mm/yyyy',
    '%d/%m/%y' : 'dd/mm/yy',
    '%d-%m-%Y' : 'dd-mm-yyyy',
    '%d-%m-%y' : 'dd-mm-yy',
    '%m-%d-%Y' : 'mm-dd-yyyy',
    '%m-%d-%y' : 'mm-dd-yy',
    '%Y-%m-%d' : 'yyyy-mm-dd',
    '%f/%e/%Y' : 'm/d/yyyy',
    '%f/%e/%y' : 'm/d/yy',
    '%e/%f/%Y' : 'd/m/yyyy',
    '%e/%f/%y' : 'd/m/yy',
    '%f-%e-%Y' : 'm-d-yyyy',
    '%f-%e-%y' : 'm-d-yy',
    '%e-%f-%Y' : 'd-m-yyyy',
    '%e-%f-%y' : 'd-m-yy'
}

FETCH_RANGE = 2000

class InsPartnerLedger(models.TransientModel):
    _name = "ins.partner.ledger"

    @api.onchange('date_range', 'financial_year')
    def onchange_date_range(self):
        if self.date_range:
            date = datetime.today()
            if self.date_range == 'today':
                self.date_from = date.strftime("%Y-%m-%d")
                self.date_to = date.strftime("%Y-%m-%d")
            if self.date_range == 'this_week':
                day_today = date - timedelta(days=date.weekday())
                self.date_from = (day_today - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
                self.date_to = (day_today + timedelta(days=6)).strftime("%Y-%m-%d")
            if self.date_range == 'this_month':
                self.date_from = datetime(date.year, date.month, 1).strftime("%Y-%m-%d")
                self.date_to = datetime(date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")
            if self.date_range == 'this_quarter':
                if int((date.month - 1) / 3) == 0:  # First quarter
                    self.date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 3, calendar.mdays[3]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 1:  # Second quarter
                    self.date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 6, calendar.mdays[6]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 2:  # Third quarter
                    self.date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 9, calendar.mdays[9]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 3:  # Fourth quarter
                    self.date_from = datetime(date.year, 10, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 12, calendar.mdays[12]).strftime("%Y-%m-%d")
            if self.date_range == 'this_financial_year':
                if self.financial_year == 'january_december':
                    self.date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 12, 31).strftime("%Y-%m-%d")
                if self.financial_year == 'april_march':
                    if date.month < 4:
                        self.date_from = datetime(date.year - 1, 4, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year, 3, 31).strftime("%Y-%m-%d")
                    else:
                        self.date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year + 1, 3, 31).strftime("%Y-%m-%d")
                if self.financial_year == 'july_june':
                    if date.month < 7:
                        self.date_from = datetime(date.year - 1, 7, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year, 6, 30).strftime("%Y-%m-%d")
                    else:
                        self.date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year + 1, 6, 30).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(days=1))
            if self.date_range == 'yesterday':
                self.date_from = date.strftime("%Y-%m-%d")
                self.date_to = date.strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(days=7))
            if self.date_range == 'last_week':
                day_today = date - timedelta(days=date.weekday())
                self.date_from = (day_today - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
                self.date_to = (day_today + timedelta(days=6)).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(months=1))
            if self.date_range == 'last_month':
                self.date_from = datetime(date.year, date.month, 1).strftime("%Y-%m-%d")
                self.date_to = datetime(date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(months=3))
            if self.date_range == 'last_quarter':
                if int((date.month - 1) / 3) == 0:  # First quarter
                    self.date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 3, calendar.mdays[3]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 1:  # Second quarter
                    self.date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 6, calendar.mdays[6]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 2:  # Third quarter
                    self.date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 9, calendar.mdays[9]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 3:  # Fourth quarter
                    self.date_from = datetime(date.year, 10, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 12, calendar.mdays[12]).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(years=1))
            if self.date_range == 'last_financial_year':
                if self.financial_year == 'january_december':
                    self.date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 12, 31).strftime("%Y-%m-%d")
                if self.financial_year == 'april_march':
                    if date.month < 4:
                        self.date_from = datetime(date.year - 1, 4, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year, 3, 31).strftime("%Y-%m-%d")
                    else:
                        self.date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year + 1, 3, 31).strftime("%Y-%m-%d")
                if self.financial_year == 'july_june':
                    if date.month < 7:
                        self.date_from = datetime(date.year - 1, 7, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year, 6, 30).strftime("%Y-%m-%d")
                    else:
                        self.date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year + 1, 6, 30).strftime("%Y-%m-%d")

    @api.model
    def _get_default_date_range(self):
        return self.env.company.date_range

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, 'Partner Ledger'))
        return res

    financial_year = fields.Selection(
        [('april_march', '1 April to 31 March'),
         ('july_june', '1 july to 30 June'),
         ('january_december', '1 Jan to 31 Dec')],
        string='Financial Year', default=lambda self: self.env.company.financial_year, required=True)

    date_range = fields.Selection(
        [('today', 'Today'),
         ('this_week', 'This Week'),
         ('this_month', 'This Month'),
         ('this_quarter', 'This Quarter'),
         ('this_financial_year', 'This financial Year'),
         ('yesterday', 'Yesterday'),
         ('last_week', 'Last Week'),
         ('last_month', 'Last Month'),
         ('last_quarter', 'Last Quarter'),
         ('last_financial_year', 'Last Financial Year')],
        string='Date Range', default=_get_default_date_range
    )
    target_moves = fields.Selection(
        [('all_entries', 'All entries'),
         ('posted_only', 'Posted Only')], string='Target Moves',
        default='posted_only', required=True
    )
    display_accounts = fields.Selection(
        [('all', 'All'),
         ('with_transaction', 'With transaction')], string='Display Partners',
        default='with_transaction', required=True
    )
    balance_less_than_zero = fields.Boolean(string='With balance less than zero')
    balance_greater_than_zero = fields.Boolean(string='With balance greater than zero')
    account_type = fields.Selection(
        [('any', 'Any'),
         ('asset_receivable', 'Receivable Only'),
         ('liability_payable', 'Payable only')],
        string='Account Type', default='any'
    )
    initial_balance = fields.Boolean(
        string='Include Initial Balance', default=True
    )
    include_initial_balance = fields.Selection(
        [
            ('yes', 'Yes'),
            ('no', 'NO')
        ], default='yes', string="Include Initial Balance"
    )
    reconciled = fields.Selection([('any', 'Any'),
                                   ('reconciled','Reconciled Only'),
                                   ('unreconciled','Unreconciled Only')],
                                  string='Reconcile Type', default='any')
    date_from = fields.Date(
        string='Start date',
    )
    date_to = fields.Date(
        string='End date',
    )
    account_ids = fields.Many2many(
        'account.account', string='Accounts'
    )
    journal_ids = fields.Many2many(
        'account.journal', string='Journals',
    )
    partner_ids = fields.Many2many(
        'res.partner', string='Partners'
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    include_details = fields.Boolean(
        string='Include Details', default=True
    )
    partner_category_ids = fields.Many2many(
       'res.partner.category', string='Partner Tag',
    )
    account_tag_ids = fields.Many2many(
        'account.account.tag', string='Account Tags'
    )

    @api.model
    def create(self, vals):
        ret = super(InsPartnerLedger, self).create(vals)
        return ret

    def write(self, vals):
        ret = super(InsPartnerLedger, self).write(vals)
        return ret

    def validate_data(self):
        if self.date_from > self.date_to:
            raise ValidationError(_('"Date from" must be less than or equal to "Date to"'))
        return True

    ################################################################################
    ############################# Core Methods Start ###############################
    ################################################################################

    def prepare_where(self, mode='strict'):
        '''
        :param mode: 'strict', 'initial', 'ending'
        :return:
        '''
        where = 'WHERE (1=1) '
        if self.journal_ids:
            where += ' AND j.id IN %s ' % str(tuple(self.journal_ids.ids) + tuple([0]))
        if self.account_ids:
            where += ' AND a.id IN %s ' % str(tuple(self.account_ids.ids) + tuple([0]))
        if self.company_id:
            where += ' AND l.company_id = %s ' % self.company_id.id
        if self.target_moves == 'posted_only':
            where += " AND m.state = 'posted' "
        if self.reconciled == 'reconciled':
            where += " AND l.reconciled = TRUE"
        if self.reconciled == 'unreconciled':
            where += " AND l.reconciled = FALSE"
        if self.account_type == 'asset_receivable':
            where += " AND a.account_type = 'asset_receivable'"
        if self.account_type == 'liability_payable':
            where += " AND a.account_type = 'liability_payable'"

        if mode == 'strict':
            where += ''' AND l.date >= '%s' AND l.date <= '%s' ''' % (self.date_from, self.date_to)
        elif mode == 'initial':
            where += ''' AND l.date < '%s' ''' % self.date_from
        else:
            where += ''' AND l.date <= '%s' ''' % self.date_to

        return where

    def prepare_from(self):
        sql_from = '''
            FROM account_move_line l
            JOIN account_move m ON (l.move_id=m.id)
            JOIN account_account a ON (l.account_id=a.id)
            --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
            LEFT JOIN res_currency c ON (l.currency_id=c.id)
            LEFT JOIN res_partner p ON (l.partner_id=p.id)
            JOIN account_journal j ON (l.journal_id=j.id)
        '''
        return sql_from

    def prepare_main_lines(self):
        '''
        It is the method for showing summary details of each accounts. Just basic details to show up
        Three sections,
        1. Initial Balance
        2. Current Balance
        3. Final Balance
        :return:
        '''
        cr = self.env.cr

        partner_company_domain = [('parent_id', '=', False),
                                  '|',
                                  ('company_id', '=', self.env.company.id),
                                  ('company_id', '=', False)]

        if self.partner_category_ids:
            partner_company_domain.append(('category_id', 'in', self.partner_category_ids.ids))
        if self.partner_ids:
            partner_company_domain.append(('id', 'in', self.partner_ids.ids))

        partner_ids = self.env['res.partner'].search(partner_company_domain, order='name asc')
        pl_lines = []
        for partner in partner_ids:

            result = {
                'id_list': [],
                'size': 0,
                'debit': 0,
                'credit': 0,
                'balance': 0
            }
            # Current
            sql = ('''
                SELECT
                    array_agg(l.id) AS id_list,
                    COUNT(l.id) AS size,
                    COALESCE(SUM(l.debit),0) AS debit, 
                    COALESCE(SUM(l.credit),0) AS credit, 
                    COALESCE(SUM(l.debit - l.credit),0) AS balance,
                    EXTRACT(HOUR FROM CURRENT_TIME)::TEXT || ':' ||
                    EXTRACT(MINUTE FROM CURRENT_TIME)::TEXT || ':' ||
                    EXTRACT(SECOND FROM CURRENT_TIME)::TEXT || ':' || '%s' AS time_string
                ''' % str(partner.id) + self.prepare_from() + self.prepare_where(mode='strict') +
                   ''' AND l.partner_id = %s 
                   ''' % partner.id)
            print("Q", sql)
            cr.execute(sql)
            res = cr.dictfetchone() or {}

            result.update(res)
            # Extra args
            result.update(
                {
                    'partner_id': partner.id,
                    'partner_name': partner.name,
                    'currency_id': self.currency_id.id,
                }
            )

            if self.display_accounts == 'with_transaction' and (
                    self.currency_id.is_zero(result.get('debit')) and self.currency_id.is_zero(result.get('credit'))
            ):
                continue

            pl_lines.append(result)
        return pl_lines

    def prepare_detailed_lines(self, move_line_ids=[], partner_id=False):
        cr = self.env.cr
        final_list = []
        lang_code = self.env.user.lang
        # Initial
        if self.include_initial_balance == 'yes':
            where_initial = self.prepare_where(mode='initial')
            sql = ('''
                    SELECT
                        'initial' AS ttype,
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                        ''' + self.prepare_from() + where_initial +
                   ''' AND l.partner_id = %s 
          ''' % partner_id)
            cr.execute(sql)
            dt_initial = cr.dictfetchone()
            dt_initial.update({'lid': str(partner_id) + 'initial'})
            final_list.append(dt_initial)

        # Current
        where_current = self.prepare_where(mode='strict') + ' AND l.id in %s ' % str(
            tuple(move_line_ids) + tuple([0]))
        sql = ('''
                SELECT
                    'strict' AS ttype,
                    l.id AS lid,
                    l.date AS ldate, 
                    l.matching_number,
                    l.date_maturity,
                    j.code AS lcode,
                    a.name ->> '%s' AS account_name,
                    a.code AS account_code,
                    m.name AS move_name,
                    m.id AS move_id,
                    l.currency_id AS currency_id,
                    l.name AS lname,
                    CASE
                        WHEN l.currency_id <> l.company_currency_id THEN l.amount_currency
                        ELSE 0
                    END AS amount_currency,
                    l.debit AS debit,
                    l.credit AS credit,
                    l.balance AS balance
                    ''' % lang_code + self.prepare_from() + where_current +
               ''' AND l.partner_id = %s 
               GROUP BY
                   l.date, l.id, m.id, l.matching_number,
                    l.date_maturity, j.code, a.name, l.currency_id, a.code, m.name, l.name, l.debit, l.credit, l.amount_currency
               ORDER BY l.date
           ''' % partner_id)
        cr.execute(sql)
        final_list += cr.dictfetchall()
        # Ending
        if self.include_initial_balance == 'yes':
            where_ending = self.prepare_where(mode='ending')
            sql = ('''
                    SELECT
                        'ending' AS ttype,
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                        ''' + self.prepare_from() + where_ending +
                   ''' AND l.partner_id = %s 
               ''' % partner_id)
            cr.execute(sql)
            dt_ending = cr.dictfetchone()
            dt_ending.update({'lid': str(partner_id) + 'ending'})
            final_list.append(dt_ending)
        return final_list

    def prepare_values_for_component(self):
        self.onchange_date_range()
        model_id = self.env['ir.model'].sudo().search([('model', '=', 'ins.partner.ledger')], limit=1)

        date_range = {'choices': [], 'selectedValue': {'value': self.date_range}}
        target_moves = {'choices': [], 'selectedValue': {'value': self.target_moves}}
        display_accounts = {'choices': [], 'selectedValue': {'value': self.display_accounts}}
        include_initial_balance = {'choices': [], 'selectedValue': {'value': self.include_initial_balance}}
        reconciled = {'choices': [], 'selectedValue': {'value': self.reconciled}}
        account_type = {'choices': [], 'selectedValue': {'value': self.account_type}}

        for field in model_id.field_id:
            if field.name == 'date_range':
                date_range['choices'] = [{'value': a.value, 'label': a.name} for a in field.selection_ids]
            if field.name == 'target_moves':
                target_moves['choices'] = [{'value': a.value, 'label': a.name} for a in field.selection_ids]
            if field.name == 'display_accounts':
                display_accounts['choices'] = [{'value': a.value, 'label': a.name} for a in field.selection_ids]
            if field.name == 'include_initial_balance':
                include_initial_balance['choices'] = [{'value': a.value, 'label': a.name} for a in
                                                      field.selection_ids]
            if field.name == 'reconciled':
                reconciled['choices'] = [{'value': a.value, 'label': a.name} for a in
                                                      field.selection_ids]
            if field.name == 'account_type':
                account_type['choices'] = [{'value': a.value, 'label': a.name} for a in
                                                      field.selection_ids]
        return {
            'defaultAccountValues': [{'value': a.id, 'label': a.name, 'code': a.code} for a in self.account_ids],
            'defaultJournalValues': [{'value': a.id, 'label': a.name, 'code': a.code} for a in self.journal_ids],
            'defaultAccountTagValues': [{'value': a.id, 'label': a.name, 'code': a.code} for a in self.account_tag_ids],
            'defaultPartnerValues': [{'value': a.id, 'label': a.name} for a in self.partner_ids],
            'defaultPartnerTagsValues': [{'value': a.id, 'label': a.name} for a in self.partner_category_ids],
            'date_from': self.date_from,
            'date_to': self.date_to,
            'date_range': date_range,
            'target_moves': target_moves,
            'include_initial_balance': include_initial_balance,
            'display_accounts': display_accounts,
            'reconciled': reconciled,
            'account_type': account_type

        }

    def update_values_from_component(self, vals):
        update_dict = {}
        model_id = self.env['ir.model'].sudo().search([('model', '=', 'ins.partner.ledger')], limit=1)
        for field in model_id.field_id:
            if field.name in vals.keys():
                if field.ttype == 'many2many':
                    if vals[field.name]:
                        update_dict.update({field.name: [int(a['value']) for a in vals[field.name]]})
                    else:
                        update_dict.update({field.name: [(5,)]})
                if field.ttype == 'selection':
                    update_dict.update({field.name: vals[field.name]['selectedValue']['value']})
                if field.ttype == 'date':
                    update_dict.update({field.name: vals[field.name]})
        self.write(update_dict)
        self.onchange_date_range()
        return self.prepare_main_lines()
        # Query the account details and share here..

    ################################################################################
    ############################# Core Methods END #################################
    ################################################################################

    def action_pdf(self):
        return self.env.ref(
            'account_dynamic_reports'
            '.action_print_partner_ledger').with_context(landscape=True).report_action(
            self, data={})

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Partner Ledger View',
            'tag': 'account_dynamic_reports.action_partner_ledger',
            'context': {'wizard_id': self.id},
            'params': {
                'wizard_id': self.id
            }
        }
        return res

    def action_xlsx(self):
        data = self.read()[0]
        # Initialize
        #############################################################
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Partnr Ledger')
        sheet.set_zoom(95)
        sheet_2 = workbook.add_worksheet('Filters')
        sheet_2.protect()

        # Get record and data
        record = self.env['ins.partner.ledger'].browse(data.get('id', [])) or False

        filter = record.prepare_values_for_component()
        account_lines = record.prepare_main_lines()

        # Formats
        ############################################################
        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 12)
        sheet.set_column(2, 2, 12)
        sheet.set_column(3, 3, 12)
        sheet.set_column(4, 4, 13)
        sheet.set_column(5, 5, 13)
        sheet.set_column(6, 6, 13)
        sheet.set_column(7, 7, 13)
        sheet.set_column(8, 8, 13)
        sheet.set_column(9, 9, 13)

        sheet_2.set_column(0, 0, 35)
        sheet_2.set_column(1, 1, 25)
        sheet_2.set_column(2, 2, 25)
        sheet_2.set_column(3, 3, 25)
        sheet_2.set_column(4, 4, 25)
        sheet_2.set_column(5, 5, 25)
        sheet_2.set_column(6, 6, 25)

        sheet.freeze_panes(4, 0)

        sheet.screen_gridlines = False
        sheet_2.screen_gridlines = False

        format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font': 'Arial',
            'border': False
        })
        format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font': 'Arial',
            'align': 'center',
            # 'border': True
        })
        content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            'border': True,
            'text_wrap': True,
        })
        content_header_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'border': True,
            'align': 'center',
            'font': 'Arial',
        })
        line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'bottom': True,
        })
        line_header_left = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'top': True,
            'font': 'Arial',
            'bottom': True,
        })
        line_header_light = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            # 'top': True,
            # 'bottom': True,
            'font': 'Arial',
            'text_wrap': True,
            'valign': 'top'
        })
        line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            # 'top': True,
            # 'bottom': True,
            'font': 'Arial',
            'align': 'center',
        })
        line_header_light_initial = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            'bottom': True,
            'text_wrap': True,
            'valign': 'top'
        })
        line_header_light_initial_bold = workbook.add_format({
            'bold': True,
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'text_wrap': True,
            'valign': 'top'
        })
        line_header_light_ending = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'text_wrap': True,
            'valign': 'top'
        })
        line_header_light_ending_bold = workbook.add_format({
            'bold': True,
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'text_wrap': True,
            'valign': 'top'
        })

        lang = self.env.user.lang
        lang_id = self.env['res.lang'].search([('code', '=', lang)])[0]
        currency_id = self.env.user.company_id.currency_id
        line_header.num_format = currency_id.excel_format
        line_header_light.num_format = currency_id.excel_format
        line_header_light_initial.num_format = currency_id.excel_format
        line_header_light_ending.num_format = currency_id.excel_format
        line_header_light_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
        content_header_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')

        # Write data
        ################################################################
        row_pos_2 = 0
        row_pos = 0
        sheet.merge_range(0, 0, 0, 8, 'Partner Ledger' + ' - ' + data['company_id'][1], format_title)

        # Write filters
        sheet_2.write(row_pos_2, 0, _('Date from'), format_header)
        datestring = fields.Date.from_string(str(filter['date_from'])).strftime(lang_id.date_format)
        sheet_2.write(row_pos_2, 1, datestring or '', content_header_date)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Date to'), format_header)
        datestring = fields.Date.from_string(str(filter['date_to'])).strftime(lang_id.date_format)
        sheet_2.write(row_pos_2, 1, datestring or '', content_header_date)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Target moves'), format_header)
        for choice in filter['target_moves']['choices']:
            if choice['value'] == filter['target_moves']['selectedValue']['value']:
                sheet_2.write(row_pos_2, 1, choice['label'], content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Display accounts'), format_header)
        for choice in filter['display_accounts']['choices']:
            if choice['value'] == filter['display_accounts']['selectedValue']['value']:
                sheet_2.write(row_pos_2, 1, choice['label'], content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Initial Balance'), format_header)
        for choice in filter['include_initial_balance']['choices']:
            if choice['value'] == filter['include_initial_balance']['selectedValue']['value']:
                sheet_2.write(row_pos_2, 1, choice['label'], content_header)
        row_pos_2 += 1
        row_pos_2 += 2
        sheet_2.write(row_pos_2, 0, _('Journals'), format_header)
        j_list = ', '.join([lt['code'] or '' for lt in filter.get('defaultJournalValues')])
        sheet_2.write(row_pos_2, 1, j_list, content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Partners'), format_header)
        p_list = ', '.join([lt['label'] or '' for lt in filter.get('defaultPartnerValues')])
        sheet_2.write(row_pos_2, 1, p_list, content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Accounts'), format_header)
        a_list = ', '.join([lt['code'] or '' for lt in filter.get('defaultAccountValues')])
        sheet_2.write(row_pos_2, 1, a_list, content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Account Tags'), format_header)
        a_list = ', '.join([lt['label'] or '' for lt in filter.get('defaultAccountTagValues')])
        sheet_2.write(row_pos_2, 1, a_list, content_header)

        # Write Ledger details
        row_pos += 3
        sheet.write_string(row_pos, 0, _('Move#'), format_header)
        sheet.write_string(row_pos, 1, _('Journal'), format_header)
        sheet.write_string(row_pos, 2, _('Invoice Date'), format_header)
        sheet.write_string(row_pos, 3, _('Due Date'), format_header)
        sheet.write_string(row_pos, 4, _('Account'), format_header)
        sheet.write_string(row_pos, 5, _('Matching'), format_header)
        sheet.write_string(row_pos, 6, _('Debit'), format_header)
        sheet.write_string(row_pos, 7, _('Credit'), format_header)
        sheet.write_string(row_pos, 8, _('Amount Currency'), format_header)
        sheet.write_string(row_pos, 9, _('Balance'), format_header)

        if account_lines:
            for line in account_lines:
                row_pos += 1
                sheet.merge_range(row_pos, 0, row_pos, 5, line.get('partner_name'), line_header_left)
                sheet.write(row_pos, 6, float(line.get('debit')), line_header)
                sheet.write(row_pos, 7, float(line.get('credit')), line_header)
                sheet.write(row_pos, 8, '', line_header)
                sheet.write(row_pos, 9, float(line.get('balance')), line_header)

                sub_lines = record.prepare_detailed_lines(line.get('id_list'), line.get('partner_id'))

                for sub_line in sub_lines:
                    if sub_line.get('ttype') == 'initial':
                        row_pos += 1
                        sheet.write(row_pos, 5, 'Initial Balance', line_header_light_ending_bold)
                        sheet.write(row_pos, 6, float(sub_line.get('debit')), line_header_light_initial)
                        sheet.write(row_pos, 7, float(sub_line.get('credit')), line_header_light_initial)
                        sheet.write(row_pos, 8, '', line_header_light_initial)
                        sheet.write(row_pos, 9, float(sub_line.get('balance')), line_header_light_initial)
                    elif sub_line.get('ttype') == 'strict':
                        row_pos += 1
                        sheet.write(row_pos, 0, sub_line.get('move_name'), line_header_light)
                        sheet.write(row_pos, 1, sub_line.get('lcode'), line_header_light)
                        datestring = fields.Date.from_string(str(sub_line.get('ldate'))).strftime(lang_id.date_format)
                        sheet.write(row_pos, 2, datestring, line_header_light_date)
                        if sub_line.get('date_maturity'):
                            datestring = fields.Date.from_string(str(sub_line.get('date_maturity'))).strftime(lang_id.date_format)
                            sheet.write(row_pos, 3, datestring, line_header_light_date)
                        else:
                            sheet.write(row_pos, 3, datestring, line_header_light_date)
                        sheet.write(row_pos, 4, sub_line.get('account_code'), line_header_light)
                        sheet.write(row_pos, 5, sub_line.get('matching_number') or '', line_header_light)
                        sheet.write(row_pos, 6, float(sub_line.get('debit')), line_header_light)
                        sheet.write(row_pos, 7, float(sub_line.get('credit')), line_header_light)
                        sheet.write(row_pos, 8, float(sub_line.get('amount_currency')), line_header_light)
                        sheet.write(row_pos, 9, float(sub_line.get('balance')), line_header_light)
                    else:  # Ending Balance
                        row_pos += 1
                        sheet.write(row_pos, 5, 'Ending Balance', line_header_light_ending_bold)
                        sheet.write(row_pos, 6, float(sub_line.get('debit')), line_header_light_ending)
                        sheet.write(row_pos, 7, float(sub_line.get('credit')), line_header_light_ending)
                        sheet.write(row_pos, 8, '', line_header_light_ending)
                        sheet.write(row_pos, 9, float(sub_line.get('balance')), line_header_light_ending)

        # Close and return
        #################################################################
        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())

        report_id = self.env['common.xlsx.out'].sudo().create({'filedata': result, 'filename': 'PL.xls'})
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=common.xlsx.out&field=filedata&id=%s&filename=%s.xls' % (
                report_id.id, 'Partner Ledger.xls'),
            'target': 'new',
        }

        output.close()
