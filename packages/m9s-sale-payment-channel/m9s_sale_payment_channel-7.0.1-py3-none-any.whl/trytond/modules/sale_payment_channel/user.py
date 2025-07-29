# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval


class User(metaclass=PoolMeta):
    __name__ = "res.user"
    sale_device = fields.Many2One('sale.device', 'Sale Device',
            domain=[('channel', '=', Eval('current_channel'))],
    )

    @classmethod
    def __setup__(cls):
        super(User, cls).__setup__()
        if 'sale_device' not in cls._context_fields:
            cls._context_fields.insert(0, 'sale_device')

    @classmethod
    def _get_preferences(cls, user, context_only=False):
        res = super(User, cls)._get_preferences(user,
            context_only=context_only)
        if not context_only:
            res['sale_device'] = user.sale_device and user.sale_device.id or None
        return res
