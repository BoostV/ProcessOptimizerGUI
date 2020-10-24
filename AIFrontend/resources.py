import colander
import deform


from persistent import Persistent
from substanced.util import find_catalog, find_service

from substanced.content import content
from substanced.folder import Folder
from substanced.property import PropertySheet
from substanced.schema import (
    Schema,
    NameSchemaNode
    )
from substanced.util import renamer


def config_columns(folder, subobject, request, default_columnspec):
    return default_columnspec + [
        {'name': 'Order',
         'value': getattr(subobject, 'order', None),
         }
    ]

def log_columns(folder, subobject, request, default_columnspec):
    return default_columnspec + [
        {'name': 'Description',
         'value': getattr(subobject, 'description', None),
         }
    ]
#Defines the datatype used to contain an logentry, this is to create a serperation on department levet og reseaarch group level

def context_is_a_logentry(context, request):
    return request.registry.content.istype(context, 'LogEntry')
class LogEntrySchema(Schema):
    name = NameSchemaNode(
        editing=context_is_a_logentry,
        )
    description = colander.SchemaNode(
        colander.String(),
        )
class LogEntryPropertySheet(PropertySheet):
    schema = LogEntrySchema()
@content(
    'LogEntry',
    icon = 'glyphicon glyphicon-comment',
    add_view='add_logentry',
)
class LogEntry(Persistent):    
    __sdi_addable__ = ('Experiment','CatVar')
    name = renamer()
    def __init__(self, name='', description=''):
#        super(LogEntry, self).__init__()
        self.description = description
        
#Defines the datatype used to contain an Categoricla opmisation varialbel, this is to create a serperation on department levet og reseaarch group level

class catvar_options(colander.SequenceSchema):
    option = colander.SchemaNode(colander.String())

def context_is_a_catvar(context, request):
    return request.registry.content.istype(context, 'CatVar')
class CatVarSchema(Schema):
    name = NameSchemaNode(
        editing=context_is_a_catvar,
        )
    description = colander.SchemaNode(
        colander.String()                              
        )
    options = catvar_options()
    order = colander.SchemaNode(
        colander.Integer()                        
        )
class CatVarPropertySheet(PropertySheet):
    schema = CatVarSchema()
    
@content(
    'CatVar',
    icon = 'glyphicon glyphicon-list',
    add_view='add_catvar',
)
class CatVar(Persistent):    
    __sdi_addable__ = ()
    name = renamer()
    def __init__(self, name='', description='', options='', order = 0):
        self.order = order
        self.options = options
        self.description = description
        
        
#Defines the datatype used to contain an numerical opmisation varialbel, this is to create a serperation on department levet og reseaarch group level

def context_is_a_valvar(context, request):
    return request.registry.content.istype(context, 'ValVar')
class ValVarSchema(Schema):
    name = NameSchemaNode(
        editing=context_is_a_valvar,
        )               
    description = colander.SchemaNode(
        colander.String()                              
        )
    minval = colander.SchemaNode(
        colander.Float()                        
        )
    maxval = colander.SchemaNode(
        colander.Float()                        
        )        
    order = colander.SchemaNode(
        colander.Integer()                        
        )
class ValVarPropertySheet(PropertySheet):
    schema = ValVarSchema()
    
@content(
    'ValVar',
    icon = 'glyphicon glyphicon-minus',
    add_view='add_valvar',
)
class ValVar(Persistent):    
    __sdi_addable__ = ()
    name = renamer()
    def __init__(self, name='', description='', minval=0.0, maxval=0.0, order=0):
        self.order = order
        self.description = description
        self.minval = minval
        self.maxval = maxval
        
        
#Defines the datatype used to contain an area, this is to create a serperation on department levet og reseaarch group level

def context_is_a_area(context, request):
    return request.registry.content.istype(context, 'Area')
class AreaSchema(Schema):
    name = NameSchemaNode(
        editing=context_is_a_area,
        )
    description = colander.SchemaNode(
        colander.String(),
        )   
class AreaPropertySheet(PropertySheet):
    schema = AreaSchema()
@content(
    'Area',
    icon = 'glyphicon glyphicon-globe',
    add_view='add_area',
)
class Area(Folder):    
    __sdi_addable__ = ('Experiment',)
    name = renamer()

    def __init__(self, name='', description=''):
        super(Area, self).__init__()
        self.description = description
        


#defines the datatype to contain an the actual experiment, this object will contain the optimizer and creation of this object
#automatically creates the associated log object and config opject

def context_is_a_experiment(context, request):
    return request.registry.content.istype(context, 'Experiment')    
class ExperimentSchema(Schema):
    name = NameSchemaNode(
        editing=context_is_a_experiment                  
        )
    description = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.RichTextWidget(options=(('browser_spellcheck', True),)),
                description='Enter some text')
