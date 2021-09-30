# -*- coding: utf-8 -*-
import pymongo
from suzuri.storage.base import BaseStorage


class MongoStorage(BaseStorage):
  """
   MongoDB Storage
  """
  def _connect(self):
    host = None
    if self.config:
      host = self.config.get('host')
    if host:
      self.client = pymongo.MongoClient(host)
      self.uri = '%s' % host
    else:
      self.client = pymongo.MongoClient()
      self.uri = '%s:%s' %(self.client.HOST, self.client.PORT)

    return self.client

  def hoge(self):
    print('hoge')
