# -*- coding: utf-8 -*-
import sys
import traceback
import logging
import falcon
from tenjin import TemplateNotFoundError
from suzuri.template import render
from suzuri.conf import settings
from suzuri.storage import get_storage

ACCESS_HEADER ='X-Access-Token'
ACCESS_TOKEN = 'access_token'

logger = logging.getLogger('suzuri')


def authorized_token(req, resp, res, params):  # pylint: disable=unused-argument
  req.params[ACCESS_TOKEN] = req.get_header(ACCESS_HEADER)

class BaseResource():
  """
   Base Resource
  """
  def __init__(self):
    self.storage = None

  def on_get(self, req, resp, **params):
    self._call_method('get', req, resp, **params)

  def on_post(self, req, resp, **params):
    self._call_method('post', req, resp, **params)

  def on_delete(self, req, resp, **params):
    self._call_method('delete', req, resp, **params)

  def _call_method(self, postfix, req, resp, **params):
    pass

  def exception_info(self):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    errmsg = ['{0}: {1}'.format(exc_type.__name__, exc_value)]
    tbinfo = traceback.format_tb(exc_traceback)
    lines = tbinfo[-1].split('\n')
    for line in lines:
      if line:
        errmsg.append(line.strip())
    for msg in errmsg:
      logger.error(msg)


class RESTfulResource(BaseResource):
  """
   REpresentational State Transfer ful resouce
  """
  media = 'json'
  _content_type = falcon.MEDIA_JSON

  def __init__(self):
    super().__init__()
    if self.media == 'msgpack':
      self._content_type = falcon.MEDIA_MSGPACK
    elif self.media == 'json':
      self._content_type = falcon.MEDIA_JSON
    else:
      logger.error('Error: Unknown media type %s', self.media)

  def _call_method(self, postfix, req, resp, **params):
    resp.content_type = self._content_type
    resp.status = falcon.HTTP_500
    doc = {'result': 'failure'}
    try:
      method = params.get('method')
      attr = getattr(self, method + '_' + postfix)
      if postfix == 'get':
        doc = attr(req, req.params)
      elif postfix == 'post':
        #body = req.stream.read().decode('utf-8')
        #params = parse.parse_qs(body)
        #rdoc = attr(req, params)
        doc = attr(req, req.media)
      elif postfix == 'delete':
        doc = attr(req)
    except (AttributeError, NameError, ValueError):
      exc_type, exc_value, _ = sys.exc_info()
      doc.update({
        'message': '{0}: {1}'.format(exc_type.__name__, exc_value)
        })
      logger.error(doc['message'])
      resp.media = doc
      resp.status = falcon.HTTP_200
    else:
      resp.media = doc
      resp.status = falcon.HTTP_200


class HtmlResource(BaseResource):
  """
   HTML resource
  """
  def _call_method(self, postfix, req, resp, **params):
    resp.content_type = falcon.MEDIA_HTML
    resp.status = falcon.HTTP_500
    resp.body = 'Internal server error'

    try:
      method = params.get('method') or 'index'
      if postfix == 'post':
        attr = getattr(self, method + '_' + postfix)
      else:
        attr = getattr(self, method)

      resp.body = attr(req, req.params)
      resp.status = falcon.HTTP_200
    except falcon.HTTPMovedPermanently:
      pass
    except AttributeError as err:
      logger.error(err)
      resp.status = falcon.HTTP_404
      resp.body = self.get_response_body(resp.status)
    except (NameError, TemplateNotFoundError) as err:
      logger.error('%s: %s <%s.%s>', err.__class__.__name__, err,
                   attr.__module__, attr.__name__)
      resp.status = falcon.HTTP_500
      resp.body = self.get_response_body(resp.status)


  def get_response_body(self, code):
    body = None
    context = {'message': 'Unknow status code'}
    try:
      if code == falcon.HTTP_404:
        context = {'message': 'Not found'}
        body = render(context, ':404')
      elif code == falcon.HTTP_500:
        context = {'message': 'Internal server error'}
        body = render(context, ':500')
    except Exception as err:  # pylint: disable=broad-except
      logger.exception(err)
      body = context['message']

    return body
