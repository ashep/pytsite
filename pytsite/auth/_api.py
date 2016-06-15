"""Auth Manager.
"""
from typing import Dict as _Dict
from collections import OrderedDict
from datetime import datetime as _datetime
from pytsite import reg as _reg, odm as _odm, form as _form, lang as _lang, router as _router, cache as _cache, \
    events as _events, validation as _validation, geo_ip as _geo_ip, logger as _logger, util as _util, \
    threading as _threading
from . import _error, _model, driver as _driver

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

_registered_drivers = OrderedDict()  # type: _Dict[str, _driver.Abstract]

_permission_groups = []
_permissions = []
_anonymous_user = None
_system_user = None
_access_tokens = _cache.create_pool('pytsite.auth.access_tokens')
_current_user = {}  # user object per thread

user_login_rule = _validation.rule.Email()
user_nickname_rule = _validation.rule.Regex(msg_id='pytsite.auth@nickname_str_rules',
                                            pattern='^[A-Za-z0-9][A-Za-z0-9\.\-_]{0,31}$')


def hash_password(secret: str) -> str:
    """Hash a password.
    """
    from werkzeug.security import generate_password_hash
    return generate_password_hash(str(secret))


def verify_password(clear_text: str, hashed: str) -> bool:
    """Verify hashed password.
    """
    from werkzeug.security import check_password_hash
    return check_password_hash(str(hashed), str(clear_text))


def register_driver(driver: _driver.Abstract):
    """Change current driver.
    """
    if not isinstance(driver, _driver.Abstract):
        raise TypeError('Instance of AbstractDriver expected.')

    name = driver.get_name()
    if name in _registered_drivers:
        raise ValueError("Driver '{}' is already registered.".format(name))

    _registered_drivers[name] = driver


def get_driver(name: str = None) -> _driver.Abstract:
    """Get driver instance.
    """
    if name is None:
        if _registered_drivers:
            name = _reg.get('auth.default_driver', list(_registered_drivers)[-1])
        else:
            raise _error.DriverNotRegistered('No authentication driver registered.')

    if name not in _registered_drivers:
        raise _error.DriverNotRegistered("Authentication driver '{}' is not registered.".format(name))

    return _registered_drivers[name]


def get_sign_in_form(driver_name: str = None, uid: str = None, **kwargs) -> _form.Form:
    """Get a login form.
    """
    driver = get_driver(driver_name)

    kwargs['css'] = kwargs.get('css', '') + ' pytsite-auth-sign-in driver-' + driver.name

    if not uid:
        uid = 'pytsite-auth-sign-in'

    if not kwargs.get('title'):
        kwargs['title'] = _lang.t('pytsite.auth@authentication')

    form = driver.get_sign_in_form(uid, **kwargs)
    form.action = _router.ep_url('pytsite.auth@sign_in_submit', {'driver': driver.name})

    return form


def sanitize_nickname(s: str) -> str:
    """Generate unique nickname.
    """
    cnt = 0
    s = _util.transform_str_2(s[:32])
    nickname = s
    while True:
        if not get_user(nickname=nickname):
            return nickname

        cnt += 1
        nickname = s + '-' + str(cnt)


def create_user(login: str, password: str = None) -> _model.User:
    """Create new user.
    """
    if login not in (_model.ANONYMOUS_USER_LOGIN, _model.SYSTEM_USER_LOGIN):
        if get_user(login):
            raise _error.UserExists("User with login '{}' already exists.".format(login))

        user_login_rule.value = login
        user_login_rule.validate()

    user = _odm.dispense('user')  # type: _model.User
    user.f_set('login', login).f_set('email', login).f_set('password', password)

    # Do some actions with non-anonymous users
    if login not in (_model.ANONYMOUS_USER_LOGIN, _model.SYSTEM_USER_LOGIN):
        # Automatic roles for new users
        for role_name in _reg.get('auth.signup.roles', ['user']):
            role = get_role(role_name)
            if role:
                user.f_add('roles', role)

        # GeoIP data
        if _router.request():
            user.f_set('geo_ip', _geo_ip.resolve(_router.request().remote_addr))

    return user


def get_anonymous_user() -> _model.User:
    global _anonymous_user
    if not _anonymous_user:
        _anonymous_user = create_user(_model.ANONYMOUS_USER_LOGIN)

    return _anonymous_user


def get_system_user() -> _model.User:
    global _system_user
    if not _system_user:
        _system_user = create_user(_model.SYSTEM_USER_LOGIN)

    return _system_user


def get_user(login: str = None, uid: str = None, nickname: str = None, access_token: str = None,
             check_status: bool = True) -> _model.User:
    """Get user by login, nickname or by uid.
    """
    with _threading.get_r_lock():
        # Don't cache finder results due to frequent user updates in database
        f = _odm.find('user').cache(0)
        if login is not None:
            f.where('login', '=', login)

        elif uid is not None:
            f.where('_id', '=', uid)

        elif nickname is not None:
            f.where('nickname', '=', nickname)

        elif access_token is not None:
            # Check if the access token is valid
            if _access_tokens.has(access_token):
                f.where('access_token', '=', access_token)

        else:
            return get_anonymous_user()

        user = f.first()  # type: _model.User
        if check_status and user.status != 'active':
            sign_out(user)
            raise _error.AuthenticationError("Account of user '{}' is not active.".format(user.login))

        return user


