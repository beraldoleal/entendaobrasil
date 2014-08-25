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
    print("DEBUG: Obtendo lista de tipos de proposicoes...")

    list_url = "http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ListarSiglasTipoProposicao"
    doc = minidom.parse(urllib.urlopen(list_url))
    return doc.getElementsByTagName("sigla")


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
    

for tipo in get_tipos_proposicoes():
    sigla = tipo.getAttribute('tipoSigla')
    descricao = tipo.getAttribute('descricao')
    ativa = tipo.getAttribute('ativa')
    genero = tipo.getAttribute('genero')

    exists = TipoProposicao.objects.filter(sigla=sigla).first()

    if exists:
        continue

    t = TipoProposicao()

    set_atributo(t, 'sigla', sigla)
    set_atributo(t, 'descricao', descricao)
    set_atributo(t, 'ativa', ativa)
    set_atributo(t, 'genero', genero)
    t.save()
