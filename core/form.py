"""Forms.
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from .util import xml_attrs_str, dict_sort
from .widget.abstract import AbstractWidget
from .widget.input import HiddenInputWidget
from .validation import Validator, Rule
from .html import Div
from . import router


class AbstractForm:
    """Abstract form.
    """

    def __init__(self, uid: str, **kwargs: dict):
        """Init.
        """

        self._uid = uid
        self._name = kwargs.get('name', '')
        self._method = kwargs.get('method', 'post')
        self._action = kwargs.get('action', '#')
        self._legend = kwargs.get('legend', '')
        self._cls = kwargs.get('cls', '')

        self._areas = {'form': [], 'header': [], 'body': [], 'footer': []}
        self._widgets = {}
        self._validator = Validator()

        if not self._name:
            self._name = uid

        self.add_widget(HiddenInputWidget(name='__form_location', value=router.current_url()), area='form')

        self._setup()

    def _setup(self):
        """_setup() hook.
        """
        pass

    @property
    def uid(self) -> str:
        """Get form ID.
        """
        return self._uid

    @property
    def name(self) -> str:
        """Get form name.
        """
        return self._name

    @property
    def method(self) -> str:
        """Get method.
        """
        return self._method

    @property
    def action(self) -> str:
        """Get form action URL.
        """
        return self._action

    @action.setter
    def action(self, val):
        """Set form action URL.
        """
        self._action = val

    @property
    def legend(self) -> str:
        """Get legend.
        """
        return self._legend

    @legend.setter
    def legend(self, value: str):
        """Set legend.
        """
        self._legend = value

    @property
    def cls(self) -> str:
        """CSS classes getter.
        """
        return self._cls

    @property
    def messages(self):
        """Get validation messages.
        """
        return self._validator.messages

    def fill(self, values: dict):
        """Fill form's widgets with values.
        """

        for field_name, field_value in values.items():
            if self.has_widget(field_name):
                self.get_widget(field_name).value = field_value

            if self._validator.has_field(field_name):
                self._validator.set_value(field_name, field_value)

        return self

    def add_rule(self, widget_id: str, rule: Rule):
        """Add a rule to the validator.
        """

        if widget_id not in self._widgets:
            raise KeyError("Widget '{0}' is not exists.".format(widget_id))

        self._validator.add_rule(widget_id, rule)

        return self

    def validate(self) -> bool:
        """Validate the form.
        """

        return self._validator.validate()

    def store_state(self, except_fields: tuple=None):
        """Store state of the form into the session.
        """
        pass

    def restore_state(self, except_fields: tuple=None):
        """Store state of the form from the session.
        """
        pass

    def render(self) -> str:
        """Render the form.
        """

        body = ''
        for area in ['form', 'header', 'body', 'footer']:
            rendered_area = self._render_widgets(area)
            body += rendered_area

        return self._render_open_tag() + body + self._render_close_tag()

    def add_widget(self, widget: AbstractWidget, weight: int=0, area: str='body'):
        """Add a widget.
        """

        uid = widget.uid
        if uid in self._widgets:
            raise KeyError("Widget '{0}' already exists.".format(uid))

        self._widgets[uid] = {'widget': widget, 'weight': weight}
        self._areas[area].append(uid)

        return self

    def has_widget(self, uid: str) -> bool:
        """Check if the form has widget.
        """

        return uid in self._widgets

    def get_widget(self, uid: str) -> AbstractWidget:
        """Get a widget.
        """

        if not self.has_widget(uid):
            raise KeyError("Widget '{0}' is not exists.".format(uid))

        return self._widgets[uid]['widget']

    def _render_open_tag(self) -> str:
        """Render form's open tag.
        """

        attrs = {
            'id': self.uid,
            'name': self.name,
            'class': self.cls,
            'action': self.action,
            'method': self.method,
        }

        r = '<form {}>\n'.format(xml_attrs_str(attrs))

        return r + '\n'

    def _render_widgets(self, area: str) -> str:
        """Render widgets.
        """

        widgets_to_render = {}
        for widget_uid in self._areas[area]:
            widgets_to_render[widget_uid] = self._widgets[widget_uid]

        rendered_widgets = []
        for k, v in dict_sort(widgets_to_render):
            rendered_widgets.append(v['widget'].render())

        if not rendered_widgets:
            return ''

        return self._render_area(area, '\n'.join(rendered_widgets))

    def _render_area(self, area: str, content: str):
        """Render area.
        """

        if area == 'form':
            return content + '\n'
        else:
            return Div(content + '\n', cls='box-' + area).render()

    def _render_close_tag(self) -> str:
        """Render form's close tag.
        """

        return '</form>\n'
