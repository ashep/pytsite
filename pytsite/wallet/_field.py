"""PytSite Money ODM Field
"""
from copy import deepcopy as _deepcopy
from frozendict import frozendict as _frozendict
from decimal import Decimal as _Decimal
from pytsite import odm as _odm, currency as _currency, auth as _auth

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class Money(_odm.field.Dict):
    """PytSite Money ODM Field
    """
    def __init__(self, name: str, **kwargs):
        """Init.
        """
        # Default value
        if not kwargs.get('default'):
            u = _auth.current_user()
            currency = u.f_get('currency') if u and u.has_field('currency') else _currency.get_main()
            kwargs['default'] = {'currency': currency, 'amount': _Decimal('0.0')}

        super().__init__(name, **kwargs)

    @property
    def is_empty(self):
        return self._value['amount'] == _Decimal('0.0')

    def _on_set(self, value: dict, **kwargs):
        """Set value fo the field.
        """
        # Convert to mutable dict if necessary
        if isinstance(value, _frozendict):
            value = dict(value)

        # Check value type
        if not isinstance(value, dict):
            raise TypeError("Value of the field '{}' should be a dict.".format(self._name))

        # Check for required dict keys
        if 'currency' not in value or not value['currency']:
            raise ValueError("Value of the field '{}' must contain 'currency' key.".format(self._name))
        if 'amount' not in value:
            raise ValueError("Value of the field '{}' must contain 'amount' key.".format(self._name))

        # Check for currency validness
        if value['currency'] not in _currency.get_all():
            raise _currency.error.CurrencyNotDefined("Currency '{}' is not defined.".format(value['currency']))

        # Float amount should be converted to string before converting to Decimal
        if isinstance(value['amount'], float):
            value['amount'] = str(value['amount'])

        # Convert amount to Decimal
        if not isinstance(value['amount'], _Decimal):
            value['amount'] = _Decimal(value['amount'])

        return value

    def _on_get(self, internal_value, **kwargs) -> dict:
        """Get value of the field.
        """
        internal_value.update({
            'currency_symbol': _currency.get_symbol(internal_value['currency']),
            'currency_title': _currency.get_title(internal_value['currency']),
        })

        return internal_value

    def _on_get_jsonable(self, internal_value, **kwargs):
        internal_value['amount'] = float(internal_value['amount'])

        return internal_value

    def _on_get_storable(self, internal_value, **kwargs):
        """Get storable value of the feld.
        """
        return {
            'currency': internal_value['currency'],
            'amount': float(internal_value['amount'])
        }
