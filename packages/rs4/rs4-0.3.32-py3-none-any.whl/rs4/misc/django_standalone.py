import os
import sys
import django

def activate (settings = 'backend.orm.settings', project_root = None):
    if project_root:
        sys.path.insert (0, project_root)
    os.environ["DJANGO_SETTINGS_MODULE"] = settings
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    django.setup()
