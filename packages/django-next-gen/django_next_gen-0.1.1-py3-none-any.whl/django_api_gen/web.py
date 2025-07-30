# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.conf import settings
from .util import *
import os
from django.apps import apps
from django.db import models

API_GENERATOR = {}
WEB_PATH = ""

try:
    API_GENERATOR = getattr(settings, 'API_GENERATOR') 
    WEB_PATH = getattr(settings, "WEB_GENERATOR_PATH")
except:     
    pass 

# For cross platform imports 
# https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

def generate_enum():
    #for val in API_GENERATOR.values():
    for val in valid_models():        
        # extract model from import path
        app_name      = val.split('.')[0]
        model_name    = val.split('.')[-1]
        folder_path = os.path.join(WEB_PATH, "modules", to_filename(app_name), to_filename(model_name))
        file_path = os.path.join(folder_path, f"{to_filename(model_name)}.enum.ts")

        os.makedirs(folder_path, exist_ok=True)

        with open(file_path, 'w') as enum_file:
            enum_file.write("")

    return "generation"

def generate_model():
    # Import your base template for the model interface
    from . import web_model

    model_structure = pkg_resources.read_text(web_model, 'model_structure')
    # Example: model_structure might be something like:
    # "export interface {model_name} {{\n{fields}\n}}"

    for val in valid_models():
        app_name = val.split('.')[0]
        model_name = val.split('.')[-1]

        # Get the actual Django model class
        model_class = apps.get_model(app_name, model_name)

        # Build the TypeScript fields string
        ts_fields = []

        for field in model_class._meta.get_fields():
            # Skip reverse relations and auto-created fields
            if field.auto_created and not field.concrete:
                continue

            field_name = field.name
            field_class_name = field.__class__.__name__

            # Map Django field types to TypeScript types (extend as needed)
            DJANGO_TO_TS = {
                'CharField': 'string',
                'TextField': 'string',
                'EmailField': 'string',
                'URLField': 'string',
                'IntegerField': 'number',
                'FloatField': 'number',
                'BooleanField': 'boolean',
                'DateField': 'string | Date',
                'DateTimeField': 'string | Date',
                'ForeignKey': 'string',  # Typically the ID field
                'ManyToManyField': 'string[]',
            }

            ts_type = DJANGO_TO_TS.get(field_class_name, 'any')

            # Normal field
            ts_fields.append(f"    {field_name}: {ts_type};")

            # Add _detail field if ForeignKey
            if field_class_name == 'ForeignKey':
                related_model = field.related_model.__name__
                ts_fields.append(f"    {field_name}_detail: {related_model};")

        fields_str = "\n".join(ts_fields)

        # Format the model interface content
        generation = model_structure.format(
            model_name=model_name,
            fields=fields_str
        )

        # Define path to save model file
        folder_path = os.path.join(WEB_PATH, "modules", to_filename(app_name), to_filename(model_name))
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{to_filename(model_name)}.model.ts")

        with open(file_path, 'w') as model_file:
            model_file.write(generation)

    return generation

def generate_service():
    from . import web_service
    # Load the TypeScript service template
    service_structure = pkg_resources.read_text(web_service, 'service_structure')

    for val in valid_models():
        app_name = val.split('.')[0]
        model_name = val.split('.')[-1]

        model_lower = model_name.lower()
        endpoint = f"{to_kebab_case(model_name)}s"  # Customize if needed

        # Fill in the service structure template
        generation = service_structure.format(
            model_name=model_name,
            model_name_lower=model_lower,
            endpoint=endpoint,
            model_file=f"{to_filename(model_name)}.model",
            app_name=app_name
        )

        # Output path: modules/{app_name}/{model_name}/{model_name}.service.ts
        folder_path = os.path.join(WEB_PATH, "modules",to_filename(app_name), to_filename(model_name))
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, f"{to_filename(model_name)}.service.ts")

        with open(file_path, 'w') as service_file:
            service_file.write(generation)

    return "Service generation complete."

