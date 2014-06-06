#!/usr/bin/env python

from xml.dom import minidom
from core.models import Parlamentar, Partido
import wikipedia

doc = minidom.parse('raw/deputados.xml')
deputados = doc.getElementsByTagName("deputado")

fields_mapping = {'ideCadastro':'ide_cadastro',
                  'condicao': 'condicao',
                  'matricula':'matricula',
                  'idParlamentar': 'id_parlamentar',
                  'nome':'nome',
                  'nomeParlamentar':'nome_parlamentar',
                  'urlFoto':'url_foto',
                  'sexo':'sexo',
                  'uf':'uf',
                  'partido':'partido',
                  'gabinete':'gabinete',
                  'fone':'telefone',
                  'email':'email'}


def get_field_type(model, field):
  return model._meta.get_field(field).get_internal_type()


for deputado in deputados:
  p = Parlamentar()
  for old, new in fields_mapping.iteritems():
    field_type = get_field_type(Parlamentar, new)

    # Get value from xml
    value = deputado.getElementsByTagName(old)[0].firstChild.nodeValue

    print old, new, value

    if new == "partido":
      value = Partido.objects.filter(sigla=value).first()
    elif new == "condicao":
      if value == 'Titular':
        value = 'T'
      else:
        value = 'S'
    elif new == 'sexo':
      if value == 'masculino':
        value = 'M'
      else:
        value = 'F'

    if field_type == 'IntegerField':
      setattr(p, new, int(value))
    else:
      setattr(p, new, value)

  print "Searching wikipedia for %s..." % p.nome_parlamentar
  try:
    wikipedia.set_lang("pt")
    w = wikipedia.page(p.nome_parlamentar)
    p.wikipedia = w.url
    p.sumario = w.summary
  except wikipedia.exceptions.PageError:
    print "not found"
    pass
  except wikipedia.exceptions.DisambiguationError:
    print "Disambigation"
    pass

  p.tipo = 'D'
  p.save()
