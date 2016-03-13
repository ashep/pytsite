"""Settings Plugin Init.
"""
# Public API
from ._api import define, get_setting

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


# Init wrapper
def __init():
    import sys
    from pytsite import odm, tpl, lang, router, admin, ajax
    from ._model import Setting

    # Language package
    lang.register_package(__name__)

    # Template package and globals
    tpl.register_package(__name__)
    tpl.register_global('settings', sys.modules[__name__])

    # ODM model
    odm.register_model('setting', Setting)

    # Routing
    router.add_rule(admin.base_path() + '/settings/<string:uid>', 'pytsite.settings.ep.form')
    router.add_rule(admin.base_path() + '/settings/<string:uid>/submit', 'pytsite.settings.ep.form_submit',
                    methods='POST')

    # Sidebar section
    admin.sidebar.add_section('settings', __name__ + '@settings', 2000, ('*',))

    # AJAX endpoints
    ajax.register_ep('pytsite.settings.ep.form_validate')


# Package initialization
__init()