def generate_detail():
    from . import web_detail
    detail_structure = pkg_resources.read_text(web_detail, 'detail_structure')

    for val in valid_models():
        app_name = val.split('.')[0]
        model_name = val.split('.')[-1]
        model_lower = model_name.lower()
        model_class = apps.get_model(app_name, model_name)
        model_var = model_lower

        fields = []
        for field in model_class._meta.get_fields():
            # skip reverse relations and M2M
            if field.auto_created and not field.concrete:
                continue
            if isinstance(field, models.ManyToManyField):
                continue
            fields.append(format_field_ts(field, model_var))

        fields_str = ",\n".join(fields)

        generation = detail_structure.format(
            model_name=model_name,
            model_name_lower=model_lower,
            model_file=to_filename(model_name),
            fields=fields_str,
            app_file_name=to_filename(app_name),
            model_file_name=to_filename(model_name)
        )

        folder_path = os.path.join(WEB_PATH, "modules", to_filename(app_name), to_filename(model_name), "components")
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{to_filename(model_name)}.detail.tsx")

        with open(file_path, 'w') as f:
            f.write(generation)

    return "Detail component generation complete."

def generate_form():
    from . import web_form  # Your React form template as a text file

    # Load the form template with placeholders {model_name}, {model_lower}, {fields}
    form_template = pkg_resources.read_text(web_form, 'form_structure')

    def enum_to_label_value_array_name(field):
        # Assuming enums named like GenderType, UserType, etc. based on field name
        name = field.name.title().replace('_', '')
        return name

    def generate_form_field(field):
        name = field.name
        label = str(field.verbose_name).title() if field.verbose_name else name.title()

        # Validation rules
        rules = []
        if not getattr(field, 'blank', True) and not getattr(field, 'null', True):
            rules.append('{ required: true, message: "%s is required" }' % label)

        rules_str = ", ".join(rules)

        if isinstance(field, models.BooleanField):
            return f'''
            {{!props.{name} && (
      <Form.Item name="{name}" label="{label}" valuePropName="checked" rules={{[{rules_str}]}}>
        <Checkbox />
      </Form.Item>)}}'''

        elif field.choices:
            enum_name = enum_to_label_value_array_name(field)
            return f'''
            {{!props.{name} && (
      <Form.Item name="{name}" label="{label}" rules={{[{rules_str}]}}>
        <Select
          optionFilterProp="label"
          options={{enumToLabelValueArray({enum_name})}}
          placeholder="{label}"
        />
      </Form.Item>)}}'''

        elif isinstance(field, models.TextField):
            return f'''
            {{!props.{name} && (
      <Form.Item name="{name}" label="{label}" rules={{[{rules_str}]}}>
        <Input />
      </Form.Item>)}}'''

        elif 'phone' in name.lower():
            return f'''
            {{!props.{name} && (
      <Form.Item name="{name}" label="{label}" rules={{[{rules_str}]}}>
        <PhoneInput datatype="text" placeholder="{label}" />
      </Form.Item>)}}'''

        elif isinstance(field, (models.DateField, models.DateTimeField)):
            return f'''
            {{!props.{name} && (
      <Form.Item name="{name}" label="{label}" rules={{[{rules_str}]}}>
        <DatePicker style={{{{ width: "100%" }}}} />
      </Form.Item>)}}'''
        
        elif isinstance(field, (models.ForeignKey, models.OneToOneField)):
            return f'''
            {{!props.{name} && (
        <Form.Item name="{name}" label="{label}" rules={{[{rules_str}]}}>
            <{to_camel_case(field.related_model.__name__)}SearchInput detail={{data?.{name}_detail}} />
        </Form.Item>)}}'''

        else:
            # Default to Input
            return f'''
            {{!props.{name} && (
      <Form.Item name="{name}" label="{label}" rules={{[{rules_str}]}}>
        <Input placeholder="{label}" />
      </Form.Item>)}}'''

    for val in valid_models():
        app_label = val.split('.')[0]
        model_name = val.split('.')[-1]
        model_class = apps.get_model(app_label, model_name)

        # Collect fields JSX
        form_fields_jsx = []
        for field in model_class._meta.get_fields():
            # Skip reverse relations and m2m
            if field.auto_created and not field.concrete:
                continue
            if isinstance(field, models.ManyToManyField):
                continue
            form_fields_jsx.append(generate_form_field(field))

        fields_str = '\n'.join(form_fields_jsx)

        # Format full React form component string
        form_code = form_template.format(
            model_name=model_name,
            model_lower=model_name.lower(),
            fields=fields_str,
            app_file_name=to_filename(app_label),
            model_file_name=to_filename(model_name)
        )

        folder_path = os.path.join(WEB_PATH, 'modules', to_filename(app_label), to_filename(model_name), "components")
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f'{to_filename(model_name)}.form.tsx')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(form_code)

    return "Form components generated."

