# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from . import manager
from . import web

def generate_api():
    manager.generate_serializer_file()
    manager.generate_views_file()
    manager.generate_urls_file()
    manager.generate_admin_file()

def generate_web():
    web.generate_enum()
    web.generate_model()
    web.generate_service()
    web.generate_detail()
    web.generate_form()
    web.generate_list()
    web.generate_search_input()
    web.generate_create_page()
    web.generate_edit_page()
    web.generate_detail_page()
    web.generate_list_page()
    web.generate_app_menu()