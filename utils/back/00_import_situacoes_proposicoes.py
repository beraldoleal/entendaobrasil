#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.models import *
from xml.dom import minidom
from datetime import datetime
import sys
import os
import urllib
import requests

DATE_FORMAT = "%d/%m/%Y"

def get_tipos_proposicoes():
    print("DEBUG: Obtendo lista de situacoes de proposicoes...")

    list_url = "http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ListarSituacoesProposicao"
    doc = minidom.parse(urllib.urlopen(list_url))
    s = doc.getElementsByTagName("situacaoProposicao")[0]
    return s.getElementsByTagName("situacaoProposicao")


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
    else:
        setattr(objeto, campo, valor)
    

for situacao in get_tipos_proposicoes():
    id = situacao.getAttribute('id')
    descricao = situacao.getAttribute('descricao')
    ativa = situacao.getAttribute('ativa')

    print id, descricao, ativa
    exists = SituacaoProposicao.objects.filter(id=id).first()

    if exists:
        continue

    s = SituacaoProposicao()

    set_atributo(s, 'id', id)
    set_atributo(s, 'descricao', descricao)
    set_atributo(s, 'ativa', ativa)
    s.save()
