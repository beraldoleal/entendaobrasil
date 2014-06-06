#!/usr/bin/env python

from xml.dom import minidom
from core.models import Partido

import time
from datetime import datetime

doc = minidom.parse('raw/partidos.xmls')
items = doc.getElementsByTagName("partido")

fields_mapping = {'siglaPartido':'sigla',
                  'nomePartido': 'nome',
                  'dataCriacao': 'data_criacao',
                  'dataExtincao': 'data_extincao',
                 }


def get_field_type(model, field):
  return model._meta.get_field(field).get_internal_type()


for item in items:
  p = Partido()
  for old, new in fields_mapping.iteritems():
    field_type = get_field_type(Partido, new)

    # Get value from xml
    value = item.getElementsByTagName(old)[0].firstChild.nodeValue

    #print "importing \'%s\' from %s to %s (%s)" % (value, old, new, field_type)

    if field_type == 'IntegerField':
      setattr(p, new, int(value))
    elif field_type == 'DateField':
      try:
        date = datetime.strptime(value, "%d/%m/%Y")
        setattr(p, new, date)
      except ValueError:
        print "INFO: date is empty"
    else:
      setattr(p, new, value)

  p.save()
