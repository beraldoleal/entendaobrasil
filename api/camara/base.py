#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Beraldo Leal <beraldo@ime.usp.br>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License version
# 2 as published by the Free Software Foundation.
#
# vim: tabstop=4:softtabstop=4:shiftwidth=4:expandtab

from suds.client import Client
from entendaobrasil import settings
from datetime import datetime
import urllib2
import logging

logging.basicConfig(level=settings.CAMARA_API_LOG_LEVEL)
logger = logging.getLogger('entendaobrasil.api.camara')

class CamaraAPI(object):
    def __init__(self):
        # Baixa wsdl e instancia cliente
        try:
            logger.info(u"Baixando wsdl a partir de %s ..." % self.wsdl_url)
            self.client = Client(self.wsdl_url)
            self.service = self.client.service
        except urllib2.URLError:
            logger.error(u"Erro ao baixar wsdl. Abortando....")


    def executar_metodo(self, metodo, *args, **kwargs):
        logger.info(u"Acessando metodo %s ..." % metodo)
        return getattr(self.service, metodo)(*args, **kwargs)


    def as_list(self, element):
        if type(element) == list:
            return element
        else:
            return [element]

    def as_text(self, valor):
        return " ".join(valor.split())

    def as_text_without_spaces(self, valor):
        return "".join(valor.split())


    def as_date(self, date, date_format="%d/%m/%Y"):
        try:
            return datetime.strptime(date, date_format)
        except ValueError:
            logger.debug(u"Data em formato inválido.")
            return None 
