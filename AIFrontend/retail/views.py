from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPForbidden
from deform import Form, ValidationFailure
import deform
from pyramid.view import view_config, view_defaults
from substanced.util import find_catalog, find_objectmap
from ..resources import Config, Experiment, Area, CatVarSchema, ValVarSchema, ConfigSchema, ExperimentSchema, Log
from pyramid.httpexceptions import HTTPFound
from substanced.file import File
import colander
from ProcessOptimizer import Optimizer, expected_minimum
from ProcessOptimizer.plots import plot_objective, plot_convergence
from ProcessOptimizer.utils import cook_estimator
from ProcessOptimizer.learning.gaussian_process.kernels import Matern
import numpy
numpy.random.seed(42)


from substanced.util import find_service, oid_of, get_oid
import datetime
from pyramid.security import (
    remember,
    forget
)
from io import StringIO
from matplotlib.pyplot import savefig
from matplotlib.pyplot import clf as pyplotclose
import csv
from pyramid.response import Response



@view_config(
    context  = HTTPForbidden,
    renderer = 'templates/denied.pt'       
    )
def denied_view(context, request):
    if request.authenticated_userid == None:
        username = None
    else:
        username = find_objectmap(request.root).object_for(request.authenticated_userid).name
    return {'master': get_renderer('templates/main.pt').implementation(),
            'authenticated_user': username
            }

#View used to handle login request, when logging in from the login form in the navbar, this view has no special permission
@view_config(
    name = 'login',
    renderer='templates/root.pt',
    )
def login_view(context, request):
    login = request.params['login']
    password = request.params['password']
    principals = find_service(context, 'principals')
    users = principals['users']
    user = users.get(login)
    if user is not None and user.check_password(password):
        headers = remember(request, oid_of(user))
        return HTTPFound(location=request.referer, headers=headers)
    return HTTPFound(location=request.referer)

#View used to handle logou request, this view has no special permission

@view_config(
    name = 'logout',
    renderer='templates/root.pt',
    )
def logout_view(context, request):
    headers = forget(request)
    return HTTPFound(location=request.resource_url(request.root),
                     headers=headers)




#View used to diplay the list of areas in the root of the site.
@view_config(
    renderer='templates/root.pt',
    permission='retail.view_root'
    )
def default_view(context, request):
    catalog = find_catalog(request.context, 'system')
    content_type = catalog['content_type']
    path = catalog['path']
    q = content_type.eq('Area') & path.eq(context)
    Areas = q.execute()
    return {'master': get_renderer('templates/main.pt').implementation(),
            'areas': Areas,
            'authenticated_user': find_objectmap(context).object_for(request.authenticated_userid).name,
            }



#View used to display the areas view contianing a list of experiments
@view_config(
    context=Area,
    renderer='templates/area.pt',
    permission = 'retail.view_area'
    )
def area_view(context, request):
    catalog = find_catalog(request.context, 'system')
    q1 = catalog['content_type']
    q2 = catalog['path']
    q = q1.eq('Experiment') & q2.eq(request.resource_path(context))
    resultset = q.execute()
    return {'master': get_renderer('templates/main.pt').implementation(),
            'experiments': resultset,
            'authenticated_user': find_objectmap(context).object_for(request.authenticated_userid).name
           }


@view_config(
    name = 'reports',
    context = Experiment,
    renderer='templates/reports.pt',
    attr='view_report',
    permission='retail.view_reports'
    )
