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

def get_eleito(entrada, mapfile):
    with open(mapfile) as map_csvfile:
        for line in map_csvfile:
            if entrada in line:
                return True
    return False

def get_value(value):
    #number = float("".join(value.split()[1].split(",")[0].split(".")))
    number = float(value.split()[1].replace('.', '').replace(',','.'))
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

def clean(text):
  remove = ['á', 'ç', 'ã', 'é', 'i', '\x83', '\x81', '\x8d', '\x94']
  return text.translate(None, ''.join(remove))

def get_uf(unidade):
  ufs = {'ACRE': 'AC',
         'ALAGOAS': 'AL',
         'AMAZONAS': 'AM',
         'AMAP': 'AP',
         'BAHIA': 'BA',
         'CEAR': 'CE',
         'DISTRITO FEDERAL': 'DF',
         'ESPRITO SANTO': 'ES',
         'GOIS': 'GO',
         'MARANHO': 'MA',
         'MATO GROSSO': 'MT',
         'MATO GROSSO DO SUL': 'MS',
         'MINAS GERAIS': 'MG',
         'PAR': 'PA',
         'PARABA': 'PB',
         'PARAN': 'PR',
         'PERNAMBUCO': 'PE',
         'PIAU': 'PI',
         'RIO DE JANEIRO': 'RJ',
         'RIO GRANDE DO NORTE': 'RN',
         'RIO GRANDE DO SUL': 'RS',
         'RONDNIA': 'RO',
         'RORAIMA': 'RR',
         'SANTA CATARINA': 'SC',
         "SO PAULO": 'SP',
         'SERGIPE': 'SE',
         'TOCANTINS': 'TO'}

  return ufs[clean(unidade)]

def main():
    candidatos = []
    foto = "http://divulgacand2014.tse.jus.br/divulga-cand-2014/eleicao/2014/UF/%s/foto/%s.jpg"
    root, dirs, files = os.walk('.').next()
    montante = 0
    for f in files:
        if f == "map-candidato-parlamentar.csv":
            continue
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
                    candidato['eleito'] = get_eleito(codigo, os.path.join(root,"map-candidato-parlamentar.csv"))
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
                with open('%s.json' % candidato['sequencia'], 'w') as jsonfile:
                  jsonfile.write(json.dumps(details, indent=4))

    output={}
    output['resumo'] = {}
    output['resumo']['candidatos'] = len(candidatos)
    output['resumo']['montante'] = montante
    output['aaData'] = candidatos

    print json.dumps(output, indent=4)

if __name__ == '__main__':
    main()

