from pyramid.httpexceptions import HTTPFound
from substanced.util import find_service, get_oid, set_acl
from substanced.sdi import mgmt_view
from substanced.form import FormView
from substanced.interfaces import IFolder

from .resources import (
    ConfigSchema,
    AreaSchema,
    ExperimentSchema,
    LogEntrySchema,
    LogSchema,
    CatVarSchema,
    ValVarSchema
)

@mgmt_view(
    context=IFolder,
    name='add_area',
    tab_title='Add Area',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddAreaView(FormView):
    title = 'Add Area'
    schema = AreaSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = appstruct.pop('name')
        item = registry.content.create('Area', **appstruct)
        self.context[name] = item
        admingroup = name + ' - admin group'
        usergroup = name + ' - user group'
        viewgroup = name + ' - view group'
        groups_service = find_service(self.request.root, 'principals', 'groups')
        groups_service[admingroup] = registry.content.create('Group')
        groups_service[usergroup] = registry.content.create('Group')
        groups_service[viewgroup] = registry.content.create('Group')
        set_acl(self.context[name], [('Allow', get_oid(groups_service[admingroup]), ['retail.add_catvar', 
                                                             'retail.add_experiment', 
                                                             'retail.add_valvar', 
                                                             'retail.use_experiment', 
                                                             'retail.view_area', 
                                                             'retail.view_log',
                                                             'retail.view_config',
                                                             'retail.configure_experiment',
                                                             'retail.view_experiment',
                                                             'retail.view_reports',
                                                             'retail.experiment.ul_data',
                                                             'retail.experiment.dl_data'
                                                             ]
                                                             ),
             ('Allow', get_oid(groups_service[usergroup]), ['retail.add_catvar', 
                                                             'retail.add_valvar', 
                                                             'retail.use_experiment', 
                                                             'retail.view_area', 
                                                             'retail.view_log',
                                                             'retail.view_config',
                                                             'retail.configure_experiment',
                                                             'retail.view_reports',
                                                             'retail.experiment.ul_data',
                                                             'retail.experiment.dl_data'
                                                             ]
                                                             ),
                                     
            ('Allow', get_oid(groups_service[viewgroup]), ['retail.view_experiment', 
                                                           'retail.view_area', 
                                                           'retail.view_log',
                                                           'retail.view_config',
                                                           'retail.view_reports',
                                                           'retail.experiment.dl_data'
                                                             ]
                                                             )])
        return HTTPFound(
            self.request.sdiapi.mgmt_path(self.context, '@@contents')
            )

@mgmt_view(
    context=IFolder,
    name='add_logentry',
    tab_title='Add LogEntry',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddLogEntryView(FormView):
    title = 'Add LogEntry'
    schema = LogEntrySchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = appstruct.pop('name')
        item = registry.content.create('LogEntry', **appstruct)
        self.context[name] = item
        return HTTPFound(
            self.request.sdiapi.mgmt_path(self.context, '@@contents')
            )

@mgmt_view(
    context=IFolder,
    name='add_experiment',
    tab_title='Add Experiment',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddExperimentView(FormView):
    title = 'Add Experiment'
    schema = ExperimentSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = appstruct.pop('name')
        item = registry.content.create('Experiment', **appstruct)
        self.context[name] = item
        return HTTPFound(
            self.request.sdiapi.mgmt_path(self.context, '@@contents')
            )

@mgmt_view(
    context=IFolder,
    name='add_config',
    tab_title='Add Config',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddConfigView(FormView):
    title = 'Add Config'
    schema = ConfigSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = appstruct.pop('name')
        item = registry.content.create('Config', **appstruct)
        self.context[name] = item
        return HTTPFound(
            self.request.sdiapi.mgmt_path(self.context, '@@contents')
            )
        
@mgmt_view(
    context=IFolder,
    name='add_log',
    tab_title='Add Log',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddLogView(FormView):
    title = 'Add Log'
    schema = LogSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = appstruct.pop('name')
        item = registry.content.create('Log', **appstruct)
        self.context[name] = item
        return HTTPFound(
            self.request.sdiapi.mgmt_path(self.context, '@@contents')
            )
        
@mgmt_view(
    context=IFolder,
    name='add_catvar',
    tab_title='Add Categorical Variable',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddCatVarView(FormView):
    title = 'Add Categorical Variable'
    schema = CatVarSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = appstruct.pop('name')
        item = registry.content.create('CatVar', **appstruct)
        self.context[name] = item
        return HTTPFound(
            self.request.sdiapi.mgmt_path(self.context, '@@contents')
            )
        
@mgmt_view(
    context=IFolder,
    name='add_valvar',
    tab_title='Add Numerical Variable',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddValVarView(FormView):
    title = 'Add Numberical Variable'
    schema = ValVarSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = appstruct.pop('name')
        item = registry.content.create('ValVar', **appstruct)
        self.context[name] = item
        return HTTPFound(
            self.request.sdiapi.mgmt_path(self.context, '@@contents')
            )