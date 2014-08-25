#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.models import Parlamentar
from googleapi import search
import sys 
import urllib
import os
import time
import logging

# Set log level and create a new logger
log_level = logging.DEBUG

logging.basicConfig(level=log_level)
logger = logging.getLogger('import-tool')

destination = "core/static/photos/deputados"

#if not os.path.isfile(destination):
#    urllib.urlretrieve(url_foto, destination)

parlamentares = Parlamentar.objects.all()

for parlamentar in parlamentares:
    query = "%s %s" % (parlamentar.tratamento(), parlamentar.nome_parlamentar)
    logger.info("Searching for photo (%s)" % query)

    dest_dir = "%s/%s" % (destination, parlamentar.ide_cadastro)
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    if len(parlamentar.fotos_perfil()) == 5:
        logger.info("Already downloaded, skipping %s" % query)
        continue

    results = search.images(query.encode("UTF-8"), 5)
    i=1
    for result in results:
        f = "%s/%s/%d.jpg" % (destination, parlamentar.ide_cadastro, i)
        try:
            if not os.path.isfile(f):
                opener = urllib.urlopen(result['image_url'])
                if opener.headers.maintype == 'image':
                    open(f, 'wb').write(opener.read())
                #urllib.urlretrieve(result['image_url'].encode("UTF-8"), f)
        except UnicodeEncodeError:
            logger.error("Skipping %s, url with wrong enconde" % query)
        except IOError:
            logger.error("Skipping %s, timeout" % query)
            time.sleep(5)
            
        i=i+1

