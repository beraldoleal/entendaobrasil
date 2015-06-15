#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Gera a lista de candidatos e seus respectivos valores em doacoes
# Gera também um arquivo para cada candidato com suas doacoes detalhadas.
#
# Execute:
#
# $ python parse.py > ../../../../site/tse/2014/data/candidato/list.json
# $ mv *.json ../../../../site/tse/2014/data/candidato/

import csv
import json
import sys
import operator
import os

def get_value(value):
    number = float("".join(value.split()[1].split(",")[0].split(".")))
    return number

def get_utf8(value):
  return value.decode('iso-8859-1').encode('utf-8')

def get_doacao(row):
  output = {}

  doador, doador_cpf_cnpj, tipo = get_doador(row)

  try:
    output['doador'] = get_utf8(doador)
    output['cpf_cnpj'] = get_utf8(doador_cpf_cnpj)
    output['recibo_eleitoral'] = row[5]
    output['documento'] = row[8]
    output['valor'] = get_value(row[6])
    output['especie_recurso'] = get_utf8(row[7])
    output['data'] = row[4]
    output['tipo'] = tipo
  except IndexError:
    print "ERROR: get_doacao %s" % sys.argv[1]
    print row
    sys.exit(-1)

  return output

def get_doador(row):
  if row[2] == "":
    return (row[0], row[1], "Direta")
  else:
    return (row[2], row[3], "Indireta")

candidatos = []
root, dirs, files = os.walk('.').next()
montante = 0
for f in files:
  if f.endswith('.csv'):
    with open(os.path.join(root, f)) as csvfile:       
      reader = csv.reader(csvfile, delimiter=';', quotechar='/')
      total = 0
      candidato = {}
      doacoes = []
      for row in reader:
        if row[0] == "Doador": continue

        candidato['nome'] = get_utf8(row[9])
        candidato['numero'] = get_utf8(row[10])
        candidato['partido'] = get_utf8(row[12])
        candidato['uf'] = get_utf8(row[13])
        candidato['candidatura'] = get_utf8(row[11])
        candidato['sequencia'] = f.split('.')[0]

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
      with open('%s.json' % candidato['sequencia'], 'w') as jsonfile:
        jsonfile.write(json.dumps(details, indent=4))


output={}
output['resumo'] = {}
output['resumo']['candidatos'] = len(candidatos)
output['resumo']['montante'] = montante
output['aaData'] = candidatos

print json.dumps(output, indent=4)