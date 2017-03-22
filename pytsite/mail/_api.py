"""PytSite Mail API.
"""
from pytsite import settings as _settings, router as _router

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def mail_from() -> tuple:
    """Get default mail sender's address and name.
    """
    return _settings.get('mail.from', 'info@' + _router.server_name())
