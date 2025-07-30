# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.conf import settings
from .util import *
import os

API_GENERATOR = {}

try:
    API_GENERATOR = getattr(settings, 'API_GENERATOR') 
except:     
    pass 

# For cross platform imports 
# https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

def generate_serializer_file():

    # serializers should be visible in the local namespace
    from . import serializers

    serializers_structure = pkg_resources.read_text(serializers, 'serializers_structure')
    library_imports       = pkg_resources.read_text(serializers, 'library_imports')
    base_serializer       = pkg_resources.read_text(serializers, 'base_serializer')
    foreign_serializers       = pkg_resources.read_text(serializers, 'foreign_serializers')

    #for val in API_GENERATOR.values():
    for val in valid_models():        
        # extract model from import path
        app_name      = val.split('.')[0]
        model_name    = val.split('.')[-1]
        model_import  = val.replace('.'+model_name, '')
        file_name = os.path.join(app_name, 'serializers.py')
        model_file_name = os.path.join(app_name, 'models.py')
        fields = extract_foreign_fields_and_targets(model_file_name, model_name)

        # Build Imports
        project_imports = 'from ' + model_import + ' import ' + model_name

        foreigns = '    '.join([foreign_serializers.format(model_name=field[0], model_class=field[1]) for field in fields])
        
        serializers = base_serializer.format(model_name=model_name, foreigns=foreigns)


        generation = serializers_structure.format(
            library_imports= file_import_library(file_name, library_imports),
            project_imports=project_imports,
            serializers=serializers,
            previous_classes = file_get_classes(file_name),
        )

        with open(file_name, 'w') as serializers_py:
            serializers_py.write(generation)

    return generation

def generate_admin_file():

    # serializers should be visible in the local namespace
    from . import admin

    admin_structure = pkg_resources.read_text(admin, 'admin_structure')
    library_imports       = pkg_resources.read_text(admin, 'library_imports')
    base_admin       = pkg_resources.read_text(admin, 'base_admin')
    base_imports       = pkg_resources.read_text(admin, 'base_imports')


    #for val in API_GENERATOR.values():
    for val in valid_models():        
        # extract model from import path
        app_name      = val.split('.')[0]
        model_name    = val.split('.')[-1]
        file_name = os.path.join(app_name, 'admin.py')

        # Build Imports
        project_imports = base_imports.format(app_name=app_name, model_name=model_name)
        
        admin = base_admin.format(model_name=model_name)

        generation = admin_structure.format(
            library_imports= file_import_library(file_name, library_imports),
            base_imports=project_imports,
            admin=admin,
            previous_admin = file_get_admins(file_name)
        )

        with open(file_name, 'w') as admin_py:
            admin_py.write(generation)

    return generation

def generate_apps_file():

    # serializers should be visible in the local namespace
    from . import apps

    apps_structure = pkg_resources.read_text(admin, 'apps_structure')


    #for val in API_GENERATOR.values():
    for val in valid_models():        
        # extract model from import path
        app_name      = val.split('.')[0]
        model_name    = val.split('.')[-1]
        file_name = os.path.join(app_name, 'apps.py')

        generation = apps_structure.format(
            model_name= model_name,
            model_name_name = to_filename(model_name)
        )

        with open(file_name, 'w') as admin_py:
            admin_py.write(generation)

    return generation

def generate_views_file():

    # views should be visible in the local namespace
    from . import views

    views_structure = pkg_resources.read_text(views, 'views_structure')  
    library_imports = pkg_resources.read_text(views, 'library_imports')
    base_views      = pkg_resources.read_text(views, 'base_views')

    #for val in API_GENERATOR.values():
    for val in valid_models():
        
        # extract model from import path
        app_name      = val.split('.')[0]
        model_name    = val.split('.')[-1]
        model_import  = val.replace('.'+model_name, '') 
        file_name = os.path.join(app_name, 'views.py')
        model_file_name = os.path.join(app_name, 'models.py')
        base_imports    = "from {}.serializers import {}Serializer".format(app_name, model_name)
        # Build Imports
        project_imports = 'from ' + model_import + ' import ' + model_name
        search_fields = extract_string_fields_from_model(model_file_name, model_name)
        views = base_views.format(
            serializer_name=f'{model_name}Serializer',
            model_name=model_name,
            search_fields=search_fields
        )

        generation = views_structure.format(
            library_imports= file_import_library(file_name, library_imports),
            project_imports=project_imports,
            base_imports=base_imports,
            previous_views=file_get_classes(file_name),
            views=views
        )

        with open(file_name, 'w') as views_py:
            views_py.write(generation)

    return generation

def generate_urls_file():

    # urls should be visible in the local namespace
    from . import urls
    
    urls_file_structure = """{library_imports}\n{project_imports}\n\nurlpatterns = [\n{paths}\n]"""

    library_imports = pkg_resources.read_text(urls, 'library_imports') 
    base_imports    = pkg_resources.read_text(urls, 'base_imports')
    base_urls_path  = pkg_resources.read_text(urls, 'base_urls_path')

    #for val in API_GENERATOR.values():
    for endpoint, val in API_GENERATOR.items():
        # extract model from import path
        app_name      = val.split('.')[0]
        model_name    = val.split('.')[-1]
        file_name = os.path.join(app_name, 'urls.py')
        paths = f'{base_urls_path.format(endpoint=endpoint, model_name=model_name, kebab_name=to_kebab_case(model_name))}'

        generation = urls_file_structure.format(
            library_imports= file_import_library(file_name, library_imports),
            project_imports=base_imports.format(app_name=app_name, model_name=model_name),
            paths=extract_existing_paths(file_name) + paths
        )
        with open(file_name, 'w') as urls_py:
            urls_py.write(generation)

    return generation

