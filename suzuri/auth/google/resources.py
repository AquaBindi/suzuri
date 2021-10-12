# -*- coding: utf-8 -*-
"""
 google oauth
"""
import inspect
import json
from pathlib import Path
import logging
import falcon
import requests
from google_auth_oauthlib.flow import Flow
from suzuri.conf import settings

logger = logging.getLogger('suzuri')

class AuthResource():
  """
    google auth
  """
  def logout(self, req, _):  # pylint: disable=no-self-use
    session = req.env.get('beaker.session')
    if session:
      if not session.get('auth'):
        logger.error('Can not delete auth. auth is None in session')
      else:
        del session['auth']
        session.save()
        raise falcon.HTTPTemporaryRedirect('/')
    else:
      logger.error('not found session store')

    # TODO: render error.html
    # return render('error', msg)

  def get_secret(self):  # pylint: disable=no-self-use
    if isinstance(settings.GOOGLE_AUTH_SECRET, Path):
      result = str(settings.GOOGLE_AUTH_SECRET)
    elif isinstance(settings.GOOGLE_AUTH_SECRET, str):
      result = settings.GOOGLE_AUTH_SECRET
    else:
      err = TypeError('GOOGLE_AUTH_SECRET in settings')
      logger.error(err)
      result = ''

    return result

  def login(self, req, _):
    flow = Flow.from_client_secrets_file(
      self.get_secret(),
      scopes = settings.YOUTUBE_SCOPE)
    #flow.redirect_uri = 'http://localhost:5500/auth/google/oauth2callback'
    func_name = inspect.stack()[0][3]
    relative_uri = req.relative_uri.replace(func_name, '')
    uri = '{}://{}{}oauth2callback'.format(req.scheme,
                                           req.netloc,
                                           relative_uri)
    flow.redirect_uri = uri
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

  def oauth2callback(self, req, _):
    session = req.env.get('beaker.session')
    if session:
      state = session['auth']['google']['state']

      secret_path = self.get_secret()
      flow = Flow.from_client_secrets_file(
        secret_path,
        scopes = settings.YOUTUBE_SCOPE,
        state=state)

      with open(secret_path, 'r') as output_file:
        secret = json.load(output_file)
        flow.redirect_uri = secret.get('web').get('redirect_uris')[0]
        logger.debug(flow.redirect_uri)

      flow.redirect_uri = 'http://localhost:5500/auth/google/oauth2callback'

      authorization_response = req.url
      flow.fetch_token(authorization_response=authorization_response)
      credentials = flow.credentials
      session['auth']['google']['credentials'] = credentials_to_dict(credentials)
      session.save()
    else:
      logger.error('not found session store')

    raise falcon.HTTPTemporaryRedirect('/')

  def get_attribute(self, method):
    try:
      if method:
        attr = getattr(self, method)
      else:
        attr = getattr(self, 'login')
    except AttributeError as err:
      raise falcon.HTTPNotFound(f'Not Found {method} method') from err

    return attr

  def on_get(self, req, resp, **params):
    attr = self.get_attribute(params.get('method'))
    try:
      resp.body = attr(req, params)
    except falcon.HTTPTemporaryRedirect as err:
      raise err
    else:
      resp.content_type = falcon.MEDIA_HTML
      resp.status = falcon.HTTP_200

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def credential_revoke(credentials_dict):
  requests.post('https://oauth2.googleapis.com/revoke',
                params = {'token': credentials_dict['token']},
                headers = {'content-type':
                           'application/x-www-form-urlencoded'})
