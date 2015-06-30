#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Gera a lista de candidatos e seus respectivos valores em doacoes
# Gera também um arquivo para cada candidato com suas doacoes detalhadas.
#
# Execute:
#
# $ python parse.py > ../../../../site/tse/2014/data/candidato/list.json
# $ mv candidato/*.json ../../../../site/tse/2014/data/candidato/

import csv
import json
import sys
import operator
import os
from parseutils import *

def main():
    doadores = {}
    root, dirs, files = os.walk('csv/').next()
    montante = 0
    for f in files:
        if f.endswith('.csv'):
            with open(os.path.join(root, f)) as csvfile:
                reader = csv.reader(csvfile, delimiter=';', quotechar='/')
                doador = {}
                doacoes = []
                for row in reader:
                    if row[0] == "Doador":
                        continue
                    doacao = get_doacao(row)
                    doacao['candidato'] = get_utf8(row[9])
                    doacao['numero'] = get_utf8(row[10])
                    doacao['partido'] = get_utf8(row[12])
                    doacao['uf'] = get_uf(row[13])
                    doacao['candidatura'] = get_utf8(row[11])
                    doacao['sequencia'] = f.split('.')[0]
                    cpf_cnpj_clean = clean(doacao['cpf_cnpj'])

                    try:
                        doadores[cpf_cnpj_clean]['doacoes'].append(doacao)
                        doadores[cpf_cnpj_clean]['resumo']['total'] += doacao['valor']
                    except KeyError:
                        doadores[cpf_cnpj_clean] = {}
                        doadores[cpf_cnpj_clean]['doacoes'] = []
                        doadores[cpf_cnpj_clean]['doacoes'].append(doacao)
                        doadores[cpf_cnpj_clean]['resumo'] = {'nome': doacao['doador'],
                                                              'cpf_cnpj': doacao['cpf_cnpj'],
                                                              'total': doacao['valor']}
                    montante += doacao['valor']

    aadata = []
    for k,v in doadores.iteritems():
      aadata.append(v['resumo'])

      details = {}
      details['dados'] = v['resumo']
      details['aaData'] = v['doacoes']
      ## Salva arquivo individual por doador
      with open('doador/%s.json' % clean(v['resumo']['cpf_cnpj']), 'w') as jsonfile:
         jsonfile.write(json.dumps(details, indent=4))

    output={}
    output['resumo'] = {}
    output['resumo']['doadores'] = len(doadores)
    output['resumo']['montante'] = montante
    output['aaData'] = aadata

    print json.dumps(output, indent=4)

if __name__ == '__main__':
    main()

