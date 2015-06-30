#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys

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
  remove = ['\xc1', '\xcd', '\xd4', 'ã', 'ç','\x83', '\x81', '\x8d', '\x94', '\.', '\/', '\-']
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
