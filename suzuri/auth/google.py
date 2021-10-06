# -*- coding: utf-8 -*-
"""
 google oauth
"""
import os
import sys
import logging
import falcon
from google_auth_oauthlib.flow import Flow
from suzuri.conf import settings

logger = logging.getLogger('suzuri')

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

class AuthResource(object):
  def logout(self, req, params):
    session = req.env.get('beaker.session')
    if session:
      if session.get('auth'):
        del session['auth']
        session.save()
        raise falcon.HTTPTemporaryRedirect('/index.html')
      else:
        logger.error('can not clear. auth in session')

    else:
      logger.error('not found session store')

    # TODO: render error.html
    # return render('error', msg)

  def google_auth(self, req, params):
    flow = Flow.from_client_secrets_file(
      settings.PROJECT_PATH + '/client_secret.json',
      #scopes = ['https://www.googleapis.com/auth/youtube.force-ssl'],
      scopes = [settings.YOUTUBE_SCOPE])
    flow.redirect_uri = 'http://localhost:5500/auth/google_oauth2callback'
    authorization_url, state = flow.authorization_url(
      access_type = 'offline',
      include_granted_scopes = 'true')
    session = req.env.get('beaker.session')
    if session:
      session.update({'auth': {'google': {'state': state}}})
      session.save()
      logger.debug(session['auth'])
    else:
      logger.error('not found session store. can not save state')

    raise falcon.HTTPTemporaryRedirect(authorization_url)

  def google_oauth2callback(self, req, params):
    logger.debug('google_oauth2callback')
    session = req.env.get('beaker.session')
    if session:
      state = session['auth']['google']['state']

      flow = Flow.from_client_secrets_file(
        settings.PROJECT_PATH + '/client_secret.json',
        scopes = [settings.YOUTUBE_SCOPE],
        state=state)

      flow.redirect_uri = 'http://localhost:5500/auth/google_oauth2callback'

      authorization_response = req.url
      try:
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        session['auth']['google']['credentials'] = credentials_to_dict(credentials)
        session.save()
      except:
        exc_t, exc_v, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        text = '%s: %s - %s:%s' % (exc_t.__name__, str(exc_v), fname, exc_tb.tb_lineno)
        logger.error(text)

    else:
      logger.error('not found session store')

    raise falcon.HTTPTemporaryRedirect('/index.html')

  def on_get(self, req, resp, **params):
    doc = {'result': 'failure'}
    resp.content_type = falcon.MEDIA_HTML
    resp.status = falcon.HTTP_500

    try:
      attr = getattr(self, params.get('method'))
      doc = attr(req, req.params)
    except falcon.HTTPTemporaryRedirect as e:
      raise e
    except AttributeError as e:
      logger.error(e)
      raise e
    except Exception as e:
      logger.error(e)
      raise e
    else:
      resp.status = falcon.HTTP_200
      resp.body = doc

urlpattern = [
  ('/auth/{method}', AuthResource),
]
