"""ODM UI Models.
"""
from pytsite import html as _html, lang as _lang, widget as _widget, odm as _odm, validation as _validation, \
    http as _http, router as _router, metatag as _metatag, auth as _auth, odm_ui as _odm_ui

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class UserUI(_auth.model.User, _odm_ui.UIMixin):
    """User UI.
    """
    def _setup_fields(self):
        super()._setup_fields()
        self.define_field(_odm.field.Bool('profile_is_public'))

    @property
    def profile_is_public(self) -> bool:
        return self.f_get('profile_is_public')

    @property
    def profile_view_url(self) -> str:
        return _router.ep_url('pytsite.auth_ui.ep.profile_view', {'nickname': self.nickname})

    @property
    def profile_edit_url(self) -> str:
        return _router.ep_url('pytsite.auth_ui.ep.profile_edit', {
            'nickname': self.nickname,
            '__redirect': _router.current_url(),
        })

    @classmethod
    def ui_browser_setup(cls, browser):
        """Setup ODM UI browser hook.

        :type browser: pytsite.odm_ui._browser.Browser
        :return: None
        """
        browser.data_fields = 'login', 'full_name', 'roles', 'status', 'profile_is_public', 'is_online', '_created', \
                              'last_activity'
        browser.default_sort_field = 'last_activity'

    def ui_browser_get_row(self) -> tuple:
        """Get single UI browser row hook.
        """
        groups_cell = ''
        for role in self.f_get('roles'):
            cls = 'label label-default'
            if role.name == 'admin':
                cls += ' label-danger'
            groups_cell += str(_html.Span(_lang.t(role.description), cls=cls)) + ' '

        status_cls = 'info' if self.status == 'active' else 'default'

        return (
            self.login,
            self.full_name,
            groups_cell,
            '<span class="label label-{}">{}</span>'.format(status_cls,
                                                            _lang.t('pytsite.auth@status_' + self.f_get('status'))),
            '<span class="label label-info">{}</span>'.format(self.t('word_yes')) if self.profile_is_public else '',
            '<span class="label label-success">{}</span>'.format(self.t('word_yes')) if self.is_online else '',
            self.f_get('_created', fmt='pretty_date_time'),
            self.f_get('last_activity', fmt='pretty_date_time')
        )

    def ui_m_form_setup(self, frm):
        """Modify form setup hook.

        :type frm: pytsite.form.Form
        """
        current_user = _auth.get_current_user()

        _metatag.t_set('title', self.t('profile_edit'))

        # Profile is public
        frm.add_widget(_widget.select.Checkbox(
            weight=10,
            uid='profile_is_public',
            value=self.f_get('profile_is_public'),
            label=self.t('profile_is_public'),
        ))

        # Image
        from pytsite import image
        frm.add_widget(image.widget.ImagesUpload(
            weight=20,
            uid='picture',
            label=self.t('picture'),
            value=self.picture,
            max_file_size=1,
        ))

        # Login
        if current_user.has_permission('pytsite.odm_ui.modify.user'):
            frm.add_widget(_widget.input.Email(
                weight=30,
                uid='login',
                value=self.f_get('login'),
                label=self.t('login'),
                required=True,
            ))
            frm.add_rule('login', _odm.validation.FieldUnique(
                'pytsite.auth_ui@this_login_already_used',
                model='user',
                field='login',
                exclude_ids=self.id
            ))

        # Nickname
        frm.add_widget(_widget.input.Text(
            weight=40,
            uid='nickname',
            value=self.f_get('nickname'),
            label=self.t('nickname'),
            required=True,
        ))
        frm.add_rules('nickname', (
            _auth.user_nickname_rule,
            _odm.validation.FieldUnique(
                msg_id='pytsite.auth_ui@this_nickname_already_used',
                model=self.model,
                field='nickname',
                exclude_ids=self.id
            )
        ))

        # First name
        frm.add_widget(_widget.input.Text(
            weight=50,
            uid='first_name',
            value=self.first_name,
            label=self.t('first_name'),
            required=True,
        ))

        # Last name
        frm.add_widget(_widget.input.Text(
            weight=60,
            uid='last_name',
            value=self.last_name,
            label=self.t('last_name'),
        ))

        # Email
        frm.add_widget(_widget.input.Email(
            weight=70,
            uid='email',
            value=self.f_get('email'),
            label=self.t('email'),
            required=True,
        ))
        frm.add_rule('email', _odm.validation.FieldUnique(
            msg_id='pytsite.auth_ui@this_email_already_used',
            model=self.model,
            field='email',
            exclude_ids=self.id
        ))

        # Password
        frm.add_widget(_widget.input.Password(
            weight=80,
            uid='password',
            label=self.t('password'),
        ))

        # Country
        frm.add_widget(_widget.input.Text(
            weight=90,
            uid='country',
            label=self.t('country'),
            value=self.country,
        ))

        # City
        frm.add_widget(_widget.input.Text(
            weight=100,
            uid='city',
            label=self.t('city'),
            value=self.city,
        ))

        # Description
        frm.add_widget(_widget.input.TextArea(
            weight=110,
            uid='description',
            value=self.f_get('description'),
            label=self.t('about_yourself'),
            max_length=1024,
        ))

        # Status
        if current_user.has_permission('pytsite.odm_ui.modify.user'):
            frm.add_widget(_widget.select.Select(
                weight=120,
                uid='status',
                value=self.f_get('status'),
                label=self.t('status'),
                items=_auth.get_user_statuses(),
                h_size='col-sm-5 col-md-4 col-lg-3',
                required=True,
            ))

        # URLs
        frm.add_widget(_widget.input.StringList(
            weight=130,
            uid='urls',
            label=self.t('social_links'),
            value=self.urls,
            max_values=5,
            add_btn_label=self.t('add_link'),
        ))
        frm.add_rule('urls', _validation.rule.Url())

        # Roles
        if current_user.has_permission('pytsite.odm_ui.modify.user'):
            frm.add_widget(_odm_ui.widget.EntityCheckboxes(
                weight=140,
                uid='roles',
                label=self.t('roles'),
                model='role',
                caption_field='description',
                value=self.f_get('roles'),
            ))
            frm.add_rule('roles', _odm.validation.ODMEntitiesList(model='role'))

        # Token
        if not self.is_new and current_user.has_permission('pytsite.odm_ui.modify.user'):
            frm.add_widget(_widget.input.Text(
                weight=150,
                uid='token',
                value=self.f_get('token'),
                label=self.t('token'),
            ))
            frm.add_rules('token', (
                _validation.rule.Regex(pattern='^[a-f0-9]{32}$'),
                _odm.validation.FieldUnique(
                    msg_id='pytsite.auth_ui@this_token_already_used',
                    model=self.model,
                    field='token',
                    exclude_ids=self.id)
            ))

    def ui_entity_deletion_allowed(self) -> bool:
        return False if _auth.get_current_user().id == self.id else True

    def ui_mass_action_get_entity_description(self) -> str:
        """Get delete form description.
        """
        return self.login


