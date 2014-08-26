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
import suds
import logging
import urllib2

logging.basicConfig(level=settings.CAMARA_API_LOG_LEVEL)
logger = logging.getLogger('entendaobrasil.api.camara')

class DeputadosCamara(CamaraAPI):
    def __init__(self):
        self.wsdl_url = "http://www.camara.gov.br/SitCamaraWS/Deputados.asmx?wsdl"
        return super(DeputadosCamara, self).__init__()

    def importar_partidos(self):
        """
        Obtém os partidos com representação na Câmara dos Deputados.

        Este método acessa a API da Câmara dos Deputados e salva na base de
        dados local, apenas se o partido não existir ou possuir o campo
        'atualizado' igual a False.

        Caso você queira força a atualização de um objeto existente na execução
        deste método, torne o campo 'atualizado' = False.

        Note: Infelizmente este endpoint encontra-se no webservice "Deputados",
        onde deveria possuir um endpoint próprio.
        """
        result = self.executar_metodo("ObterPartidosCD")
        for item in self.as_list(result.partidos.partido):

            # Consulta se o objeto já existe e a flag "atualizado" está ativa
            existe = Partido.objects.filter(sigla=item.siglaPartido).first()
            if existe and existe.atualizado:
                logger.info(u"%s já está atualizado. %s ignorado." %
                            (existe._meta.object_name, existe))
                continue

            # Cria o novo objeto
            novo = Partido(sigla = self.as_text(item.siglaPartido),
                           nome = self.as_text(item.nomePartido),
                           data_criacao = self.as_date(item.dataCriacao),
                           data_extincao = self.as_date(item.dataExtincao))
            novo.save()
            logger.info(u"%s importado com sucesso (%s)." %
                        (novo._meta.object_name, novo))

    def importar_deputados(self):
        """
        Obtém os deputados em exercício da Câmara dos Deputados.

        Este método acessa a API da Câmara dos Deputados e salva na base de
        dados local, apenas se o deputado não existir ou possuir o campo
        'atualizado' igual a False.

        Caso você queira força a atualização de um objeto existente na execução
        deste método, torne o campo 'atualizado' = False.
        """
        result = self.executar_metodo("ObterDeputados")
        for item in self.as_list(result.deputados.deputado):
 
            # Consulta se o objeto já existe e a flag "atualizado" está ativa
            existe = Parlamentar.objects.filter(ide_cadastro = int(item.ideCadastro)).first()
            if existe and existe.atualizado:
                logger.info(u"%s já está atualizado. %s ignorado." %
                            (existe._meta.object_name, existe))
                continue

            endereco = u"Câmara dos Deputados, Edifício Principal,"
            endereco += u"Praça dos Três Poderes, Gabinete %s." % self.as_text(item.gabinete)
            endereco += u"Anexo %s. CEP: 70.160-900 - Brasília/DF" % self.as_text(item.anexo)

            # Cria o novo objeto
            novo = Parlamentar(ide_cadastro = int(item.ideCadastro),
                               nome = self.as_text(item.nome),
                               nome_parlamentar = self.as_text(item.nomeParlamentar),
                               email = self.as_text_without_spaces(item.email),
                               sexo = item.sexo[0].upper(),
                               uf = self.as_text_without_spaces(item.uf).upper(),
                               telefone = u"(61) %s" % self.as_text(item.fone),
                               endereco = endereco,
                               partido = Partido.objects.get(sigla=item.partido),
                               tipo = 'D')
            novo.save()
            logger.info(u"%s importado com sucesso (%s)." %
                        (novo._meta.object_name, novo))

    def importar_detalhes_deputado(self, parlamentar, legislatura):
        try:
            result = self.executar_metodo("ObterDetalhesDeputado",
                                          ideCadastro = parlamentar.ide_cadastro,
                                          numLegislatura = legislatura)

            # Atualiza algumas informações básicas do deputado
            item = result.Deputados.Deputado
            parlamentar.profissao = self.as_text(item.nomeProfissao)
            parlamentar.data_nascimento = self.as_date(item.dataNascimento)
            parlamentar.uf = self.as_text_without_spaces(item.ufRepresentacaoAtual)
            parlamentar.save()
            logger.info(u"Detalhes básicos do Parlamentar atualizado. (%s)" % parlamentar)
        except suds.WebFault:
            logger.debug(u"Deputado %d sem dados para a legislatura %d" %
                         (parlamentar.ide_cadastro, legislatura))
            return False


        # Atualiza os Orgaos em que foi membro
        comissoes = item.comissoes
        if (len(comissoes) == 0):
            return

        for comissao in self.as_list(comissoes.comissao):
            orgao_id = int(comissao.idOrgaoLegislativoCD)
            orgao_sigla = self.as_text_without_spaces(comissao.siglaComissao)
            orgao_nome = u"%s" % self.as_text(comissao.nomeComissao)

            logger.info(u"Adicionando parlamentar ao Orgao ID: %d, %s" % (orgao_id, orgao_sigla))

            tipo = TipoOrgao.objects.get(id=110) # Comissao da Camara dos Deputados

            try:
                orgao = Orgao.objects.get(id = orgao_id)
            except Orgao.DoesNotExist:
                orgao = Orgao(id = orgao_id,
                              sigla = orgao_sigla,
                              descricao = orgao_nome,
                              tipo = tipo)
                orgao.save()

            condicao = self.as_text(comissao.condicaoMembro)
            data_entrada = self.as_date(comissao.dataEntrada)
            data_saida = self.as_date(comissao.dataSaida)


            # Cria objeto em CargoOrgao (Cargo exercido em determinado Orgao)
            cargo_id = 1001 if condicao == "Titular" else 1002
            cargo_base = Cargo.objects.get(id=cargo_id)

            cargo_orgao, _ = CargoOrgao.objects.get_or_create(orgao = orgao,
                                                              cargo = cargo_base,
                                                              parlamentar = parlamentar,
                                                              data_entrada = data_entrada,
                                                              data_saida = data_saida)
            cargo_orgao.save()


        cargos_comissoes = item.cargosComissoes
        if (len(cargos_comissoes) == 0):
            return

        for cargo_comissao in self.as_list(cargos_comissoes.cargoComissoes):
            orgao_id = int(cargo_comissao.idOrgaoLegislativoCD)
            orgao_sigla = self.as_text_without_spaces(cargo_comissao.siglaComissao)
            orgao_nome = u"%s" % self.as_text(cargo_comissao.nomeComissao)

            tipo = TipoOrgao.objects.get(id=110) # Comissao da Camara dos Deputados

            try:
                orgao = Orgao.objects.get(id = orgao_id)
            except Orgao.DoesNotExist:
                orgao = Orgao(id = orgao_id,
                              sigla = orgao_sigla,
                              descricao = orgao_nome,
                              tipo = tipo)
                orgao.save()

        
            cargo_id = int(cargo_comissao.idCargo)
            data_entrada = self.as_date(cargo_comissao.dataEntrada)
            data_saida = self.as_date(cargo_comissao.dataSaida)

            # Cria objeto em CargoOrgao (Cargo exercido em determinado Orgao)
            cargo_base = Cargo.objects.get(id=cargo_id)

            cargo_orgao, _ = CargoOrgao.objects.get_or_create(orgao = orgao,
                                                              cargo = cargo_base,
                                                              parlamentar = parlamentar,
                                                              data_entrada = data_entrada,
                                                              data_saida = data_saida)
            cargo_orgao.save()

        logger.info(u"Detalhes sobre as comissões do Parlamentar atualizado. (%s)" % parlamentar)

    def importar_detalhes_deputados(self):
        legislaturas = [53,54]

        for parlamentar in Parlamentar.objects.all():
            for legislatura in legislaturas:
               while True:
                   try:
                       self.importar_detalhes_deputado(parlamentar, legislatura)
                   except urllib2.URLError:
                       logger.error(u"Erro de conexão retentando para o parlamentar %s, legislatura %d" %
                                    (parlamentar, legislatura))
                       continue
                   break

    def importar_photos(self):
        for parlamentar in Parlamentar.objects.all():
            parlamentar.download_photos()
