"""Object Document Mapper Package Init
"""
# Public API
from . import _field as field, _validation as validation, _error as error, _geo as geo, _model as model
from ._model import I_ASC, I_DESC, I_TEXT, I_GEO2D, I_GEOSPHERE
from ._finder import Finder, Result as FinderResult
from ._api import register_model, unregister_model, is_model_registered, get_model_class, get_registered_models, \
    resolve_ref, resolve_refs, get_by_ref, dispense, find, aggregate

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def _init():
    from pytsite import console, lang, events, stats, cron
    from . import _console_command, _eh, _cache

    # Resources
    lang.register_package(__name__)

    # Console commands
    console.register_command(_console_command.ODM())

    # Event listeners
    events.listen('pytsite.update.after', _eh.update_after)
    events.listen('pytsite.db.restore', _eh.db_restore)

    # Cron tasks
    cron.every_min(_cache.cleanup)

    # Stats update
    stats.on_update(lambda: 'ODM entities cache size: {}'.format(_cache.get_size()))


_init()
