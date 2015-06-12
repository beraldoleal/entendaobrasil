#!/usr/bin/env python

from api.camara.orgaos import *
from api.camara.deputados import *
from core.models import *
import django

django.setup()
## Orgaos Webservice
orgaos = OrgaosCamara()

orgaos.importar_tipos_orgaos()
orgaos.importar_orgaos()
orgaos.importar_cargos()

## Deputados Webservice
deputados = DeputadosCamara()

deputados.importar_partidos()
deputados.importar_deputados()
#deputados.importar_detalhes_deputados()

# Google Images download
#for parlamentar in Parlamentar.objects.all():
#    parlamentar.download_photos()

# Wikipedia data
#for parlamentar in Parlamentar.objects.all():
#    parlamentar.get_wikipedia_data()
