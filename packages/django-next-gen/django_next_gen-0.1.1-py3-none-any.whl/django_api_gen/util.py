# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os, importlib, shutil
from django.conf import settings
from django.db import models
from django.apps import apps

import re

pattern = r'^\s*(import\s+[a-zA-Z0-9_., ]+|from\s+[a-zA-Z0-9_.]+\s+import\s+[\*\w., ]+)'

def valid_models():

    retVal = []

    API_GENERATOR = getattr(settings, 'API_GENERATOR')

    for val in API_GENERATOR.values():

        app_name      = val.split('.')[0]
        model_name    = val.split('.')[-1]
        model_import  = val.replace('.'+model_name, '')             

        models = importlib.import_module( model_import )

        try:
            model = getattr(models, model_name)
        except:
            #print(f' > Warn: [' + model_name + '] model NOT_FOUND for [' + app_name + '] APP' )
            #print(f'   Hint: Add [' + model_name + '] model definition in [' + app_name + ']')
            continue 

        try:
            model.objects.last()
        except:
            #print(f' > Warn: [' + model_name + '] model not migrated in DB.' )
            #print(f'   Hint: run makemigrations, migrate commands')
            continue

        #print ( ' Valid API_GEN Model -> ' + val )
        retVal.append( val )

    return retVal

import ast

def extract_top_level_classes(code):
    tree = ast.parse(code)
    classes = []

    # Only look at nodes directly in the module body (top-level)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_code = ast.get_source_segment(code, node)
            if class_code:
                classes.append(class_code)

    return classes

def file_import_library(file_name, content):
    if(os.path.exists(file_name)):
        with open(file_name, 'r') as f:
            file_content = f.read()
            imp = ''
            matches = re.findall(r'^\s*(import\s+[a-zA-Z0-9_., ]+|from\s+[a-zA-Z0-9_.]+\s+import\s+[\*\w., ]+)', file_content, re.MULTILINE)
            imp += '\n'.join(matches)
            if content in file_content:
                return imp
            return content + imp
    return content

def file_get_classes(file_name):
    cls = ''
    if(os.path.exists(file_name)):
        with open(file_name, 'r') as f:
            file_content = f.read()
            extracted_classes = extract_top_level_classes(file_content)
            if(extracted_classes):
                cls = '\n\n'.join(extracted_classes)
    return cls

def extract_admin_register_calls(content):
    """
    Extract full admin.site.register(...) calls from file content.
    """
    pattern = re.compile(r"admin\.site\.register\s*\((.*?)\)", re.DOTALL)
    return [f"admin.site.register({match.strip()})" for match in pattern.findall(content)]

def file_get_admins(file_name):
    cls = ''
    if(os.path.exists(file_name)):
        with open(file_name, 'r') as f:
            file_content = f.read()
            extracted_admins = extract_admin_register_calls(file_content)
            if(extracted_admins):
                cls = '\n'.join(extracted_admins)
    return cls

def extract_string_fields_from_model(model_file_path, model_name):
    with open(model_file_path, 'r') as file:
        node = ast.parse(file.read())

    string_fields = []

    for class_node in [n for n in node.body if isinstance(n, ast.ClassDef)]:
        if class_node.name == model_name:
            for stmt in class_node.body:
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                    try:
                        field_type = stmt.value.func.attr
                        if field_type in ('CharField', 'TextField'):
                            field_name = stmt.targets[0].id
                            string_fields.append(field_name)
                    except AttributeError:
                        continue
    return string_fields

def extract_foreign_fields_and_targets(model_file_path, model_name):
    with open(model_file_path, 'r') as file:
        node = ast.parse(file.read())

    foreign_fields = []

    for class_node in [n for n in node.body if isinstance(n, ast.ClassDef)]:
        if class_node.name == model_name:
            for stmt in class_node.body:
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                    try:
                        call = stmt.value
                        func = call.func

                        # Must be models.ForeignKey or models.OneToOneField
                        if isinstance(func, ast.Attribute) and func.attr in ('ForeignKey', 'OneToOneField'):
                            field_name = stmt.targets[0].id

                            # Handle first positional arg
                            if call.args:
                                target_arg = call.args[0]
                            else:
                                # Fallback: look for keyword "to"
                                target_arg = next((kw.value for kw in call.keywords if kw.arg == 'to'), None)

                            if isinstance(target_arg, ast.Str):
                                target_model = target_arg.s
                            elif isinstance(target_arg, ast.Name):
                                target_model = target_arg.id
                            elif isinstance(target_arg, ast.Attribute):
                                target_model = f"{target_arg.value.id}.{target_arg.attr}"
                            else:
                                target_model = "Unknown"

                            foreign_fields.append((field_name, target_model))
                    except Exception:
                        continue

    return foreign_fields
