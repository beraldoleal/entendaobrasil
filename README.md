README
======


For now is a sqlite simple, just run:


     $ export PYTHONPATH=dir:$PYTHONPATH
     $ export DJANGO_SETTINGS_MODULE=entendaobrasil.settings
     $ python manage.py syncdb
     $ python scripts/import.py
     $ python utils/deputados_fotos.py


Run:

    python manage.py runserver