# -*- coding: utf-8 -*-
import inspect
from pathlib import Path
from importlib import import_module
import logging
import tenjin
try:
  from webext import escape, to_str  # pylint: disable=unused-import
except ImportError:
  from tenjin.helpers import escape, to_str

logger = logging.getLogger('suzuri')


def render(context=None, template=None, layout=None, path='templates'):
  settings = import_module('suzuri.conf').settings
  if context:
    context.update({'debug': False})
  else:
    context = {'debug': False}

  if layout is None:
    layout = ':base'

  curframe = inspect.currentframe()
  try:
    frameinfo = inspect.getouterframes(curframe, 2)[1]
  finally:
    del curframe

  filename = Path(frameinfo.filename)
  if filename.is_file():
    path = str(filename.parent / path)

  if not template:
    template = ':' + frameinfo.function

  trace = True
  preprocessors = [tenjin.TemplatePreprocessor()]
  if settings.DEBUG is False:
    preprocessors.append(tenjin.TrimPreprocessor())
    trace = False

  cache = settings.TEMPLATE_OPTION.get('cache', True)
  encoding = settings.TEMPLATE_OPTION.get('encoding', 'utf-8')
  engine = tenjin.Engine(path=[path], postfix='.pyhtml', layout=layout,
                         encoding=encoding, cache=cache, pp=preprocessors,
                         trace=trace)

  # TODO: settings.TEMPLATE_CONTEXT_PROCESSORS
  context.update({'debug': settings.DEBUG})

  return engine.render(template, context)
