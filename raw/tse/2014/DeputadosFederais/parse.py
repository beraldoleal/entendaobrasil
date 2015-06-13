#!/usr/bin/env python
# -*- encoding: iso-8859-1 -*-
# Gera a lista de candidatos e seus respectivos valores em doacoes
#
# Execute:
# python parse.py > candidatos.json

import csv
import json
import sys
import operator
import os

def get_value(value):
    number = float("".join(value.split()[1].split(",")[0].split(".")))
    return number

def get_doacao(row):
  output = {}

  doador, doador_cpf_cnpj, tipo = get_doador(row)

  try:
    output['doador'] = doador.decode("iso-8859-1") # doador
    output['cpf_cnpj'] = doador_cpf_cnpj.decode("iso-8859-1")
    output['recibo_eleitoral'] = row[5]
    output['documento'] = row[8]
    output['valor'] = get_value(row[6])
    output['especie_recurso'] = row[7]
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
      for row in reader:
        if row[0] == "Doador": continue

        candidato['nome'] = row[9].decode("iso-8859-1")
        candidato['numero'] = row[10]
        candidato['partido'] = row[12].decode("iso-8859-1")
        candidato['uf'] = row[13].decode("iso-8859-1")
        candidato['candidatura'] = row[11].decode("iso-8859-1")
        candidato['sequencia'] = f.split('.')[0]

        doacao = get_doacao(row)
        total += doacao['valor']
        montante += doacao['valor']
      
      candidato['total'] = total

      candidatos.append(candidato)

output={}
output['resumo'] = {}
output['resumo']['candidatos'] = len(candidatos)
output['resumo']['montante'] = montante
output['candidatos'] = candidatos

print json.dumps(output, indent=4)
