"""Facebook Content Export Driver.
"""
from pytsite import content_export as _content_export, logger as _logger, content as _content
from ._widget import Auth as _FacebookAuthWidget
from ._session import Session as _Session

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class Driver(_content_export.AbstractDriver):
    def __init__(self, **kwargs):
        """Init.
        """
        self._access_token = kwargs.get('access_token')

    def get_settings_widget(self, uid: str, **kwargs):
        scope = 'public_profile,email,user_friends,publish_actions,manage_pages,publish_pages'
        return _FacebookAuthWidget(uid=uid, scope=scope, **kwargs)

    def export(self, entity: _content.model.Content, exporter=_content_export.model.ContentExport):
        """Export data.
        """
        _logger.info("Export started. '{}'".format(entity.title), __name__)

        user_session = _Session(self._access_token)
        opts = exporter.driver_opts
        """:type: dict"""

        try:
            tags = ['#' + t for t in exporter.add_tags if ' ' not in t]
            tags += ['#' + t.title for t in entity.tags if ' ' not in t.title]
            message = entity.description + ' ' + ' '.join(tags) + ' ' + entity.url

            if opts['page_id']:
                page_session = _Session(self._get_page_access_token(opts['page_id'], user_session))
                page_session.feed_message(message, entity.url)
            else:
                user_session.feed_message(message, entity.url)
        except Exception as e:
            raise _content_export.error.ExportError(e)

        _logger.info("Export finished. '{}'".format(entity.title), __name__)

    def _get_page_access_token(self, page_id: str, user_session: _Session) -> str:
        """Get page access token.
        """
        for acc in user_session.accounts():
            if 'id' in acc and acc['id'] == page_id:
                return acc['access_token']

        raise Exception('Cannot get access token for page with id == {}'.format(page_id))
