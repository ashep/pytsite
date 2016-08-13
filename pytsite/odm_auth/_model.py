"""PytSite ODM Permissions Models.
"""
from typing import Tuple as _Tuple
from pytsite import odm as _odm, auth as _auth
from . import _api

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class AuthorizableEntity(_odm.model.Entity):
    """Entity which has owner and can be authorized to perform certain actions on it.
    """

    @classmethod
    def get_permission_group(cls) -> str:
        return cls.get_package_name().split('.')[-1]

    @classmethod
    def get_permissions(cls) -> _Tuple[str]:
        """Get a list of all permissions supported by this model.
        """
        return 'create', 'view', 'modify', 'delete', 'view_own', 'modify_own', 'delete_own'

    def check_permissions(self, action: str) -> bool:
        """Check current user's permissions.
        """
        return _api.check_permissions(action, self.model, self.id)

    def _pre_save(self):
        super()._pre_save()

        # If entity's owner was deleted, set it to first administrator
        for f_name in 'author', 'owner':
            if self.has_field(f_name) and not self.f_get(f_name):
                c_user = _auth.get_current_user()
                if not c_user.is_anonymous:
                    if self.is_new and c_user.has_permission('pytsite.odm_perm.create.' + self.model):
                        # Entity is new and user has permission to create it
                        self.f_set(f_name, c_user)
                    elif not self.is_new and c_user.has_permission('pytsite.odm_perm.modify.' + self.model):
                        # Entity is not new and user has permission to modify any entity of this model
                        self.f_set(f_name, c_user)
                    else:
                        # User does not have necessary permissions, make first admin as author
                        self.f_set(f_name, _auth.get_first_admin_user())
                else:
                    # Current user is anonymous, make first admin as author
                    self.f_set(f_name, _auth.get_first_admin_user())
