"""CKEditor Widget.
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite.core import widget as _widget, assetman as _assetman, html as _html


class CKEditor(_widget.Base):
    """CKEditor Widget.
    """
    def __init__(self, **kwargs: dict):
        """Init.
        """
        super().__init__(**kwargs)
        self._group_cls = ' '.join((self._group_cls, 'widget-ckeditor'))
        _assetman.add('pytsite.ckeditor@ckeditor/skins/moono/editor.css')
        _assetman.add('pytsite.ckeditor@ckeditor/ckeditor.js')
        _assetman.add('pytsite.ckeditor@ckeditor/adapters/jquery.js')
        _assetman.add('pytsite.ckeditor@js/ckeditor.js')

    def render(self) -> str:
        """Render the widget.
        """
        return self._group_wrap(_html.TextArea(self.get_value(), name=self._uid))
