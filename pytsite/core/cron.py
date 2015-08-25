"""PytSite Cron.
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

import pickle as _pickle
from os import path as _path
from datetime import datetime as _datetime, timedelta as _timedelta
from pytsite.core import events as _events, logger as _logger, reg as _reg, threading as _threading


_period = _reg.get('cron.period', 60)
_last_start = _datetime.now() - _timedelta(seconds=_period)
_stats = None
_working = False


def _thread_start():
    if _working:
        _logger.error('{}. Cron is still working.'.format(__name__))
        return

    # Start new thread
    delta = _datetime.now() - _last_start
    if delta.seconds >= _period:
        _threading.create_thread(_start).start()


def _start():
    """Start the cron.
    """
    global _last_start, _working, _period

    _working = True
    _events.fire('pytsite.core.cron.tick')

    stats = _get_stats()
    now = _datetime.now()
    for evt in '1min', '5min', '15min', '30min' 'hourly', 'daily', 'weekly', 'monthly':
        if evt in stats:
            delta = now - stats[evt]
            if evt == '1min' and delta.total_seconds() >= 60 \
                    or evt == '5min' and delta.total_seconds() >= 300 \
                    or evt == '15min' and delta.total_seconds() >= 900 \
                    or evt == '30min' and delta.total_seconds() >= 1800 \
                    or evt == 'hourly' and delta.total_seconds() >= 3600 \
                    or evt == 'daily' and delta.total_seconds() >= 86400 \
                    or evt == 'weekly' and delta.total_seconds() >= 604800 \
                    or evt == 'monthly' and delta.total_seconds() >= 2592000:

                _logger.info(__name__ + '. Event: pytsite.core.cron.' + evt)

                try:
                    _events.fire('pytsite.core.cron.' + evt)
                except Exception as e:
                    _logger.error('{}. {}'.format(__name__, str(e)))
                finally:
                    _update_stats(evt)
        else:
            _update_stats(evt)

    _last_start = _datetime.now()
    _working = False


def _get_stats_file_path():
    """Get descriptor file path.
    """
    return _path.join(_reg.get('paths.storage'), 'cron.data')


def _get_stats() -> dict:
    """Get descriptor info.
    """
    global _stats

    if not _stats:
        file_path = _get_stats_file_path()
        if not _path.exists(file_path):
            data = {
                '1min': _datetime.fromtimestamp(0),
                '5min': _datetime.fromtimestamp(0),
                '15min': _datetime.fromtimestamp(0),
                'hourly': _datetime.fromtimestamp(0),
                'daily': _datetime.fromtimestamp(0),
                'weekly': _datetime.fromtimestamp(0),
                'monthly': _datetime.fromtimestamp(0),
            }
            with open(file_path, 'wb') as f:
                _pickle.dump(data, f)
        else:
            with open(file_path, 'rb') as f:
                data = _pickle.load(f)

        _stats = data

    return _stats


def _update_stats(part: str) -> dict:
    """Update descriptor.
    """
    data = _get_stats()
    data[part] = _datetime.now()
    with open(_get_stats_file_path(), 'wb') as f:
        _pickle.dump(data, f)

    global _stats
    _stats = data

    return _stats

if _reg.get('cron.enabled', True):
    _events.listen('pytsite.core.router.dispatch', _thread_start)
