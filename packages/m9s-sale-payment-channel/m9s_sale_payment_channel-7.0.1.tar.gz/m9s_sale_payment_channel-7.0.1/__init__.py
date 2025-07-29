# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool

from . import device, sale, statement, user

__all__ = ['register']


def register():
    Pool.register(
        device.SaleDevice,
        device.SaleDeviceStatementJournal,
        sale.Sale,
        sale.SalePaymentForm,
        statement.Journal,
        statement.Statement,
        statement.Line,
        statement.OpenStatementStart,
        statement.OpenStatementDone,
        statement.CloseStatementStart,
        statement.CloseStatementDone,
        user.User,
        module='sale_payment_channel', type_='model')
    Pool.register(
        sale.WizardSalePayment,
        sale.WizardSaleReconcile,
        statement.OpenStatement,
        statement.CloseStatement,
        module='sale_payment_channel', type_='wizard')
