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
    candidatos = []
    foto = "http://divulgacand2014.tse.jus.br/divulga-cand-2014/eleicao/2014/UF/%s/foto/%s.jpg"
    root, dirs, files = os.walk('csv/').next()
    montante = 0
    for f in files:
        if f.endswith('.csv'):
            with open(os.path.join(root, f)) as csvfile:
                reader = csv.reader(csvfile, delimiter=';', quotechar='/')
                total = 0
                candidato = {}
                doacoes = []
                for row in reader:
                    if row[0] == "Doador":
                        continue

                    candidato['nome'] = get_utf8(row[9])
                    candidato['numero'] = get_utf8(row[10])
                    candidato['partido'] = get_utf8(row[12])
                    candidato['uf'] = get_utf8(row[13])
                    candidato['candidatura'] = get_utf8(row[11])
                    candidato['sequencia'] = f.split('.')[0]
                    codigo = "2014%s%s" % (get_uf(candidato['uf']), candidato['numero'])
                    candidato['eleito'] = get_eleito(codigo, "map-candidato-parlamentar.csv")
                    candidato['codigo'] = codigo
                    candidato['foto'] = foto % (get_uf(candidato['uf']), candidato['sequencia'])
                    doacao = get_doacao(row)
                    doacoes.append(doacao)
                    total += doacao['valor']
                    montante += doacao['valor']

                candidato['total'] = total
                candidatos.append(candidato)

                details = {}
                details['dados'] = candidato
                details['aaData'] = doacoes
                # Salva arquivo individual por candidato
                with open('candidato/%s.json' % candidato['sequencia'], 'w') as jsonfile:
                  jsonfile.write(json.dumps(details, indent=4))

    output={}
    output['resumo'] = {}
    output['resumo']['candidatos'] = len(candidatos)
    output['resumo']['montante'] = montante
    output['aaData'] = candidatos

    print json.dumps(output, indent=4)

if __name__ == '__main__':
    main()

