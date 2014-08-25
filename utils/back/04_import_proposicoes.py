#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api.camara import CamaraAPI
import sys

# WSDL SOAP URL
# Each endpoint has an url with webservice definitions
api = CamaraAPI("http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx?wsdl")

result = api.service.ListarProposicoes(sigla="PL", ano=2013)
for p in result.proposicoes.proposicao:
    print len(p.situacao)
#    print "** ID: %s, Numero: %s, Ano: %s (%s)" % (p.id, p.numero, p.ano, p.nome)
#    print "   Tipo...............: %s (%s - %s)" % (p.tipoProposicao.id, p.tipoProposicao.sigla, p.tipoProposicao.nome)
#    print "   Orgao Numerador....: %s (%s - %s)" % (p.orgaoNumerador.id, p.orgaoNumerador.sigla, p.orgaoNumerador.nome)
#    print "   Data Apresentacao..: %s" % (p.datApresentacao)
#    print "   Regime.............: %s (%s)" % (p.regime.codRegime, p.regime.txtRegime)
#    print "   Apreciacao.........: %s (%s)" % (p.apreciacao.id, p.apreciacao.txtApreciacao)
#    print p.situacao.orgao.codOrgaoEstado, p.situacao.orgao.siglaOrgaoEstado

sys.exit()
