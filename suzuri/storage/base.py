# -*- coding: utf-8 -*-
"""
storage base for suzuri
"""


class BaseStorage():
  """
   base storage class
  """
  def __init__(self, config=None):
    self.config = config or None
    if self.config:
      self.type_name = self.config.get('type', None)
    self.uri = None
    self.client = None

  def _connect(self):
    result = self.client
    return result

  def get_client(self):
    result = self.client
    if result is None:
      result = self._connect()

    return result

  def filter(self):
    pass

  def all(self):
    pass

  def __repr__(self):
    return '<%(cls)s "type=%(type)s", "host=%(uri)s">' % {
      'cls': self.__class__.__name__,
      'type': self.type_name,
      'uri': self.uri
    }
