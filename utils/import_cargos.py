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

def get_cargos():
    print("DEBUG: Obtendo lista de cargos...")

    list_url = "http://www.camara.gov.br/SitCamaraWS/Orgaos.asmx/ListarCargosOrgaosLegislativosCD"
    doc = minidom.parse(urllib.urlopen(list_url))
    return doc.getElementsByTagName("cargo")


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
    

for cargo in get_cargos():
    id = cargo.getAttribute('id')
    descricao = cargo.getAttribute('descricao')

    exists = Cargo.objects.filter(id=id).first()

    if exists:
        continue

    c = Cargo()

    set_atributo(c, 'id', id)
    set_atributo(c, 'descricao', descricao)
    c.save()
