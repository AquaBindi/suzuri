# -*- coding: utf-8 --
DEBUG = True
LOCALE_PATHS = []

TEMPLATES = {
  'DIRS': [],
  'BASE_NAME': 'templates',
  'CACHE': True,
  'ENCODING': 'utf8',
  'CONTEXT_PROCESSORS': []
}

STORAGE = {}

"""
Beaker use redis for Example

redis://[:password]@localhost:6379/0
unix://[:password]@/path/to/socket.sock?db=0

mongodb Example
'mongodb://%s:%s@127.0.0.1:27017/db' % (username, password)

"""
SESSION_OPTS = {
  'session.cookie_domain': 'localhost:5500',
  'session.type': 'ext:mongodb',
  'session.url': 'mongodb://localhost/capdio',
  #'session.url': 'mongodb://user:password@localhost:27017/capdio',
  'session.auto': True,
  'session.httponly': True,
  'session.secure': True
}

# Custom logging configuration.
LOGGING = {}
