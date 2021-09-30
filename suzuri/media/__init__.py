# -*- coding: utf-8 -*-
from falcon.media import JSONHandler
try:
  from rapidjson import dumps, loads
except ImportError:
  dumps = None
  loads = None

from .umsgpack import UMessagePackHandler


json_handler = JSONHandler(dumps=dumps, loads=loads)
unicode_msgpack_handler = UMessagePackHandler()
