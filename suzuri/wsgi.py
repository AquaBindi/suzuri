# -*- coding: utf-8 -*-
import os
import re
import logging
from logging import config as logging_config
from importlib import import_module
import falcon
from beaker.middleware import SessionMiddleware
from suzuri.media import unicode_msgpack_handler, json_handler
from suzuri.utils import get_all_routes

logger = logging.getLogger('suzuri')


def handle_404(req, resp):
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
    resp.body = render(response, ':404')
  elif resp.content_type == falcon.MEDIA_MSGPACK:
    resp.media = response.update({'result': 'failure'})
  elif resp.content_type == falcon.MEDIA_JSON:
    resp.media = response.update({'result': 'failure'})
  else:
    resp.body = 'Not found'


def create_app():
  app = falcon.API()
  handlers = falcon.media.Handlers({
    falcon.MEDIA_MSGPACK: unicode_msgpack_handler,
    falcon.MEDIA_JSON: json_handler,
  })
  app.req_options.media_handlers.update(handlers)  # pylint: disable=no-member
  app.resp_options.media_handlers.update(handlers)  # pylint: disable=no-member

  app.add_sink(handle_404, '/')

  return app


def get_wsgi_application():
  settings = import_module('suzuri.conf').settings
  logger.info('%s', settings)
  app = create_app()
  for entry in settings.INSTALLED_APPS:
    urlconf_module = import_module('%s.%s' % (entry, 'urls'))
    urlpattern = getattr(urlconf_module, 'urlpatterns', urlconf_module)

    for pattern in urlpattern:
      app.add_route(pattern[0], pattern[1]())  # pylint: disable=no-member

  for route in get_all_routes(app):
    logger.info('%s => %s.%s', route[0], route[1].__module__,
                route[1].__class__.__name__)

  # TODO change my session system
  app = SessionMiddleware(app, settings.SESSION_OPTS)

  if settings.DEBUG:
    # google auth
    # When running locally, disable OAuthlib's HTTPs verification.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  return app
