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

def get_orgaos():
    print("DEBUG: Obtendo lista de orgaos...")

    list_url = "http://www.camara.gov.br/SitCamaraWS/Orgaos.asmx/ObterOrgaos"
    doc = minidom.parse(urllib.urlopen(list_url))
    return doc.getElementsByTagName("orgao")


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
    

for orgao in get_orgaos():
    id = orgao.getAttribute('id')
    tipo_orgao = orgao.getAttribute('idTipodeOrgao')
    sigla = orgao.getAttribute('sigla')
    descricao = orgao.getAttribute('descricao')

    exists = Orgao.objects.filter(id=id).first()

    if exists:
        continue

    o = Orgao()

    tipo = TipoOrgao.objects.get(pk=tipo_orgao)

    set_atributo(o, 'id', id)
    set_atributo(o, 'tipo', tipo)
    set_atributo(o, 'sigla', sigla)
    set_atributo(o, 'descricao', descricao)
    o.save()
