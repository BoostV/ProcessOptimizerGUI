from substanced.catalog import (
    catalog_factory,
    Text,
    indexview,
    indexview_defaults,
    Field
    )
from .resources import ValVar, CatVar


@catalog_factory('AIPlatform')
class CatalogFactory(object):
    order = Field()


@indexview_defaults(catalog_name='AIPlatform')
class CatalogViews(object):
    """
    The catalog views are used by the catalog to get the actual value that we
    want to store for each field. This allows us to examine the value before
    indexing and pass in a modified value if necessary. "indexview_defaults"
    are for setting parameters that will be used in all the class views. Here,
    the views will be set for the catalog named "AIPlatform",
    which is the one we created above.
    """
    def __init__(self, resource):
        self.resource = resource

    @indexview(context=CatVar)
    @indexview(context=ValVar)
    def order(self, default):
        return getattr(self.resource, 'order', default)
