#!/usr/bin/env python
# -*- encoding: iso-8859-1 -*-
import csv
import json
import sys
import operator

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

def exists(nodes, name):
  for node in nodes:
    if node['name'] == name:
      return True
  return False

# Prepara JSON
output = {}
with open('%s' % sys.argv[1], 'r') as csvfile:
  reader = csv.reader(csvfile, delimiter=';', quotechar='/')
  total = 0
  for row in reader:
    if row[0] == "Doador": continue

    numero = row[10]

    try:
      output['candidato']
    except KeyError:
      output['candidato'] = {}
      output['candidato']['nome'] = row[9].decode("iso-8859-1")
      output['candidato']['numero'] = numero
      output['candidato']['partido'] = row[12].decode("iso-8859-1")
      output['candidato']['uf'] = row[13].decode("iso-8859-1")
      output['candidato']['candidatura'] = row[11].decode("iso-8859-1")

    doacao = get_doacao(row)
    total += doacao['valor']

  output['candidato']['total'] = total

with open('%s.json' % numero, 'w') as outfile:
  print "SUCCESS: Salvando %s para %s.json, total = R$ %.2f" % (output['candidato']['nome'], numero, output['candidato']['total'])
  outfile.write(json.dumps(output, indent=4))

## Summarize
#summ = {}
#for numero, v in output.iteritems():
#  summ[numero] = {}
#  for doacao in output[numero]['doacoes']:
#    cpf_cnpj = doacao['cpf_cnpj']
#    try:
#      summ[numero][cpf_cnpj] += float(doacao['valor'])
#    except KeyError:
#      summ[numero][cpf_cnpj] = float(doacao['valor'])
#
#result = {}
#total = 20
## Ordenacao
#for numero, v in summ.iteritems():
#  s = sorted(summ[numero].items(), key=operator.itemgetter(1), reverse=True)
#
#  result[numero] = {}
#  result[numero]['doacoes'] = []
#
#  # Top 10
#  top = 0
#  for i in range(0,min(total, len(s))):
#    try:
#      result[numero]['doacoes'].append({"doador": s[i][0],
#                                        "valor": s[i][1]})
#
#      top += s[i][1]
#    except IndexError:
#      print "ERROR ordenacao"
#      print "%d - %d, %d - %d" % (0, min(total, len(s)), total, len(s))
#      print s[i]
#      sys.exit(-1)
#
#  # Outros
#  outros = 0
#
#  if total < len(s):
#    for i in range(total,len(s)):
#      outros += s[i][1]
#
#  result[numero]['doacoes'].append({"doador": "Outros",
#                                    "valor": outros})
#
#  result[numero]['dados'] = output[numero]['dados']
#  result[numero]['total'] = top + outros
#
#if len(result) != 1:
#  print "ERROR: Resultado com mais de um candidato skipping %s" % sys.argv[1]
#  sys.exit(0)


