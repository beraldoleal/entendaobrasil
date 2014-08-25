#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api.camara import CamaraAPI
from core.models import *
import sys
import suds
import logging

# Set log level and create a new logger
log_level = logging.INFO

logging.basicConfig(level=log_level)
logging.getLogger('suds.client').setLevel(log_level)
logger = logging.getLogger('import-tool')

def as_list(element):
    print type(element)
    if type(element) == list:
        return element
    else:
        return [element]
    
# WSDL SOAP URL
# Each endpoint has an url with webservice definitions
api = CamaraAPI("http://www.camara.gov.br/SitCamaraWS/Deputados.asmx?wsdl")

# Partido
logger.info("Accessing endpoint \'ObterPartidosCD\'...")
result = api.service.ObterPartidosCD()
items = result.partidos.partido
for item in items:
    try:
        exists = Partido.objects.get(sigla=item.siglaPartido)
        logger.debug("Partido.sigla=%s already exists, skipping... " % (exists.sigla))
    except Partido.DoesNotExist:
        new = Partido()
        new.sigla = " ".join(item.siglaPartido.split())
        new.nome = " ".join(item.nomePartido.split())
        try:
            new.data_criacao = datetime.strptime(item.dataCriacao, "%d/%m/%Y")
            new.data_extincao = datetime.strptime(item.dataExtincao, "%d/%m/%Y")
        except ValueError:
            logger.error("Date in invalid format")
        new.save()
        logger.info("Created new object (Partido): %d, %s." % (new.id, new.sigla))

# Deputado
logger.info("Accessing endpoint \'ObterDeputados\'...")
result = api.service.ObterDeputados()
items = result.deputados.deputado
for item in items:
    try:
        exists = Parlamentar.objects.get(ide_cadastro=int(item.ideCadastro))
        logger.debug("Deputado.ide_cadastro=%d already exists, skipping... " % (exists.ide_cadastro))
    except Parlamentar.DoesNotExist:
        new = Parlamentar()
        new.tipo = 'D'
        new.ide_cadastro = int(item.ideCadastro)
        new.nome = " ".join(item.nome.split()).title()
        new.nome_parlamentar = " ".join(item.nomeParlamentar.split()).title()
        new.email = " ".join(item.email.split())
        new.url_foto = " ".join(item.urlFoto.split())
        new.sexo = item.sexo[0].upper()
        new.partido = Partido.objects.get(sigla=item.partido)
        new.uf = item.uf
        new.telefone = "(61) %s" % item.fone
        new.endereco = u"Câmara dos Deputados, Edifício Principal, Praça dos Três Poderes, Gabinete %s. Anexo %s. CEP: 70.160-900 - Brasília/DF" % (item.gabinete, item.anexo)
        new.save()
        logger.info("Created new object (Deputado): %d, %s." % (new.ide_cadastro, new.nome_parlamentar))

# Deputado details
logger.info("Accessing endpoint \'ObterDetalhesDeputado\'...")
for p in Parlamentar.objects.all():
    logger.info("Getting details for %d %s" % (p.ide_cadastro, p.nome_parlamentar))

    try:
        result = api.service.ObterDetalhesDeputado(ideCadastro=p.ide_cadastro, numLegislatura=53)
    except suds.WebFault:
        logger.debug("Deputado %s with no results in current legislatura" % p.ide_cadastro)
        continue

    item = result.Deputados.Deputado
    p.profissao = " ".join(item.nomeProfissao.split())
    try:
        p.data_nascimento = datetime.strptime(item.dataNascimento, "%d/%m/%Y")
    except ValueError:
        logger.error("Failed to set \'data_nascimento\'. Invalid format.")

    p.uf = " ".join(item.ufRepresentacaoAtual.split())

    logger.info("Updated %s", p.nome_parlamentar)
    p.save()


    # CargosComissoes
    cargos = item.cargosComissoes

    if len(cargos) == 0:
        continue

    for cargo in as_list(cargos.cargoComissoes):
        orgao_id = int(cargo.idOrgaoLegislativoCD)
        orgao_sigla = cargo.siglaComissao
        orgao_nome = u'%s' % cargo.nomeComissao
        logger.debug("Searching for orgao %d %s (%s)" % (orgao_id, orgao_sigla, orgao_nome))
        try:
            orgao_base = Orgao.objects.get(id=orgao_id)
        except Orgao.DoesNotExist:
            tipo = TipoOrgao.objects.get(id=110) # Comissao da Camara dos Deputados
            orgao_base = Orgao(id=orgao_id, sigla=orgao_sigla, descricao=orgao_nome, tipo=tipo)
            orgao_base.save()
        cargo_base = Cargo.objects.get(id=cargo.idCargo)
        cargo_orgao = CargoOrgao()
        cargo_orgao.orgao = orgao_base
        cargo_orgao.cargo = cargo_base
        cargo_orgao.parlamentar = p
        try:
            cargo_orgao.data_entrada = datetime.strptime(cargo.dataEntrada, "%d/%m/%Y")
            cargo_orgao.data_saida = datetime.strptime(cargo.dataSaida, "%d/%m/%Y")
        except ValueError:
            logger.error("Invalid date, skipping date field")
        cargo_orgao.save()
        logger.debug("Created new object (CargoOrgao): Orgao: %s, Cargo: %s, Parlamentar: %s (%s - %s)" % 
                    (cargo_orgao.orgao.sigla, cargo_orgao.cargo.descricao,
                     cargo_orgao.parlamentar.nome_parlamentar, cargo_orgao.data_entrada, cargo_orgao.data_saida))
        
       
    # Comissoes
    comissoes = item.comissoes

    if len(comissoes) == 0:
        continue

    for comissao in as_list(comissoes.comissao):
        orgao_id = int(comissao.idOrgaoLegislativoCD)
        orgao_sigla = comissao.siglaComissao
        orgao_nome = u'%s' % comissao.nomeComissao
        logger.debug("Searching for orgao %d %s (%s)" % (orgao_id, orgao_sigla, orgao_nome))
        try:
            orgao_base = Orgao.objects.get(id=orgao_id)
        except Orgao.DoesNotExist:
            tipo = TipoOrgao.objects.get(id=110) # Comissao da Camara dos Deputados
            orgao_base = Orgao(id=orgao_id, sigla=orgao_sigla, descricao=orgao_nome, tipo=tipo)
            orgao_base.save()

        cargo_id = 63 if comissao.condicaoMembro == "Titular" else 64
        cargo_base = Cargo.objects.get(id=cargo_id)
        cargo_orgao = CargoOrgao()
        cargo_orgao.orgao = orgao_base
        cargo_orgao.cargo = cargo_base
        cargo_orgao.parlamentar = p
        try:
            cargo_orgao.data_entrada = datetime.strptime(comissao.dataEntrada, "%d/%m/%Y")
            cargo_orgao.data_saida = datetime.strptime(comissao.dataSaida, "%d/%m/%Y")
        except ValueError:
            logger.error("Invalid date, skipping date field")

        cargo_orgao.save()
        logger.debug("Created new object (CargoOrgao): Orgao: %s, Cargo: %s, Parlamentar: %s (%s - %s)" % 
                    (cargo_orgao.orgao.sigla, cargo_orgao.cargo.descricao,
                     cargo_orgao.parlamentar.nome_parlamentar, cargo_orgao.data_entrada, cargo_orgao.data_saida))
 
