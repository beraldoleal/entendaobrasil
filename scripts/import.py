#!/usr/bin/env python

from api.camara.orgaos import *
from api.camara.deputados import *

# Orgaos Webservice
orgaos = OrgaosCamara()

orgaos.importar_tipos_orgaos()
orgaos.importar_orgaos()
orgaos.importar_cargos()

# Deputados Webservice
deputados = DeputadosCamara()

deputados.importar_partidos()
deputados.importar_deputados()
deputados.importar_detalhes_deputados()
