#!/usr/bin/env python

from googleapi import search

result = search.images('deputado eros biondini', 4)

for image in result:
	print image['description']
	print image['thumbnail_url']
	print image['image_url']
	
