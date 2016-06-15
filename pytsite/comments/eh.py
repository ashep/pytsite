"""Event Handlers.
"""
from pytsite import db as _db

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def pytsite_update(version: str):
    """'pytsite.update' event handler.
    """
    if version == '0.73.0':
        # No needed anymore
        _db.get_collection('comments_counts').drop()
