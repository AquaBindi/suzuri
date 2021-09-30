from __future__ import absolute_import

from falcon import errors
from falcon.media import BaseHandler
import umsgpack

class UMessagePackHandler(BaseHandler):
  """Handler built using the :py:mod:`u-msgpack-python` module.

  This handler uses ``umsgpack.unpackb()`` and ``umsgpack.packb()``. The
  MessagePack ``bin`` type is used to distinguish between Unicode strings
  (``str`` on Python 3, ``unicode`` on Python 2) and byte strings
  (``bytes`` on Python 2/3, or ``str`` on Python 2).

  Note:
      This handler requires the extra ``u-msgpack-python`` package, which
      must be installed in addition to ``falcon`` from PyPI:

      .. code::

          $ pip install u-msgpack-python

  """

  def __init__(self):
    #umsgpack.compatibility = True
    self.msgpack = umsgpack

  def deserialize(self, stream, content_type, content_length):
    try:
      return self.msgpack.unpackb(stream.read())
    except ValueError as err:
      raise errors.HTTPBadRequest(
        'Invalid MessagePack',
        'Could not parse MessagePack body - {0}'.format(err)
      )
    except TypeError as err:
      raise errors.HTTPBadRequest(
        'Invalid MessagePack',
        'Could not parse MessagePack body - {0}'.format(err)
      )

  def serialize(self, media, content_type):
    return self.msgpack.packb(media)
