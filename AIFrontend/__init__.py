from pyramid.config import Configurator
from substanced.util import set_acl, get_acl

from substanced.db import root_factory
from substanced.root import Root
from substanced.event import subscribe_created

import numpy
numpy.random.seed(42)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, root_factory=root_factory)
    config.include('substanced')
    config.include('.resources')
    config.include('pyramid_retry')
    config.add_static_view(name='static', path='static')
    config.add_static_view('deformstatic', 'deform:static')
    config.scan()
    return config.make_wsgi_app()

@subscribe_created(Root)
def created(event):
    root = event.object
    root.sdi_title = 'AI Platform'
    service = root['catalogs']
    service.add_catalog('AIPlatform', update_indexes=True)
    additional_acl = [get_acl(root)[0],('Allow', 'system.Authenticated', ['retail.view_root'])]
    set_acl(root, additional_acl)