class reports_view(object):
    def __init__(self,context, request):
        self.request = request
        self.context = context
        self.result = context.result
        if getattr(context,'img_result', None) is not context.result and len(getattr(self.context.result, 'x_iters', [])) >= self.context['config'].n_initial_points:
            pyplotclose()
            plot_convergence(context.result)
            with open('tmp/'+ str(get_oid(context)) +'_convergence.png', 'wb') as imgfile:
                savefig(imgfile,  bbox_inches='tight', pad_inches=0)
            with open('tmp/'+ str(get_oid(context)) +'_convergence.png', 'rb') as imgfile:
                context['convergence_plot'].upload(imgfile) 
            pyplotclose()
            dimensions = []
            names = self.context['config'].gen_opt_vars(self.context, request)
            for var in names:
                dimensions.append(var.name[:20])           
            plot_objective(context.result, dimensions=dimensions, usepartialdependence=False)
            with open('tmp/'+ str(get_oid(context)) +'_objectve.png', 'wb') as imgfile:
                savefig(imgfile,  bbox_inches='tight', pad_inches=0)
            with open('tmp/'+ str(get_oid(context)) +'_objectve.png', 'rb') as imgfile:
                context['objective_plot'].upload(imgfile)
            pyplotclose()
            context.img_result = context.result
            if getattr(context,'contains_catvar', False) == False :
                context.expected_minimum = expected_minimum(context.result)
            else:
                context.expected_minimum = None
        self.r_dict = {'master': get_renderer('templates/main.pt').implementation(),
                       'authenticated_user': find_objectmap(context).object_for(request.authenticated_userid).name}
        
    def view_report(self):
        header_list = []
        for title in self.context['config'].gen_opt_vars(self.context,self.request):
            header_list.append(title.name)
        header_list.append('Result')
        result_list=[]

        for inputval,result in zip(self.context.optimizer.Xi, self.context.optimizer.yi):
            temp_list =  []
            temp_list.extend(inputval)
            temp_list.append(result)
            result_list.append(temp_list)
        if getattr(self.context['config'], 'configured', False) == True:                                               
            if getattr(self.context, 'expected_minimum', None) is not None:
                temp_exp_min =[]
                for entry,value in zip(header_list[:-1], self.context.expected_minimum[0]):
                    temp_exp_min.append([entry, value])
                exp_min_out = {'value':temp_exp_min, 'result':self.context.expected_minimum[1]}
                self.r_dict['exp_min'] = exp_min_out
            else:
                pass

        self.r_dict['input_header'] = header_list
        self.r_dict['input_values'] = result_list
        
        return self.r_dict


@view_defaults(
    context=Experiment,
    renderer='templates/experiment.pt',
    )
@view_config(
    permission='retail.use_experiment',
    attr='multiple_dl',
    request_param='dl_multiple'
             
    )
@view_config(
    permission='retail.experiment.ul_data',
    attr='ul_data',
    request_param='ul_expdata'                          
    )
@view_config(
    permission='retail.experiment.dl_data',
    attr='dl_data',
    request_param='dl_expdata'                          
    )
@view_config(
    permission='retail.use_experiment',
    attr='add_datapoint',
    request_param='Submit'
    )    
@view_config(
    permission='retail.view_experiment',
    attr='disp_exp',
    )
