"""Description.
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

__import__('pytsite.odm_ui')

from pytsite.core import lang, router
from pytsite.admin import sidebar

lang.register_package(__name__)

sidebar.add_section('auth', lang.t('pytsite.auth_ui@security'), 1000)

url = router.endpoint_url('pytsite.odm_ui.endpoints.browse', {'model': 'user'})
sidebar.add_section_menu('auth', 'users', lang.t('pytsite.auth_ui@users'), url, 'fa fa-user', weight=10)

url = router.endpoint_url('pytsite.odm_ui.endpoints.browse', {'model': 'role'})
sidebar.add_section_menu('auth', 'roles', lang.t('pytsite.auth_ui@roles'), url, 'fa fa-users', weight=20)
