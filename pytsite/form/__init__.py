"""Pytsite Form Package.
"""
# Public API
from . import _error as error, _cache as cache
from ._form import Form

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def _init():
    from pytsite import assetman, tpl, lang, router, http_api, cron, stats
    from . import _http_api

    lang.register_package(__name__)
    assetman.register_package(__name__)
    tpl.register_package(__name__)

    router.handle('/form/submit/<uid>', 'pytsite.form@submit', 'pytsite.form@submit', methods='POST')

    http_api.handle('POST', 'form/widgets/<uid>', _http_api.get_widgets, 'pytsite.form@post_get_widgets')
    http_api.handle('POST', 'form/validate/<uid>', _http_api.post_validate, 'pytsite.form@post_validate')

    # Cron tasks
    cron.every_min(cache.cleanup)

    # Stats update
    stats.on_update(lambda: 'Forms cache size: {}'.format(cache.get_size()))


_init()