def generate_list():
    from . import web_list
    list_template = pkg_resources.read_text(web_list, 'list_structure')
    def generate_table_field(field):
        name = field.name
        title = name.replace('_', ' ').title()

        sorter = '{ multiple: 1 }'  # you can auto-increment for better sorting logic
        if field.choices:
            enum_name = name.title().replace('_', '')
            return f'''
        {{
        key: "{name}",
        title: "{title}",
        dataIndex: "{name}",
        render: (_, row) => getEnumName({enum_name}, row.{name}),
        sorter: {sorter},
        filters: enumToTextValueArray({enum_name}),
        }},'''

        elif isinstance(field, (models.DateTimeField, models.DateField)):
            return f'''
        {{
        key: "{name}",
        title: "{title}",
        dataIndex: "{name}",
        render: (_, row) => toDateAndTime(row.{name}),
        sorter: {sorter},
        }},'''

        elif isinstance(field, (models.TimeField)):
            return f'''
        {{
        key: "{name}",
        title: "{title}",
        dataIndex: "{name}",
        render: (_, row) => formatTo12Hour(row.{name}),
        sorter: {sorter},
        }},'''

        elif isinstance(field, (models.ForeignKey, models.OneToOneField)):
            return f'''
        {{
        key: "{name}",
        title: "{title}",
        dataIndex: "{name}",
        render: (_, row) => row.{name}_detail.name,
        filterDropdown: ({{setSelectedKeys, confirm }}) => (
          <div style={{{{ padding: 8 }}}}>
            <{to_camel_case(name)}SearchInput
              defaultOpen
              onChange={{(value) => {{
                setSelectedKeys(value ? [value] : []);
                confirm();
              }}}}
              style={{{{ width: 200 }}}}
              allowClear
            />
          </div>
        ),
        sorter: {sorter},
        }},'''

        else:
            return f'''
        {{
        key: "{name}",
        title: "{title}",
        dataIndex: "{name}",
        sorter: {sorter},
        }},'''

    for val in valid_models():
        app_name = val.split('.')[0]
        model_name = val.split('.')[-1]
        model_class = apps.get_model(app_name, model_name)
        # Then format the template
        columns_code = "\n".join(generate_table_field(f) for f in model_class._meta.get_fields() if f.concrete and not f.auto_created)

        list_code = list_template.format(
            model_name=model_name,
            model_lower=model_name.lower(),
            fields=columns_code,
            app_file_name=to_filename(app_name),
            model_file_name=to_filename(model_name)
        )

        folder_path = os.path.join(WEB_PATH, 'modules', to_filename(app_name), to_filename(model_name), "components")
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f'{to_filename(model_name)}.list.tsx')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(list_code)


def generate_search_input():
    from . import web_search
    # Load the TypeScript service template
    search_structure = pkg_resources.read_text(web_search, 'search_structure')

    for val in valid_models():
        app_name = val.split('.')[0]
        model_name = val.split('.')[-1]

        pascal_model = to_pascal_case(model_name)
        camel_model = model_name.lower()

        generation = search_structure.format(
            pascal_model=pascal_model,
            camel_model=camel_model,
            model_file_name=to_filename(model_name)
        )

        folder_path = os.path.join(WEB_PATH, "modules", to_filename(app_name), to_filename(model_name), "components")
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, f"{to_filename(model_name)}.search.tsx")

        with open(file_path, 'w') as search_file:
            search_file.write(generation)

    return "Search generation complete."

