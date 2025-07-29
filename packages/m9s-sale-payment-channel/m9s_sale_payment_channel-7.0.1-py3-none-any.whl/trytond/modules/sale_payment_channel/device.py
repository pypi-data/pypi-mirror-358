# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, fields
from trytond.pyson import Eval


class SaleDevice(ModelSQL, ModelView):
    'Sale Device'
    __name__ = 'sale.device'
    name = fields.Char('Device Name', required=True)
    channel = fields.Many2One('sale.channel', 'Channel', required=True)
    company = fields.Function(fields.Many2One('company.company', 'Company',),
        'get_company', searcher='search_company')
    journals = fields.Many2Many('sale.device.account.statement.journal',
        'device', 'journal', 'POS Journals',
        domain=[
            ('company', '=', Eval('company')),
            ])
    journal = fields.Many2One('account.statement.journal',
        "Default POS Journal", ondelete='RESTRICT',
        domain=[
            ('id', 'in', Eval('journals', [])),
            ])

    @fields.depends('channel')
    def on_change_channel(self):
        self.company = self.channel.company.id if self.channel else None

    def get_company(self, name):
        return self.channel.company.id

    @classmethod
    def search_company(cls, name, clause):
        return [('channel.%s' % name,) + tuple(clause[1:])]


class SaleDeviceStatementJournal(ModelSQL):
    'Sale Device - POS Journal'
    __name__ = 'sale.device.account.statement.journal'
    _table = 'sale_device_account_statement_journal'
    device = fields.Many2One('sale.device', 'Sale Device',
            ondelete='CASCADE', required=True)
    journal = fields.Many2One('account.statement.journal', 'POS Journal',
            ondelete='RESTRICT', required=True)