def create_role(name: str, description: str = ''):
    """Create new role.
    """
    if get_role(name=name):
        raise RuntimeError("Role with name '{}' already exists.".format(name))

    role = _odm.dispense('role')

    return role.f_set('name', name).f_set('description', description)


def get_role(name: str = None, uid=None) -> _model.Role:
    """Get role by name or by UID.
    """
    f = _odm.find('role')

    if name:
        return f.where('name', '=', name).first()
    elif uid:
        return f.where('_id', '=', uid).first()
    else:
        RuntimeError('Either role name or ID must be specified while calling this function.')


def sign_in(driver: str, data: dict) -> _model.User:
    """Authenticate user.
    """
    try:
        # Get user from driver
        user = get_driver(driver).sign_in(data)
        set_current_user(user)

    except _error.AuthenticationError as e:
        _logger.warn(str(e))
        raise e

    # Generate new token or prolong existing one
    if not _access_tokens.has(user.access_token):
        user.f_set('access_token', create_access_token(user.login, data.get('access_token_ttl', 3600))).save()
    else:
        prolong_access_token(user.access_token)

    # Set session marker
    if _router.session() is not None:
        _router.session()['pytsite.auth.login'] = user.login

    # Update login counter
    user.f_inc('sign_in_count').f_set('last_sign_in', _datetime.now()).save()

    # Update IP address and geo data
    if _router.request():
        user.f_set('last_ip', _router.request().remote_addr)
        if not user.country and user.geo_ip.country:
            user.f_set('country', user.geo_ip.country)
        if not user.city and user.geo_ip.city:
            user.f_set('city', user.geo_ip.city)

        user.save()

    # Login event
    _events.fire('pytsite.auth.sign_in', user=user)

    return user


def get_access_token_info(token: str) -> dict:
    """Get access token's metadata.
    """
    if not _access_tokens.has(token):
        raise _error.InvalidAccessToken('Invalid access token.')

    r = _access_tokens.get(token)
    r['expires'] = _access_tokens.ttl(token)

    return r


def create_access_token(login: str, ttl: int) -> str:
    """Generate new access token.
    """
    try:
        access_token_ttl = int(ttl)
        if access_token_ttl <= 0:
            raise ValueError()
    except ValueError:
        raise ValueError("'access_token_ttl' must be a positive integer.")

    with _threading.get_r_lock():
        while True:
            token = _util.random_str(32)
            if not _access_tokens.has(token):
                _access_tokens.put(token, {'login': login, 'ttl': ttl}, ttl)
                return token


def prolong_access_token(token: str):
    """Prolong user's access token.
    """
    with _threading.get_r_lock():
        token_info = get_access_token_info(token)
        _access_tokens.put(token, token_info, token_info['ttl'])


def sign_out(user: _model.User, issue_event: bool = True):
    """Sign out current user.
    """
    # Anonymous user cannot be signed out
    if user.is_anonymous:
        return

    # Ask drivers to perform necessary operations
    for driver in _registered_drivers.values():
        driver.sign_out(user)

    # Remove access token
    _access_tokens.rm(user.access_token)

    # Remove session's data
    if _router.session().get('pytsite.auth.login'):
        del _router.session()['pytsite.auth.login']

    # Notify listeners
    if issue_event:
        _events.fire('pytsite.auth.sign_out', user=user)

    # Set anonymous user as current
    set_current_user(get_anonymous_user())


def get_current_user() -> _model.User:
    """Get currently session-authorized user.
    """
    # Current or anonymous
    return _current_user.get(_threading.get_id(), get_anonymous_user())


def set_current_user(user: _model.User = None):
    _current_user[_threading.get_id()] = user


def get_user_statuses() -> tuple:
    """Get available user statuses.
    """
    return (
        ('active', _lang.t('pytsite.auth@status_active')),
        ('waiting', _lang.t('pytsite.auth@status_waiting')),
        ('disabled', _lang.t('pytsite.auth@status_disabled')),
    )


def get_sign_in_url(driver: str = None) -> str:
    """Get login URL.
    """
    if not driver:
        driver = list(_registered_drivers)[-1]

    return _router.ep_url('pytsite.auth@sign_in', {'driver': driver})


def get_sign_out_url(driver: str = None) -> str:
    """Get logout URL.
    """
    if not driver:
        driver = list(_registered_drivers)[-1]

    return _router.ep_url('pytsite.auth@sign_out', {'driver': driver, '__redirect': _router.current_url()})


def find_users(active_only: bool = True) -> _odm.Finder:
    """Get users finder.
    """
    f = _odm.find('user').sort([('sign_in_count', _odm.I_DESC)])
    if active_only:
        f.where('status', '=', 'active')

    return f