def generate_list_page():
    from . import web_list_page
    # Load the TypeScript service template
    list_page_structure = pkg_resources.read_text(web_list_page, 'list_page_structure')

    for val in valid_models():
        app_name = val.split('.')[0]
        model_name = val.split('.')[-1]

        generation = list_page_structure.format(
            app_file_name=to_filename(app_name),
            model_name=to_pascal_case(model_name),
            model_file_name=to_filename(model_name)
        )

        folder_path = os.path.join(WEB_PATH, "app", "admin", to_filename(app_name), to_filename(model_name) + "s")
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, "page.tsx")

        with open(file_path, 'w') as list_page_file:
            list_page_file.write(generation)

    return "Search generation complete."

def generate_detail_page():
    from . import web_detail_page
    # Load the TypeScript service template
    detail_page_structure = pkg_resources.read_text(web_detail_page, 'detail_page_structure')

    for val in valid_models():
        app_name = val.split('.')[0]
        model_name = val.split('.')[-1]

        generation = detail_page_structure.format(
            app_file_name=to_filename(app_name),
            model_name=to_pascal_case(model_name),
            model_file_name=to_filename(model_name)
        )

        folder_path = os.path.join(WEB_PATH, "app", "admin", to_filename(app_name), to_filename(model_name) + "s", f"[{to_filename(model_name)}_id]")
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, "page.tsx")

        with open(file_path, 'w') as list_page_file:
            list_page_file.write(generation)

    return "Search generation complete."

def generate_edit_page():
    from . import web_edit_page
    # Load the TypeScript service template
    list_page_structure = pkg_resources.read_text(web_edit_page, 'edit_page_structure')

    for val in valid_models():
        app_name = val.split('.')[0]
        model_name = val.split('.')[-1]

        generation = list_page_structure.format(
            app_file_name=to_filename(app_name),
            model_name=to_pascal_case(model_name),
            model_file_name=to_filename(model_name)
        )

        folder_path = os.path.join(WEB_PATH, "app", "admin", to_filename(app_name), to_filename(model_name) + "s", f"[{to_filename(model_name)}_id]", "edit")
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, "page.tsx")

        with open(file_path, 'w') as list_page_file:
            list_page_file.write(generation)

    return "Search generation complete."

def generate_create_page():
    from . import web_create_page
    # Load the TypeScript service template
    create_page_structure = pkg_resources.read_text(web_create_page, 'create_page_structure')

    for val in valid_models():
        app_name = val.split('.')[0]
        model_name = val.split('.')[-1]

        generation = create_page_structure.format(
            model_name=to_pascal_case(model_name),
            app_file_name=to_filename(app_name),
            model_file_name=to_filename(model_name)
        )

        folder_path = os.path.join(WEB_PATH, "app", "admin", to_filename(app_name), to_filename(model_name) + "s", "create")
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, "page.tsx")

        with open(file_path, 'w') as list_page_file:
            list_page_file.write(generation)

    return "Search generation complete."

def generate_app_menu():
    from . import web_menu
    # Load the TypeScript service template
    menu_structure = pkg_resources.read_text(web_menu, 'menu_structure')
    apps = {}

    for val in valid_models():
        app_name = val.split('.')[0]
        model_name = val.split('.')[-1]
        apps[app_name] = apps.get(app_name, "")
        apps[app_name] += f'''  {{
            key: "/admin/{to_filename(app_name)}/{to_filename(model_name)}s",
            icon: <UserOutlined />,
            label: <Link href="/admin/{to_filename(app_name)}/{to_filename(model_name)}s">{to_title_case(model_name)}</Link>,
        }},
        '''
    
    for app in apps:
        generation = menu_structure.format(
            app_name_pascal=to_pascal_case(app),
            app_file_name=to_filename(app),
            app_name_tilte=to_title_case(app),
            children=apps[app]
        )

        folder_path = os.path.join(WEB_PATH, "app", "admin", to_filename(app))
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, f"{to_filename(app)}.menu.tsx")

        with open(file_path, 'w') as menu_file:
            menu_file.write(generation)

    return "Menu generation complete."