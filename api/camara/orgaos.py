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

from entendaobrasil import settings
from api.camara.base import CamaraAPI
from core.models import *
import logging

logging.basicConfig(level=settings.CAMARA_API_LOG_LEVEL)
logger = logging.getLogger('entendaobrasil.api.camara')

class OrgaosCamara(CamaraAPI):
    def __init__(self):
        self.wsdl_url = "http://www.camara.gov.br/SitCamaraWS/Orgaos.asmx?wsdl"
        return super(OrgaosCamara, self).__init__()


    def importar_tipos_orgaos(self):
        """
        Obtém os tipos de órgãos e importa localmente.

        Este método acessa a API da Câmara dos Deputados e salva na base de
        dados local, apenas se o tipo de órgão não existir ou possuir o campo
        'atualizado' igual a False.

        Caso você queira força a atualização de um objeto existente na execução
        deste método, torne o campo 'atualizado' = False.

        Exemplos: Comissão Especial, Comissão Permanente, etc.
        """
        result = self.executar_metodo("ListarTiposOrgaos")

        for item in self.as_list(result.tipoOrgaos.tipoOrgao):

            # Consulta se o objeto já existe e a flag "atualizado" está ativa
            existe = TipoOrgao.objects.filter(id=int(item._id)).first()
            if existe and existe.atualizado:
                logger.info(u"%s já está atualizado. %s ignorado." %
                            (existe._meta.object_name, existe))
                continue

            # Cria o novo objeto
            novo = TipoOrgao(id = int(item._id),
                             descricao = self.as_text(item._descricao))
            novo.save()
            logger.info(u"%s importado com sucesso (%s)." % 
                        (novo._meta.object_name, novo))


    def importar_orgaos(self):
        """
        Obtém os órgãos e importa localmente.

        Este método acessa a API da Câmara dos Deputados e salva na base de
        dados local, apenas se o órgão não existir ou possuir o campo
        'atualizado' igual a False.

        Caso você queira força a atualização de um objeto existente na execução
        deste método, torne o campo 'atualizado' = False.

        Exemplos: Comissão de Cultura, Comissão de Educação, etc.
        """
        result = self.executar_metodo("ObterOrgaos")

        for item in self.as_list(result.orgaos.orgao):

            # Consulta se o objeto já existe e a flag "atualizado" está ativa
            existe = Orgao.objects.filter(id=int(item._id)).first()
            if existe and existe.atualizado:
                logger.info(u"%s já está atualizado. %s ignorando." %
                            (existe._meta.object_name, existe))
                continue

            # Caso o tipo do órgão não exista na base, não temos dados
            # suficientes para cadastrá-lo, neste caso o orgão ficará sem tipo.
            tipo = TipoOrgao.objects.filter(id=int(item._idTipodeOrgao)).first()

            # Cria o novo objeto
            novo = Orgao(id = int(item._id),
                         sigla = self.as_text_without_spaces(item._sigla),
                         descricao = self.as_text(item._descricao),
                         tipo = tipo)
            novo.save()
            logger.info(u"%s importado com sucesso (%s)." %
                        (novo._meta.object_name, novo))


    def importar_cargos(self):
        """
        Obtém os cargos e importa localmente.

        Este método acessa a API da Câmara dos Deputados e salva na base de
        dados local, apenas se o cargo não existir ou possuir o campo
        'atualizado' igual a False.

        Caso você queira força a atualização de um objeto existente na execução
        deste método, torne o campo 'atualizado' = False.
        """

        result = self.executar_metodo("ListarCargosOrgaosLegislativosCD")

        for item in self.as_list(result.cargosOrgaos.cargo):

            # Consulta se o objeto já existe e a flag "atualizado" está ativa
            existe = Cargo.objects.filter(id=int(item._id)).first()
            if existe and existe.atualizado:
                logger.info(u"%s já está atualizado. %s ignorando." %
                            (existe._meta.object_name, existe))
                continue

            # Cria o novo objeto
            novo = Cargo(id = int(item._id),
                         descricao = self.as_text(item._descricao))
            novo.save()
            logger.info(u"%s importado com sucesso (%s)." %
                        (novo._meta.object_name, novo))

        cargo = Cargo(descricao = 'Membro Titular')
        cargo.save()
    
        cargo = Cargo(descricao = 'Membro Suplente')
        cargo.save()