def extract_all_fields_from_model(model_file_path, model_name):
    with open(model_file_path, 'r') as file:
        node = ast.parse(file.read())

    all_fields = []

    for class_node in [n for n in node.body if isinstance(n, ast.ClassDef)]:
        if class_node.name == model_name:
            for stmt in class_node.body:
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                    try:
                        field_name = stmt.targets[0].id
                        all_fields.append(field_name)
                    except AttributeError:
                        continue
    return all_fields

def to_kebab_case(s):
    # Replace underscores with spaces
    return to_filename(s).replace("_", "-")

def extract_existing_paths(file_name):
    """
    Extract all lines inside urlpatterns = [ ... ]
    """
    pattern = re.compile(r"urlpatterns\s*=\s*\[\s*(.*?)\s*\]", re.DOTALL)
    s = set()
    if(os.path.exists(file_name)):
        with open(file_name, 'r') as f:
            file_content = f.read()
            match = pattern.search(file_content)
            if match:
                path_block = match.group(1)
                # Split individual lines and strip
                s = set("\t" +line.strip() for line in path_block.splitlines())
    if(s):
        return '\n'.join(s) + "\n"
    return ''

def format_field_ts(field, model_var_name):
    field_name = field.name
    label = str(field.verbose_name).title() if field.verbose_name else field.name.title()
    key = field_name

    if isinstance(field, (models.BooleanField,)):
        return f'''
    {{
      key: "{key}",
      label: "{label}",
      children: {model_var_name}?.{field_name} ? (
        <FaCheck color="green" />
      ) : (
        <FaTimes color="red" />
      ),
    }}'''
    
    elif isinstance(field, (models.DateField, models.DateTimeField)):
        return f'''
    {{
      key: "{key}",
      label: "{label}",
      children: toDateAndTime({model_var_name}?.{field_name}),
    }}'''
    
    elif field.choices:
        enum_name = field.name.title().replace('_', '')
        return f'''
    {{
      key: "{key}",
      label: "{label}",
      children: getEnumName({enum_name}, {model_var_name}?.{field_name}),
    }}'''
    
    elif isinstance(field, models.ForeignKey):
        return f'''
    {{
      key: "{key}",
      label: "{label}",
      children: {model_var_name}?.{field_name}_detail?.name || {model_var_name}?.{field_name},
    }}'''
    
    else:
        return f'''
    {{
      key: "{key}",
      label: "{label}",
      children: {model_var_name}?.{field_name},
    }}'''

def to_camel_case(s):
    # Replace non-alphanumeric characters with space
    s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
    # Split on spaces or existing uppercase word boundaries
    words = re.split(r'\s+|(?<=[a-z])(?=[A-Z])', s)
    # Capitalize and join
    return ''.join(word.capitalize() for word in words if word)

def to_pascal_case(s: str) -> str:
    if "_" in s:
        # snake_case → PascalCase
        return ''.join(word.capitalize() for word in s.split('_'))
    else:
        # camelCase or already PascalCase → PascalCase
        return ''.join(word.capitalize() for word in re.findall(r'[A-Z]?[a-z0-9]+', s))
    
import re

def to_filename(string):
    """
    Converts a camelCase or PascalCase string to lowercase, separates words with underscores,
    removes non-alphanumeric characters (except spaces), and replaces spaces with underscores.
    
    Args:
        string (str): The input string.

    Returns:
        str: The cleaned, underscore-formatted string.
    """
    # Add underscores between camelCase or PascalCase transitions
    string = string.replace('-', ' ')
    string = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', string)
    string = re.sub(r'[^\w\s]', '', string)        # Remove punctuation
    string = re.sub(r'\s+', '_', string.strip())  # Replace spaces with underscores
    return string.lower()


def to_title_case(string):
    """
    Converts a string to title case.

    Args:
        string (str): The input string.

    Returns:
        str: The title-cased string.
    """
    return string.strip().title()