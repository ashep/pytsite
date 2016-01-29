"""Content Widgets.
"""
from pytsite import taxonomy as _taxonomy, auth as _auth, widget as _widget, html as _html, lang as _lang, \
    router as _router, tpl as _tpl, odm as _odm
from . import _model, _api

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class ModelSelect(_widget.select.Select):
    """Content Model Select Widget.
    """
    def __init__(self, uid: str, **kwargs):
        self._check_perms = kwargs.get('check_perms', True)

        items = []
        u = _auth.get_current_user()
        for k, v in _api.get_models().items():
            if self._check_perms:
                if u.has_permission('pytsite.odm_ui.browse.' + k) or u.has_permission('pytsite.odm_ui.browse_own.' + k):
                    items.append((k, _lang.t(v[1])))
            else:
                items.append((k, _lang.t(v[1])))

        super().__init__(uid, items=sorted(items, key=lambda x: x[1]), **kwargs)


class StatusSelect(_widget.select.Select):
    """Content Status Select Widget.
    """
    def __init__(self, uid: str, **kwargs):
        super().__init__(uid, items=_api.get_statuses(), **kwargs)


class EntitySelect(_widget.select.Select2):
    def __init__(self, uid: str, **kwargs):
        kwargs['ajax_url'] = _router.ep_url('pytsite.content.ep.ajax_search', {
            'model': kwargs.get('model'),
            'language': kwargs.get('language', _lang.get_current()),
        })

        super().__init__(uid, **kwargs)

    def set_val(self, value, **kwargs):
        if isinstance(value, str) and not value:
            value = None
        elif isinstance(value, _model.Content):
            value = value.model + ':' + str(value.id)

        return super().set_val(value, **kwargs)

    def get_html_em(self):
        # In AJAX-mode Select2 doesn't contain any items,
        # but if we have selected item, it is necessary to append it
        if self._ajax_url and self._value:
            self._items.append((self._value, _odm.get_by_ref(self._value).f_get('title')))

        return super().get_html_em()


class SectionSelect(_taxonomy.widget.TermSelect):
    """Content Section Select Widget.
    """
    def __init__(self, uid: str, **kwargs):
        """Init.
        """
        super().__init__(uid, model='section', caption_field='title', **kwargs)


class TagCloud(_taxonomy.widget.Cloud):
    """Tags Cloud Widget.
    """
    def __init__(self, uid: str, **kwargs):
        """Init.
        """
        super().__init__(uid, model='tag', **kwargs)


class EntityTagCloud(_taxonomy.widget.Cloud):
    """Tags Cloud of the Entity Widget.
    """
    def __init__(self, uid: str, **kwargs):
        """Init.
        """
        super().__init__(uid, model='tag', **kwargs)

        self._entity = kwargs.get('entity')
        if not self._entity:
            raise ValueError('Entity is not specified.')

    @property
    def terms(self) -> tuple:
        return self._entity.tags


class Search(_widget.Base):
    def __init__(self, uid: str, **kwargs):
        """Init.
        """
        super().__init__(uid, **kwargs)

        self._model = kwargs.get('model')
        if not self._model:
            raise ValueError('Model is not specified.')

        self._value = _router.request().inp.get('search', '')
        self._title_tag = kwargs.get('title_tag', 'h3')

        self._form = _html.Form(cls='wrapper form-inline', method='GET')
        self._form.append(_html.Input(type='text', cls='form-control', name='search',  required=True, value=self.value,
                          placeholder=_lang.t('pytsite.content@search_input_placeholder')))
        self._form.set_attr('action', _router.ep_url('pytsite.content.ep.search', {'model': self._model}))

        btn = _html.Button(type='submit', cls='btn btn-default')
        self._form.append(btn.append(_html.I(cls='fa fa-search')))

    @property
    def title_tag(self) -> str:
        return self._title_tag

    @property
    def model(self) -> str:
        return self._model

    @property
    def form(self) -> _html.Element:
        return self._form

    def get_html_em(self) -> _html.Element:
        """Render the widget.
        """
        return self._group_wrap(_tpl.render('pytsite.content@widget/search', {'widget': self}))
