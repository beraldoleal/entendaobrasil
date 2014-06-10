#!/usr/bin/env python
from core.models import Parlamentar
from googleapi import search
import sys 
import urllib
import os

destination = "core/static/photos/deputados"

#if not os.path.isfile(destination):
#    urllib.urlretrieve(url_foto, destination)

parlamentares = Parlamentar.objects.all()

for parlamentar in parlamentares:
    print("INFO: Downloading photos from %s (%s)" % (parlamentar.nome, parlamentar.ide_cadastro))
    query = "%s %s" % (parlamentar.tratamento(), parlamentar.nome_parlamentar)
    results = search.images(query.encode("UTF-8"), 5)
    i=1
    for result in results:
        f = "%s/%s/%d.jpg" % (destination, parlamentar.ide_cadastro, i)
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.mkdir(d)
        try:
            if not os.path.isfile(f):
                #urllib.urlretrieve(result['thumbnail_url'].encode("UTF-8"), f)
                urllib.urlretrieve(result['image_url'].encode("UTF-8"), f)
        except UnicodeEncodeError:
            print("ERROR: Skipping %s, url with wrong enconde" % parlamentar.nome)
            
        i=i+1

