"""PytSite Cleanup Module.
"""
from pytsite import events as _events
from ._eh import cron_daily

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

_events.listen('pytsite.cron.daily', cron_daily)
