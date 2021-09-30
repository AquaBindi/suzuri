# -*- coding: utf-8 -*-
"""
storage for suzuri
"""
from suzuri.storage.mongodb import MongoStorage
from suzuri.storage.rethinkdb import RethinkStorage


def get_storage(config=None):
  storage = None
  if isinstance(config, dict):
    db_type = config.get('type')
    if db_type  == 'mongodb':
      storage = MongoStorage(config)
    elif db_type == 'rethinkdb':
      storage = RethinkStorage(config)

  if not storage:
    storage = MongoStorage()

  return storage
