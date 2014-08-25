#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api.camara import CamaraAPI
from core.models import *
import sys
import logging

# Set log level and create a new logger
log_level = logging.INFO

logging.basicConfig(level=log_level)
logging.getLogger('suds.client').setLevel(log_level)
logger = logging.getLogger('import-tool')

# WSDL SOAP URL
# Each endpoint has an url with webservice definitions
api = CamaraAPI("http://www.camara.gov.br/SitCamaraWS/Orgaos.asmx?wsdl")

# TipoOrgao
logger.info("Accessing endpoint \'ListarTiposOrgaos\'...")
result = api.service.ListarTiposOrgaos()
items = result.tipoOrgaos.tipoOrgao
for item in items:
    try:
        exists = TipoOrgao.objects.get(id=int(item._id))
        logger.debug("TipoOrgao.id=%d already exists, skipping... " % (exists.id))
    except TipoOrgao.DoesNotExist:
        new = TipoOrgao()
        new.id = int(item._id)
        new.descricao = " ".join(item._descricao.split())
        new.save()
        logger.info("Created new object (TipoOrgao): %d, %s." % (new.id, new.descricao))


# Orgao
logger.info("Accessing endpoint \'ObterOrgaos\'...")
result = api.service.ObterOrgaos()
items = result.orgaos.orgao
for item in items:
    try:
        exists = Orgao.objects.get(id=int(item._id))
        logger.debug("Orgao.id=%d already exists, skipping..." % (exists.id))
    except Orgao.DoesNotExist:
        new = Orgao()
        new.id = int(item._id)
        new.sigla = "".join(item._sigla.split())
        new.descricao = " ".join(item._descricao.split())
        new.tipo = TipoOrgao.objects.get(id=int(item._idTipodeOrgao))
        new.save()
        logger.info("Created new object (Orgao): %d, %s." % (new.id, new.sigla))

# Cargo
logger.info("Accessing endpoint \'ListarCargosOrgaosLegislativosCD\'...")
result = api.service.ListarCargosOrgaosLegislativosCD()
items = result.cargosOrgaos.cargo
for item in items:
    try:
        exists = Cargo.objects.get(id=int(item._id))
        logger.debug("Cargo.id=%d already exists, skipping..." % (exists.id))
    except Cargo.DoesNotExist:
        new = Cargo()
        new.id = int(item._id)
        new.descricao = " ".join(item._descricao.split())
        new.save()
        logger.info("Created new object (Cargo): %d, %s." % (new.id, new.descricao))

# Internal
titular = Cargo(descricao="Membro Titular")
titular.save()

suplente = Cargo(descricao="Membro Suplente")
suplente.save()
