#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.models import *
from xml.dom import minidom
from datetime import datetime
import sys
import os
import urllib
import wikipedia
import requests

DATE_FORMAT = "%d/%m/%Y"

def get_deputados():
    print("DEBUG: Obtendo lista de deputados...")

    list_url = "http://www.camara.gov.br/SitCamaraWS/Deputados.asmx/ObterDeputados"
    #doc = minidom.parse(urllib.urlopen(list_url))

    doc = minidom.parse("raw/deputados.xml")
    return doc.getElementsByTagName("deputado")


def get_deputado(ide_cadastro):
    print("DEBUG: Obtendo deputado %s..." % ide_cadastro)

    detail_url = "http://www.camara.gov.br/SitCamaraWS/Deputados.asmx/ObterDetalhesDeputado?ideCadastro=%s&numLegislatura=" % ide_cadastro
    doc = minidom.parse(urllib.urlopen(detail_url))
    deputados = doc.getElementsByTagName("Deputado")
    return deputados[len(deputados)-1]


def get_field_type(model, field):
    return model._meta.get_field(field).get_internal_type()


fields_mapping = {'ideCadastro':'ide_cadastro',
                  'nomeCivil':'nome',
                  'nomeParlamentarAtual':'nome_parlamentar',
                  'sexo':'sexo',
                  'ufRepresentacaoAtual':'uf',
                  'dataNascimento': 'data_nascimento',
                  'nomeProfissao': 'profissao',
                  'email':'email'}


def set_atributo(objeto, campo, valor):
    print("DEBUG: %s = %s" % (campo, valor))

    tipo = get_field_type(objeto.__class__, campo)
    if tipo == 'IntegerField':
        setattr(objeto, campo, int(valor))
    elif tipo == 'DateField':
        try:
            date = datetime.strptime(valor, DATE_FORMAT)
            setattr(objeto, campo, date)
        except ValueError:
            print("ERROR: Date with invalid format")
    else:
        setattr(objeto, campo, valor)
    

for deputado in get_deputados():
    ide_cadastro = deputado.getElementsByTagName('ideCadastro')[0].firstChild.nodeValue
    url_foto = deputado.getElementsByTagName('urlFoto')[0].firstChild.nodeValue

    exists = Parlamentar.objects.filter(ide_cadastro=ide_cadastro).first()

    if exists:
        continue

    details = get_deputado(ide_cadastro)

    # Novo parlamentar. Save to get id
    p = Parlamentar(tipo = 'D')

    for old, new in fields_mapping.iteritems():
        try:
            value = details.getElementsByTagName(old)[0].firstChild.nodeValue
        except IndexError:
            print("ERROR: %s not found for %s" % (old, ide_cadastro))
            continue


        set_atributo(p, new, value)


    # Partido
    partido = details.getElementsByTagName('partidoAtual')[0]
    sigla = partido.getElementsByTagName('sigla')[0].firstChild.nodeValue

    partido = Partido.objects.filter(sigla=sigla).first()
    if partido:
        set_atributo(p, 'partido', partido)


    # Endereco e Telfone
    gabinete = details.getElementsByTagName('gabinete')[0]
    numero = gabinete.getElementsByTagName('numero')[0].firstChild.nodeValue
    anexo = gabinete.getElementsByTagName('anexo')[0].firstChild.nodeValue
    telefone = gabinete.getElementsByTagName('telefone')[0].firstChild.nodeValue

    set_atributo(p, "endereco", "Câmara dos Deputados, Edifício Principal, Praça dos Três Poderes, Gabinete %s. Anexo %s. CEP: 70.160-900 - Brasília/DF".decode("utf-8") % (numero,anexo))
    set_atributo(p, "telefone", "(61) %s" % telefone)

    p.save()

    # Exercicios

    exercicios = details.getElementsByTagName('periodoExercicio')
    for exercicio in exercicios:
        e = Exercicio()
        set_atributo(e, "situacao", exercicio.getElementsByTagName('situacaoExercicio')[0].firstChild.nodeValue)
        set_atributo(e, "data_inicio", exercicio.getElementsByTagName('dataInicio')[0].firstChild.nodeValue)
        set_atributo(e, "data_fim", exercicio.getElementsByTagName('dataFim')[0].firstChild.nodeValue)
        set_atributo(e, "causa_fim", exercicio.getElementsByTagName('descricaoCausaFimExercicio')[0].firstChild.nodeValue)
        e.parlamentar = p
        e.save()

        print("INFO: Adicionando exercicio %s %s %s %s" % (e.situacao, e.data_inicio, e.data_fim, e.causa_fim))


    # Cargos em orgãos
    #cargos = details.getElementsByTagName('cargoComissoes')
    #for cargo in cargos:
    #    id_orgao = cargo.getElementsByTagName('idOrgaoLegislativoCD')[0].firstChild.nodeValue
    #    id_cargo = cargo.getElementsByTagName('idCargo')[0].firstChild.nodeValue
    #    data_entrada = cargo.getElementsByTagName('dataEntrada')[0].firstChild.nodeValue
    #    data_saida = cargo.getElementsByTagName('dataSaida')[0].firstChild.nodeValue

    #    print("DEBUG: Looking for orgao %s" % id_orgao)
    #    orgao = Orgao.objects.get(id=id_orgao)
    #    print("DEBUG: Looking for cargo %s" % id_cargo)
    #    cargo = Cargo.objects.get(id=id_cargo)

    #    c = CargoOrgao()
    #    set_atributo(c, "orgao", orgao)
    #    set_atributo(c, "cargo", cargo)
    #    set_atributo(c, "data_entrada", data_entrada)
    #    set_atributo(c, "data_saida", data_saida)
    #    c.save()

    # Comissoes / Cargos / Lider ?

    wikipedia_query = "%s %s" % (p.tratamento(), p.nome_parlamentar)
    print("INFO: Searching wikipedia for %s..." % wikipedia_query)
    try:
        wikipedia.set_lang("pt")
        w = wikipedia.page(wikipedia_query)
        p.wikipedia = w.url
        p.sumario = w.summary
    except wikipedia.exceptions.PageError:
        print("ERROR: %s not found on wikipedia" % p.nome_parlamentar)
        pass
    except wikipedia.exceptions.DisambiguationError:
        print("ERROR: %s ambiguo" % p.nome_parlamentar)
        pass
    except requests.exceptions.ConnectionError:
        print("ERROR: Failed to connect to wikiepedia")
        pass


    destination = "core/static/photos/deputados/%s.jpg" % p.ide_cadastro
    if not os.path.isfile(destination):
        urllib.urlretrieve(url_foto, destination)

    p.save()
