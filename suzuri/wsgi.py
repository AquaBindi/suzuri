# -*- coding: utf-8 -*-
import os
import re
import logging
from importlib import import_module
import falcon
from beaker.middleware import SessionMiddleware
from suzuri.media import msgpack_handler, json_handler
from suzuri.conf import settings

logger = logging.getLogger('suzuri')
EXCLUDE_EXCEPTIONS = (falcon.HTTPTemporaryRedirect,)

def set_response(req, resp, msg_dict, tpl):
  render = import_module('suzuri.template').render
  if not req.content_type:
    resp.content_type = falcon.MEDIA_HTML
  else:
    if re.match('text/html.*', req.content_type):
      resp.content_type = falcon.MEDIA_HTML
    else:
      resp.content_type = req.content_type

  if resp.content_type == falcon.MEDIA_MSGPACK or \
     resp.content_type == falcon.MEDIA_JSON:
    resp.media = msg_dict
    resp.media.update({'result': 'failure'})
  else:
    resp.body = render(msg_dict, tpl, cache=False)

  return resp


def shink_root(req, resp):
  render = import_module('suzuri.template').render
  resp.status = falcon.HTTP_404
  if not req.content_type:
    logger.debug('None Request Content-Type')
    resp.content_type = falcon.MEDIA_HTML
  else:
    if re.match('text/html.*', req.content_type):
      resp.content_type = falcon.MEDIA_HTML
    else:
      logger.debug('Request Content-Type: %s', req.content_type)
      resp.content_type = req.content_type

  response = {'message': 'Not found'}
  if resp.content_type == falcon.MEDIA_HTML:
    resp.body = render(response, ':404', cache=False)
  elif resp.content_type == falcon.MEDIA_MSGPACK:
    resp.media = response.update({'result': 'failure'})
  elif resp.content_type == falcon.MEDIA_JSON:
    resp.media = response.update({'result': 'failure'})
  else:
    resp.body = 'Not found'


def handle_500(req, resp, ex, params):
  if isinstance(ex, EXCLUDE_EXCEPTIONS):
    raise ex

  logger.error('%s', ex.__class__.__name__)
  logger.error('%s', ex)
  logger.error('relative: %s', req.relative_uri)
  logger.error('params: %s', params)
  set_response(req, resp, {'message': 'server error'}, ':500')
  resp.status = falcon.HTTP_500


def handle_404(req, resp, ex, params):
  logger.error('%s', ex.__class__.__name__)
  logger.error('%s', ex)
  logger.error('relative: %s', req.relative_uri)
  logger.error('params: %s', params)
  set_response(req, resp, {'message': 'not found'}, ':404')
  resp.status = falcon.HTTP_404


def create_app():
  app = falcon.API()
  handlers = falcon.media.Handlers({
    falcon.MEDIA_MSGPACK: msgpack_handler,
    falcon.MEDIA_JSON: json_handler,
  })
  app.req_options.media_handlers.update(handlers)  # pylint: disable=no-member
  app.resp_options.media_handlers.update(handlers)  # pylint: disable=no-member

  app.add_sink(shink_root, '/')
  app.add_error_handler(Exception, handle_500)
  app.add_error_handler(falcon.HTTPNotFound, handle_404)

  last_apps = len(settings.INSTALLED_APPS) - 1
  for i, entry in enumerate(settings.INSTALLED_APPS):
    try:
      urlconf_module = import_module('%s.%s' % (entry, 'urls'))
      urlpatterns = getattr(urlconf_module, 'urlpatterns')
    except ModuleNotFoundError as err:
      logger.error(err)
    except AttributeError:
      logger.error('Error: Not found urlpatterns in %s.urls', entry)
    else:
      last_pattern = len(urlpatterns) - 1
      for j, (url_path, resource) in enumerate(urlpatterns):
        logger.info('%s => %s.%s', url_path, resource.__module__,
                    resource.__class__.__name__)
        if i == last_apps and j == last_pattern:
          app.add_route(url_path, resource(), compile=True)
        else:
          app.add_route(url_path, resource())

  return app


def get_wsgi_application():
  logger.info('%s', settings)
  app = create_app()
  app = SessionMiddleware(app, settings.SESSION_OPTS)

  if settings.DEBUG:
    # google auth
    # When running locally, disable OAuthlib's HTTPs verification.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  return app