class ExperimentPropertySheet(PropertySheet):
    schema = ExperimentSchema()
@content(
    'Experiment',
    icon = 'glyphicon glyphicon-cog',
    add_view='add_experiment',
    after_create = 'after_creation',     
)
class Experiment(Folder):
    __sdi_addable__ = ()
    name = renamer()
    
    def __init__(self, name='', description=''):
        super(Experiment, self).__init__()
        self.description = description

    def after_creation(self, intr, registry):
        intr['config'] = registry.content.create('Config')
        intr['log'] = registry.content.create('Log')
        intr['convergence_plot'] = registry.content.create('File', mimetype='image/png')
        intr['objective_plot'] = registry.content.create('File', mimetype='image/png')
        


#defines the datatype to contain an the config if the experiment, this object will contain the 
def context_is_an_config(context, request):
    return request.registry.content.istype(context, 'Config')
class ConfigSchema(Schema):
    name = NameSchemaNode(
        editing=context_is_an_config,
        )
    base_estimator = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.SelectWidget(values=(
                ('GP','GP'),
                ('RF','RF'),
                ('ET','ET'),
                ('GBRT','GBRT')
                )
            )
                                         
        )
    acq_func = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.SelectWidget(values=(
                ('gp_hedge','gp_hedge'),
                ('LCB','LCB'),
                ('EI','EI'),
                ('PI','PI')
                )
            )                                 
        )
    n_initial_points = colander.SchemaNode(
        colander.Integer(),
        default = 3                                 
        )
    kappa = colander.SchemaNode(
        colander.Float(),
        default=1.96                                 
        )
    xi = colander.SchemaNode(
        colander.Float(),
        default = 0.01                                 
        )        
    configured = colander.SchemaNode(
        colander.Boolean()                             
        )
class ConfigPropertySheet(PropertySheet):
    schema = ConfigSchema()
@content(
    'Config',
    icon='glyphicon glyphicon-wrench',
    columns  = config_columns,
    )
class Config(Folder):
    __sdi_addable__ = ('CatVar','ValVar',)
    name = renamer()
    def __init__(self, name='', configured=False, base_estimator='', acq_func='', n_initial_points=3, kappa=1.96, xi=0.1):
        super(Config, self).__init__()
        self.base_estimator = base_estimator
        self.acq_func = acq_func
        self.n_initial_points = n_initial_points
        self.kappa = kappa
        self.xi = xi
        self.configured = configured
        
    def gen_hyperparams(self):
        return {'base_estimator': self.base_estimator,
                'acq_func':self.acq_func,
                'n_initial_points':self.n_initial_points,
                'acq_func_kwargs':{'kappa': self.kappa, 'xi': self.xi}
                }
    def gen_opt_vars(self, context, request):
        system_catalog = find_catalog(request.context, 'system')
        order_catalog = find_catalog(request.context, 'AIPlatform')
        q1 = system_catalog['content_type']
        q2 = system_catalog['path']
        q = q1.eq('ValVar') & q2.eq(request.resource_path(context)) | q1.eq('CatVar') & q2.eq(request.resource_path(context))
        resultset = q.execute()
        return resultset.sort(order_catalog['order'])
    
    def generate_space(self, context, request):
        opt_vars = self.gen_opt_vars(context, request)
        space = []
        for var in opt_vars:
            if request.registry.content.istype(var, 'CatVar'):
                space.append(var.options)
            elif request.registry.content.istype(var, 'ValVar'):
                space.append((var.minval, var.maxval))
        return space
    
    


#defines the datatype to contain an the log if the experiment, this object will contain the 
        
def context_is_an_log(context, request):
    return request.registry.content.istype(context, 'Log')
class LogSchema(Schema):
    name = NameSchemaNode(
        editing=context_is_an_log,
        )    
class LogPropertysheet(PropertySheet):
    schema = LogSchema()    
@content(
         'Log',
         icon='glyphicon glyphicon-book',
         columns = log_columns,
         )
class Log(Folder):
    __sdi_addable__ = ('LogEntry',)
    name = renamer()
    def __init__(self, name=''):
        super(Log, self).__init__()
        

 

def includeme(config): # pragma: no cover
    config.add_propertysheet('Basic', ConfigPropertySheet, Config)
    config.add_propertysheet('Basic', AreaPropertySheet, Area)
    config.add_propertysheet('Basic', ExperimentPropertySheet, Experiment)
    config.add_propertysheet('Basic', LogEntryPropertySheet, LogEntry)
    config.add_propertysheet('Basic', LogPropertysheet, Log)
    config.add_propertysheet('Basic', CatVarPropertySheet, CatVar)
    config.add_propertysheet('Basic', ValVarPropertySheet, ValVar)
