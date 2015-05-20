__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from werkzeug.utils import escape
from pytsite.core import metatag, lang, router, tpl
from pytsite.core.http.errors import Forbidden
from . import auth_manager


def get_login(args: dict, inp: dict) -> str:
    """Get login form.
    """
    metatag.set_tag('title', lang.t('pytsite.auth@authorization'))
    return tpl.render('pytsite.auth@views/login', {'form': auth_manager.get_login_form()})


def post_login(args: dict, inp: dict) -> router.RedirectResponse:
    """Process login form submit.
    """

    return auth_manager.post_login_form(args, inp)


def get_logout(args: dict, inp: dict) -> router.RedirectResponse:
    """Logout endpoint.
    """

    auth_manager.logout_current_user()
    redirect_url = router.base_url()
    if 'redirect' in inp:
        redirect_url = router.url(inp['redirect'])
    return router.RedirectResponse(redirect_url)


def filter_authorize(args: dict, inp: dict) -> router.RedirectResponse:
    """Authorization filter.
    """

    user = auth_manager.get_current_user()

    # User is currently authorized
    if user:
        # Checking requested permissions
        req_perms_str = args.get('permissions', '')
        if req_perms_str:
            for perm in req_perms_str.split(','):
                if not user.has_permission(perm.strip()):
                    raise Forbidden()
        return

    # Redirecting to the authorization endpoint
    inp['redirect'] = escape(router.current_url(True))
    return router.RedirectResponse(router.endpoint_url('pytsite.auth.endpoints.get_login', inp))
