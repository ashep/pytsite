"""Twitter Auth Widget.
"""
from pytsite import widget as _widget, html as _html, lang as _lang, router as _router
from ._session import Session as TwitterSession

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class Auth(_widget.Base):
    """Twitter oAuth Widget.
    """
    def __init__(self, uid: str, **kwargs):
        """Init.
        """
        super().__init__(uid, **kwargs)

        self._oauth_token = kwargs.get('oauth_token', '')
        self._oauth_token_secret = kwargs.get('oauth_token_secret', '')
        self._user_id = kwargs.get('user_id', '')
        self._screen_name = kwargs.get('screen_name', '')
        self._callback_uri = kwargs.get('callback_uri', '')

        self._css += ' widget-twitter-oauth'

        self._session = TwitterSession(self.oauth_token, self.oauth_token_secret)
        """:type: pytsite.twitter._oauth.Driver"""

        # If 'verifier' is here, we need to exchange it to an access token
        inp_oauth_verifier = _router.request().inp.get('oauth_verifier')
        if inp_oauth_verifier:
            token = self._session.get_access_token(inp_oauth_verifier)
            self._oauth_token = token['oauth_token']
            self._oauth_token_secret = token['oauth_token_secret']
            self._user_id = token['user_id']
            self._screen_name = token['screen_name']

    @property
    def oauth_token(self) -> str:
        return self._oauth_token

    @property
    def oauth_token_secret(self) -> str:
        return self._oauth_token_secret

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def screen_name(self) -> str:
        return self._screen_name

    def get_html_em(self) -> _html.Element:
        """Render widget.
        """
        wrapper = _widget.static.Container(self.uid)

        wrapper.append(_widget.input.Hidden(
            uid=self.uid + '_oauth_token',
            value=self.oauth_token,
        ))

        wrapper.append(_widget.input.Hidden(
            uid=self.uid + '_oauth_token_secret',
            value=self.oauth_token_secret,
        ))

        wrapper.append(_widget.input.Hidden(
            uid=self.uid + '_user_id',
            value=self.user_id,
        ))

        wrapper.append(_widget.input.Hidden(
            uid=self.uid + '_screen_name',
            value=self.screen_name,
        ))

        if self.screen_name:
            title = self.screen_name
            href = 'https://twitter.com/' + self._screen_name
        else:
            title = _lang.t('pytsite.twitter@authorization')
            href = self._session.get_authorization_url(self._callback_uri)

        wrapper.append(_widget.static.HTML(
            uid=self.uid + '_auth_link',
            em=_html.A(title, href=href).append(_html.I(cls='fa fa-twitter'))
        ))

        return self._group_wrap(wrapper.get_html_em())
