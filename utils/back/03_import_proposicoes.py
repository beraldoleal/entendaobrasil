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
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"

def get_proposicoes(sigla, ano):
    print("DEBUG: Obtendo lista de proposicoes (%s) para o ano %s..." % (sigla, ano))

    list_url = "http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ListarProposicoes?sigla=%s&numero=&ano=%s&datApresentacaoIni=&datApresentacaoFim=&parteNomeAutor=&idTipoAutor=&siglaPartidoAutor=&siglaUFAutor=&generoAutor=&codEstado=&codOrgaoEstado=&emTramitacao=" % (sigla, ano)

    doc = minidom.parse(urllib.urlopen(list_url))

    #doc = minidom.parse("raw/deputados.xml")
    return doc.getElementsByTagName("proposicao")

def get_field_type(model, field):
    return model._meta.get_field(field).get_internal_type()


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
    elif tipo == 'DateTimeField':
        try:
            date = datetime.strptime(valor, DATETIME_FORMAT)
            setattr(objeto, campo, date)
        except ValueError:
            print("ERROR: Datetime with invalid format")
    else:
        setattr(objeto, campo, valor)
    

for p in get_proposicoes("PL", 2012):

    id = p.getElementsByTagName("id")[0].firstChild.nodeValue
    nome = p.getElementsByTagName("nome")[0].firstChild.nodeValue
    tipo = p.getElementsByTagName("tipoProposicao")[0]
    tipo_id = tipo.getElementsByTagName("id")[0].firstChild.nodeValue
    numero = p.getElementsByTagName("numero")[0].firstChild.nodeValue
    ano = p.getElementsByTagName("ano")[0].firstChild.nodeValue
    data_apresentacao = p.getElementsByTagName("datApresentacao")[0].firstChild.nodeValue
    ementa = p.getElementsByTagName("txtEmenta")[0].firstChild.nodeValue
    explicacao = p.getElementsByTagName("txtExplicacaoEmenta")[0].firstChild.nodeValue
    autor = p.getElementsByTagName("autor1")[0]
    autor_ide_cadastro = autor.getElementsByTagName("idecadastro")[0].firstChild.nodeValue
    quantidade_autores = p.getElementsByTagName("qtdAutores")[0].firstChild.nodeValue
    situacao = p.getElementsByTagName("situacao")[0]
    situacao_id = situacao.getElementsByTagName("id")[0].firstChild.nodeValue
    genero = p.getElementsByTagName("indGenero")[0].firstChild.nodeValue

    exists = Proposicao.objects.filter(id=id).first()

    if exists:
        continue

    try:
        tipo = TipoProposicao.objects.filter(id=int(tipo_id)).first()
        autor = Parlamentar.objects.filter(ide_cadastro=int(autor_ide_cadastro)).first()
        situacao = SituacaoProposicao.objects.filter(id=int(situacao_id)).first()
    except ValueError:
        print("ERROR: Failed to get autor or tipo")
        continue

    if tipo and autor:
        proposicao = Proposicao()
        set_atributo(proposicao, "id", id)
        set_atributo(proposicao, "nome", nome)
        set_atributo(proposicao, "tipo", tipo)
        set_atributo(proposicao, "numero", numero)
        set_atributo(proposicao, "ano", ano)
        set_atributo(proposicao, "data_apresentacao", data_apresentacao)
        set_atributo(proposicao, "ementa", ementa)
        set_atributo(proposicao, "explicacao", explicacao)
        set_atributo(proposicao, "autor", autor)
        set_atributo(proposicao, "quantidade_autores", quantidade_autores)
        set_atributo(proposicao, "situacao", situacao)
        set_atributo(proposicao, "genero", genero)
        proposicao.save()
