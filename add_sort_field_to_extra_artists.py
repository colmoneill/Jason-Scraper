#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main.settings import db

for exhib in db.exhibitions.find({'is_group_expo': True}):
  artists = exhib['extra_artists']

  for key, artist in enumerate(artists):
    old = exhib['extra_artists'][key]
    parts = old.rsplit(' ', 1)

    if len(parts) > 1:
      sort = u'{1}, {0}'.format(parts[0], parts[1])
    else:
      sort = old

    exhib['extra_artists'][key] = {'name': old, 'artist_sort': sort}
  
  db.exhibitions.update({'_id': exhib['_id']}, exhib)