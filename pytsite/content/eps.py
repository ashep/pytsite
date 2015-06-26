"""Content Plugin Endpoints.
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite import content as _content, disqus as _disqus
from pytsite.core import reg as _reg, http as _http, router as _router, metatag as _metatag, assetman as _assetman


def view(args: dict, inp: dict):
    """View Content Entity.
    """
    model = args.get('model')
    entity = _content.manager.find(model).where('_id', '=', args.get('id')).first()
    if not entity:
        raise _http.error.NotFoundError()

    current_cc = entity.f_get('comments_count')
    actual_cc = _disqus.functions.get_comments_count(_router.current_url(True))
    if actual_cc != current_cc:
        entity.f_set('comments_count', actual_cc).save()

    _metatag.t_set('title', entity.f_get('title'))

    endpoint = _reg.get('content.endpoints.view.' + model, 'app.eps.' + model + '_view')

    _assetman.add('pytsite.content@js/content.js')

    return _router.call_endpoint(endpoint, {'entity': entity})


def view_count(args: dict, inp: dict) -> int:
    model = inp.get('model')
    eid = inp.get('id')

    if model and eid:
        entity = _content.manager.find(model).where('_id', '=', eid).first()
        if entity:
            entity.f_inc('views_count').save()
            return entity.f_get('views_count')

    return 0
