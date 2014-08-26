"""
WSGI config for entendaobrasil project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys

path = '/var/www/entendaobrasil'
sys.path.insert(0, path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "entendaobrasil.production")
os.environ.setdefault("PYTHON_EGG_CACHE", "/tmp/")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
