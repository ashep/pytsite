"""File Widgets.
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite.core import widget as _widget, assetman as _assetman, router as _router, tpl as _tpl, client as _client, \
    html as _html
from . import _manager


class FilesUpload(_widget.base.Widget):
    """Files Upload Widget.
    """

    def __init__(self, model: str, **kwargs: dict):
        """Init.
        """
        super().__init__(**kwargs)

        self._group_cls = ' '.join((self._group_cls, 'widget-files-upload'))

        # Processing setter filtering
        self.set_value(self._value)

        self._model = model
        self._max_file_size = int(kwargs.get('max_file_size', 2))
        self._max_files = int(kwargs.get('max_files', 0))
        self._accept_files = kwargs.get('accept_files', '*/*')
        self._add_btn_label = kwargs.get('add_btn_label', '')
        self._image_max_width = kwargs.get('image_max_width', 0)
        self._image_max_height = kwargs.get('image_max_height', 0)

        if self._max_files:
            self._group_data['max_files'] = self._max_files

        _client.include('imagesloaded')
        _assetman.add('pytsite.file@css/upload-widget.css')
        _assetman.add('pytsite.file@js/load-image.all.min.js')
        _assetman.add('pytsite.file@js/canvas-to-blob.min.js')
        _assetman.add('pytsite.file@js/upload-widget.js')

    @property
    def accept_files(self) -> str:
        return self._accept_files

    @property
    def add_btn_label(self) -> str:
        return self._add_btn_label

    @add_btn_label.setter
    def add_btn_label(self, value):
        self._add_btn_label = value

    @property
    def image_max_width(self) -> int:
        return self._image_max_width

    @image_max_width.setter
    def image_max_width(self, value):
        self._image_max_width = value

    @property
    def image_max_height(self) -> int:
        return self._image_max_width

    @image_max_height.setter
    def image_max_height(self, value):
        self._image_max_height = value

    def render(self) -> str:
        self._group_data = {
            'url': _router.endpoint_url('pytsite.file.eps.post_upload', {'model': self._model}),
            'model': self._model,
            'max_files': self._max_files if self._max_files else 1,
            'max_file_size': self._max_file_size,
            'accept_files': self._accept_files,
            'image_max_width': self._image_max_width,
            'image_max_height': self._image_max_height,
        }
        widget_content = _html.Div(_tpl.render('pytsite.file@file_upload_widget', {'widget': self}))
        return self._group_wrap(widget_content)

    def set_value(self, value: list, **kwargs):
        """Set value of the widget.
        """

        if value is None:
            return

        if not isinstance(value, list):
            value = [value]

        clean_val = []
        for val in value:
            if not val:
                continue
            entity = _manager.get_by_ref(val)
            if entity:
                clean_val.append(entity)

        # Delete files which are has been removed from the widget.
        to_delete = _router.request.values_dict.get(self._uid + '_to_delete')
        if to_delete and not kwargs.get('validation_mode'):  # IMPORTANT: not in form validation mode
            if isinstance(to_delete, str):
                to_delete = [to_delete]
            for ref in to_delete:
                file = _manager.get_by_ref(ref)
                if file:
                    file.delete()

        self._value = clean_val
