"""PytSite ODM Permissions API Functions.
"""
from typing import Iterable as _Iterable
from pytsite import permission as _permission, auth as _auth, odm as _odm

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def check_permissions(perm_type: str, model: str, ids: _Iterable = None) -> bool:
    """Check current user's permissions to operate with entity(es).
    """
    # Get current user
    current_user = _auth.get_current_user()

    # Check ids type
    if ids and type(ids) not in (list, tuple):
        ids = (ids,)

    if perm_type == 'create':
        create_perm_name = 'pytsite.odm_perm.create.' + model
        if _permission.is_permission_defined(create_perm_name) and current_user.has_permission(create_perm_name):
            return True
    else:
        # If 'global' permission was not defined
        global_perm_name = 'pytsite.odm_perm.' + perm_type + '.' + model
        if not _permission.is_permission_defined(global_perm_name):
            return False

        # If user has 'global' permissions for model
        if current_user.has_permission(global_perm_name):
            return True

        # If 'personal' permission was not defined
        personal_perm_name = 'pytsite.odm_perm.' + perm_type + '_own.' + model
        if not _permission.is_permission_defined(personal_perm_name):
            return False

        # Else check user's personal permission
        if current_user.has_permission(personal_perm_name):
            if ids:
                # Check each entity
                for eid in ids:
                    entity = _odm.dispense(model, eid)

                    # Anyone cannot do anything with non-existent entities
                    if not entity:
                        return False

                    # Searching for author of the entity
                    for author_field in 'author', 'owner':
                        if entity.has_field(author_field) and entity.f_get(author_field).id == current_user.id:
                            return True
            else:
                return True

    return False