class experiment_view(object):
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.cfg = context['config']
        self.next_x = []
        self.exp_min_out = []
        self.input_form = self.gen_input_form()
        if getattr(context['config'], 'configured', False) == True:                                               
            for entry, value in zip(self.cfg.gen_opt_vars(self.cfg, self.request), context.optimizer.ask(n_points=1)[0]):
                self.next_x.append([entry.name,value])

        self.r_dict = {'master': get_renderer('templates/main.pt').implementation(),
                       'exp_desc':context.description,
                       'next_exp':self.next_x,
                       'data_form': self.input_form.render(),
                       'authenticated_user': find_objectmap(context).object_for(request.authenticated_userid).name,
                       }
        
    def add_datapoint(self):
        try:
            controls = self.request.POST.items()
            appstruct = self.input_form.validate(controls)
        except ValidationFailure as e:
            self.r_dict['data_form'] = e.render()
            return self.r_dict
        dataset = []
        for entry in self.cfg.gen_opt_vars(self.cfg, self.request):
            dataset.append(appstruct[entry.name])
        
        item = self.request.registry.content.create('LogEntry')
        item.description = 'Datapoint added ' + str(dataset) + "  " + str(appstruct['Result'])
        self.context['log'][datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = item     
        self.context.result = self.context.optimizer.tell(dataset, appstruct['Result'])
        return HTTPFound(self.request.resource_url(self.context))
        
    def disp_exp(self):        
        if self.context['config'].configured == False:
            return HTTPFound(self.request.resource_url(self.context['config']))  
        return self.r_dict
    
    def dl_data(self):
        header_list=[]
        for i in self.cfg.gen_opt_vars(self.cfg, self.request):
            header_list.append(i.name)
        header_list.append('Result')    
        output = StringIO()
        csvwriter = csv.writer(output,delimiter=';', dialect=csv.excel)
        csvwriter.writerow(header_list)
        for optinput,result in zip(self.context.optimizer.Xi, self.context.optimizer.yi):
            temp_list = []
            temp_list.extend(optinput)
            temp_list.append(result)
            csvwriter.writerow(temp_list)
        response = Response(output.getvalue())
        output.flush()
        output.close()
        response.headers['Content-type'] = 'text/csv'
        response.headers['Content-disposition'] = 'attachment; filename='+self.context.name+'.csv'
        return response

    def ul_data(self):
        try:
            input_file = self.request.POST['mp3'].file
            input_str = input_file.read()
        except Exception as e:
            self.r_dict['validationerror'] = e
            return self.r_dict
        dataset = []
        try:
            csvreader = csv.reader(StringIO(input_str.decode('UTF-8')),delimiter=';', dialect=csv.excel)
            for row in csvreader:
                dataset.append(row)
            dataset.pop(0)
        except Exception as e:
            self.r_dict['validationerror'] = e
            return self.r_dict
        try:
            input_list = []
            result_list = []
            for entry in dataset:
                fl_entry = []
                for value in entry:
                    try:  
                        fl_entry.append(float(value))
                    except ValueError as e:
                        fl_entry.append(value)

                result_list.append(fl_entry.pop())
                input_list.append(fl_entry)
            self.context.result = self.context.optimizer.tell(input_list,result_list)
            
        except Exception as e:
            self.r_dict['validationerror'] = e
            return self.r_dict
        return self.r_dict
    
    
    
    def multiple_dl(self):
        try:
            number_of_exp = int(self.request.POST['exp_number'])
        except Exception as e:
            self.r_dict['validationerror'] = e
            return self.r_dict

        next_exps = self.context.optimizer.ask(n_points=number_of_exp)
        header_list=[]
        for i in self.cfg.gen_opt_vars(self.cfg, self.request):
            header_list.append(i.name)
        header_list.append('Result')    
        output = StringIO()
        csvwriter = csv.writer(output,delimiter=';', dialect=csv.excel)
        csvwriter.writerow(header_list)
        for i in next_exps:
            csvwriter.writerow(i)
        response = Response(output.getvalue())
        output.flush()
        output.close()
        response.headers['Content-type'] = 'text/csv'
        response.headers['Content-disposition'] = 'attachment; filename='+self.context.name+'.csv'
        return response            
            
        


        

    
    def gen_input_form(self):
        schema = colander.Schema()
        for entry in self.cfg.gen_opt_vars(self.cfg, self.request):
            if self.request.registry.content.istype(entry ,'ValVar'):
                    schema.add(colander.SchemaNode(
                                        colander.Float(),
                                        name = entry.name,
                                        validator=colander.Range(entry.minval, entry.maxval)
                                        )
                       )    
            if self.request.registry.content.istype(entry ,'CatVar'):
                choices = ()
                for value in entry.options:
                    choices = choices + ((value,value),)
                schema.add(colander.SchemaNode(colander.String(),
                                name = entry.name,
                                widget=deform.widget.SelectWidget(values=choices)
                                ))
        schema.add(colander.SchemaNode(colander.Float(), name='Result'))
        form = Form(schema, buttons=('Submit',), autocomplete=False)
        return form
    



@view_defaults(context=Config,
               renderer='templates/config.pt',)
@view_config(
    permission='retail.configure_experiment',
    attr='del_var',
    request_param='Delete'
    )
@view_config(
    permission='retail.configure_experiment',
    attr='add_var',
    request_param='variable_type'
    )
@view_config(
    permission='retail.configure_experiment',
    attr='configure_experiment',
    request_param='Configure'
    )
@view_config(
    permission='retail.use_experiment',
    attr='reinitiate_report',
    request_param='Reinitiate_report'
    )
@view_config(
    permission='retail.configure_experiment',
    attr='reinitiate',
    request_param='Reinitiate'
    )
@view_config(
    permission='retail.view_config',
    attr='view_setup'
    )
class config_view(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.parent = context.__parent__
        self.opt_vars = context.gen_opt_vars(context, request)
        schema = ConfigSchema()
        del schema['name']
        del schema['configured']
        self.paramsform = Form(schema, buttons=('Configure',))
        self.r_dict = {'master': get_renderer('templates/main.pt').implementation(),
                       'variables': self.opt_vars.all(),
                       'configured':context.configured,
                       'authenticated_user': find_objectmap(self.context).object_for(self.request.authenticated_userid).name,
                       'params_form': self.paramsform.render(),
                       } 
    
    def add_var(self):
        if self.request.POST['variable_type'] == 'valvar':
            return HTTPFound(self.request.resource_url(self.context, 'valvar_post_action'))  
        elif self.request.POST['variable_type'] == 'catvar':
            return HTTPFound(self.request.resource_url(self.context, 'catvar_post_action'))
        
    def reinitiate(self):
        x_values = self.parent.optimizer.Xi
        y_values = self.parent.optimizer.yi
        print(x_values, y_values)
        space = self.context.generate_space(self.context, self.request)
        hyperparams = {'base_estimator':self.context.base_estimator,
                       'acq_func':self.context.acq_func,
                       'n_initial_points':self.context.n_initial_points,
                       'acq_func_kwargs':{'kappa': self.context.kappa, 'xi': self.context.xi}}
        print(self.context.__parent__.contains_catvar)
        print(self.context.base_estimator)
        if self.context.__parent__.contains_catvar == False and self.context.base_estimator == "GP":
            ls = [1]*len(space)
            kernel_intern = 1**2 * Matern(length_scale=ls,
                                          length_scale_bounds=[(0.2, 1.0)],
                                          nu=2.5)
            hyperparams['base_estimator'] = cook_estimator(base_estimator = "GP",
                                                           space= space,
                                                           kernel = kernel_intern, 
                                                           noise= 'gaussian',
                                                           n_restarts_optimizer=10)
            self.parent.optimizer = Optimizer(space, **hyperparams) 
            self.parent.result = self.parent.optimizer.tell(x_values,y_values)
            
        else:
            print("not trigfgered")
            pass
        
        return HTTPFound(self.request.resource_url(self.parent))
    
    def reinitiate_report(self):
        self.context.__parent__.img_result = None
        print("reinitiating the report")
        return HTTPFound(self.request.resource_url(self.parent))
    
    def del_var(self):
        del self.context[self.request.POST['rem_id']]
        return HTTPFound(self.request.resource_url(self.parent)) 
    def configure_experiment(self):
        try:
            controls = self.request.POST.items()
            appstruct = self.paramsform.validate(controls)
        except ValidationFailure as e:
            self.r_dict['params_form'] = e.render()
            return self.r_dict
        for key,value in appstruct.items():
            setattr(self.context, key, value)
        self.context.configured = True
        space = self.context.generate_space(self.context, self.request)
        
        for entry in self.context.gen_opt_vars(self.context, self.request):
            if self.request.registry.content.istype(entry ,'CatVar'):
                self.context.__parent__.contains_catvar = True
        if not hasattr(self.context.__parent__, 'contains_catvar'):
            self.context.__parent__.contains_catvar = False
        
        hyperparams = {'base_estimator':self.context.base_estimator,
                       'acq_func':self.context.acq_func,
                       'n_initial_points':self.context.n_initial_points,
                       'acq_func_kwargs':{'kappa': self.context.kappa, 'xi': self.context.xi}}
        
        if self.context.__parent__.contains_catvar == False and self.context.base_estimator == "GP":
            ls = [1]*len(space)
            kernel_intern = 1**2 * Matern(length_scale=ls,
                                          length_scale_bounds=[(0.05, 10)],
                                          nu=2.5)
            hyperparams['base_estimator'] = cook_estimator(base_estimator = "GP",
                                                           space= space,
                                                           kernel = kernel_intern, 
                                                           noise= 'gaussian',
                                                           n_restarts_optimizer=10)
            self.parent.optimizer = Optimizer(space, **hyperparams)
        else:
            self.parent.optimizer = Optimizer(space, **hyperparams)
        item = self.request.registry.content.create('LogEntry')
        item.description = 'Experiment confgured with space ' + str(space) + ' and hyperparms ' + str(hyperparams)
        self.parent['log'][datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = item       
        return HTTPFound(self.request.resource_url(self.parent))
    def view_setup(self):
        return self.r_dict
    

        




@view_config(
    name='valvar_post_action',
    context=Config,
    renderer='templates/config_post.pt',
    permission='retail.add_valvar'
    )
def config_view_post_action_varval(context, request):
    schema = ValVarSchema()
    schema['name'] = colander.SchemaNode(colander.String(), name='Name')
    form = Form(schema,buttons=('submit',))    
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            return {'master': get_renderer('templates/main.pt').implementation(),
                    'vartype':'value variable',
                    'form': e.render(),
                    'authenticated_user': find_objectmap(context).object_for(request.authenticated_userid).name
                    }
        registry = request.registry
        name = appstruct.pop('name')
        item = registry.content.create('ValVar', **appstruct)
        context[name] = item
        return HTTPFound(request.resource_url(context))
    return {'master': get_renderer('templates/main.pt').implementation(),
            'vartype':'value variable',
            'form': form.render(),
            'authenticated_user': find_objectmap(context).object_for(request.authenticated_userid).name
            }


            
@view_config(
    name='catvar_post_action',
    context=Config,
    renderer='templates/config_post.pt',
    permission='retail.add_catvar',
    )
def config_view_post_action_catvar(context, request):
    schema = CatVarSchema()
    schema['name'] = colander.SchemaNode(colander.String(), name='Name')
    form = Form(schema,buttons=('submit',))  
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            return {'master': get_renderer('templates/main.pt').implementation(),
                    'vartype':'categorical variable',
                    'form': e.render(),
                    'authenticated_user': find_objectmap(context).object_for(request.authenticated_userid).name
                    }
        registry = request.registry
        name = appstruct.pop('name')
        item = registry.content.create('CatVar', **appstruct)
        context[name] = item
        return HTTPFound(request.resource_url(context))
    return {'master': get_renderer('templates/main.pt').implementation(),
            'vartype':'categorical variable',
            'form': form.render(),
            'authenticated_user': find_objectmap(context).object_for(request.authenticated_userid).name
            }


@view_config(
    name='add_experiment',
    context=Area,
    renderer='templates/config_post.pt',
    permission='retail.add_experiment'
    )
def add_experiment_view(context, request):
    schema = ExperimentSchema()
    schema['name'] = colander.SchemaNode(colander.String(), name='name')
    form = Form(schema,buttons=('submit',))
    if 'submit' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except ValidationFailure as e:
            return {'master': get_renderer('templates/main.pt').implementation(),
                    'vartype':'Experiment',
                    'form': e.render(),
                    'authenticated_user': find_objectmap(context).object_for(request.authenticated_userid).name
                    }
        registry = request.registry
        name = appstruct.pop('name')
        item = registry.content.create('Experiment', **appstruct)
        context[name] = item
        return HTTPFound(request.resource_url(context, name))
    return {'master': get_renderer('templates/main.pt').implementation(),
            'vartype':'Experiment',
            'form': form.render(),
            'authenticated_user': find_objectmap(context).object_for(request.authenticated_userid).name
            }
    
@view_config(
    context=Log,
    renderer='templates/log.pt',
    permission='retail.view_log'
    )
def log_view(context, request):
    system_catalog = find_catalog(request.context, 'system')
    q1 = system_catalog['content_type']
    q2 = system_catalog['path']
    q = q1.eq('LogEntry') & q2.eq(request.resource_path(context))
    resultset = q.execute()
    return {'master': get_renderer('templates/main.pt').implementation(),
            'logs':resultset,
            'authenticated_user': find_objectmap(context).object_for(request.authenticated_userid).name}  
    
    
@view_config(
    context=File         
             )
def images(context,request):
    return context.get_response()  