class RoleUI(_auth.model.Role, _odm_ui.UIMixin):
    """Role UI.
    """
    @classmethod
    def ui_browser_setup(cls, browser):
        """Setup ODM UI browser hook.

        :type browser: pytsite.odm_ui._browser.Browser
        """
        browser.data_fields = 'name', 'description', 'permissions'

    def ui_browser_get_row(self) -> tuple:
        """Get single UI browser row hook.
        """
        if self.f_get('name') == 'admin':
            return

        perms = []
        for perm_name in self.f_get('permissions'):
            perm = _auth.get_permission(perm_name)
            cls = 'label label-default permission-' + perm[0]
            if perm[0] == 'admin':
                cls += ' label-danger'
            perms.append(str(_html.Span(_lang.t(perm[1]), cls=cls)))

        return self.f_get('name'), _lang.t(self.f_get('description')), ' '.join(perms)

    def ui_m_form_setup(self, frm):
        """Modify form setup hook.
        :type frm: pytsite.form.Form
        """
        if self.f_get('name') == 'admin':
            raise _http.error.Forbidden()

        frm.add_widget(_widget.input.Text(
            weight=10,
            uid='name',
            value=self.f_get('name'),
            label=self.t('name'),
            required=True,
        ))

        frm.add_widget(_widget.input.Text(
            weight=20,
            uid='description',
            value=self.f_get('description'),
            label=self.t('description'),
            required=True,
        ))

        # Permissions tabs
        perms_tabs = _widget.static.Tabs('permissions-tabs', weight=30, label=self.t('permissions'))
        for group in _auth.get_permission_groups():
            if group[0] == 'auth':
                continue

            tab_content = _html.Div()
            for perm in _auth.get_permissions(group[0]):
                p_name = perm[0]
                tab_content.append(
                    _html.Div(cls='checkbox').append(
                        _html.Label(_lang.t(perm[1]), label_for='permissions-checkbox-' + p_name).append(
                            _html.Input(type='checkbox', uid='permissions-checkbox-' + p_name,
                                        name='permissions', value=p_name, checked=p_name in self.permissions)
                        )
                    )
                )
            perms_tabs.add_tab('permissions-' + group[0], _lang.t(group[1]), tab_content.render())

        frm.add_widget(_widget.input.Hidden('permissions', value=''))
        frm.add_widget(perms_tabs)

    def ui_mass_action_get_entity_description(self) -> str:
        """Get delete form description.
        """
        return _lang.t(self.description)
