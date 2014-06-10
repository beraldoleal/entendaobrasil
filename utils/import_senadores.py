#!/usr/bin/env python

from xml.dom import minidom
from core.models import Parlamentar, Partido
from datetime import datetime

doc = minidom.parse('raw/senadores.xml')
senadores = doc.getElementsByTagName("Parlamentar")

fields_mapping = {'CodigoParlamentar': 'id_parlamentar',
                  'NomeCompleto':'nome',
                  'Foto':'url_foto',
                  'Sexo':'sexo',
                  'SiglaUfNatural':'uf',
                  'SiglaPartido':'partido',
                  'TelefoneParlamentar':'telefone',
                  'DataNascimento':'data_nascimento',
                  'EnderecoEletronico':'email',
                  'Suplente':'condicao'}


def get_field_type(model, field):
  return model._meta.get_field(field).get_internal_type()


for senador in senadores:
  p = Parlamentar()
  for old, new in fields_mapping.iteritems():
    field_type = get_field_type(Parlamentar, new)

    print old, new,
    # Get value from xml

    try:
      value = senador.getElementsByTagName(old)[0].firstChild.nodeValue
    except IndexError:
      if new == 'condicao':
        value = 'T'

    print value

    if new == "partido":
      value = Partido.objects.filter(sigla=value).first()

    if field_type == 'IntegerField':
      setattr(p, new, int(value))
    elif field_type == 'DateField':
      try:
        date = datetime.strptime(value, "%Y-%m-%d")
        setattr(p, new, date)
      except ValueError:
        print "INFO: date is empty"
    else:
      setattr(p, new, value)

  p.tipo = 'S'
  p.save()
