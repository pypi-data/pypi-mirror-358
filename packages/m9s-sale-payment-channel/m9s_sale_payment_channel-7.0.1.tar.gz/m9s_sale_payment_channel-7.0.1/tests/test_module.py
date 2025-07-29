# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase


class SalePaymentChannelTestCase(ModuleTestCase):
    "Test Sale Payment Channel module"
    module = 'sale_payment_channel'


del ModuleTestCase
