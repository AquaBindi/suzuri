# -*- coding: utf-8 -*-
import inspect
from pathlib import Path
from importlib import import_module
import logging
import tenjin
from suzuri.conf import settings

try:
  from webext import escape, to_str  # pylint: disable=unused-import
except ImportError:
  from tenjin.helpers import escape, to_str

logger = logging.getLogger('suzuri')


def string_to_list(hoge):
  if isinstance(hoge, (list, tuple)):
    result = hoge
  elif isinstance(hoge, str):
    result = [hoge]
  elif isinstance(hoge, type(None)):
    result = None
  else:
    raise TypeError('Not string or list or tuple')

  return result


def get_functions(func_list):
  result = []
  func_list = string_to_list(func_list)
  for func in func_list:
    names = func.split('.')
    module = import_module('.'.join(names[0:-1]))
    attr = getattr(module, names[-1])
    result.append(attr())

  return result


def get_default_preprocessors():
  result = ['tenjin.TemplatePreprocessor']
  if settings.DEBUG is False:
    result.append('tenjin.TrimPreprocessor')

  return result


def get_template_path(pathname):
  paths = string_to_list(settings.TEMPLATE_OPTION.get('template_path', []))
  if not paths:
    filepath = Path(pathname)
    base_name = settings.TEMPLATE_OPTION.get('base_name', 'templates')
    if filepath.is_file():
      path = filepath.parent / base_name
    else:
      path = filepath / base_name

    paths.append(str(path))

  return paths


def get_preprocessors():
  preprocessors = settings.TEMPLATE_OPTION.get('preprocessors')
  if preprocessors:
    try:
      result = get_functions(preprocessors)
    except (ValueError, AttributeError, ModuleNotFoundError) as err:
      logger.error(err)
      result = get_functions(get_default_preprocessors())
  else:
    result = get_functions(get_default_preprocessors())

  return result


def render(context=None, template=None, layout=':base', cache=None):
  if context:
    context.update({'debug': False})
  else:
    context = {'debug': False}

  curframe = inspect.currentframe()
  try:
    frameinfo = inspect.getouterframes(curframe, 2)[1]
  finally:
    del curframe

  paths = get_template_path(frameinfo.filename)

  if template is None:
    template = ':' + frameinfo.function

  preprocessors = get_preprocessors()

  if cache is None:
    cache = settings.TEMPLATE_OPTION.get('cache', True)

  encoding = settings.TEMPLATE_OPTION.get('encoding', 'utf-8')
  engine = tenjin.Engine(path=paths, postfix='.pyhtml', layout=layout,
                         encoding=encoding, cache=cache, pp=preprocessors,
                         trace=settings.DEBUG)

  # TODO: settings.TEMPLATE_CONTEXT_PROCESSORS
  context.update({'debug': settings.DEBUG})

  return engine.render(template, context)
