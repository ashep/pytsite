"""Flag Package Endpoints.
"""
from pytsite import auth as _auth, odm as _odm
from . import _functions

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def toggle(args: dict, inp: dict) -> dict:
    current_user = _auth.get_current_user()
    uid = inp.get('uid')

    print('TOGGLE')

    if current_user.is_anonymous or not uid:
        return

    e = _odm.find('flag').where('uid', '=', uid).where('author', '=', current_user).first()
    if e:
        e.delete()
        return {'status': 'unflagged', 'count': _functions.count(uid)}

    _odm.dispense('flag').f_set('uid', uid).f_set('author', current_user).save()

    return {'status': 'flagged', 'count': _functions.count(uid)}
