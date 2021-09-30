# -*- coding: utf-8 -*-
"""
Settings for suzuri
"""
import os
from importlib import import_module
from logging import config as logging_config
from dataclasses import dataclass
from suzuri.conf import global_settings

ENVIRONMENT_VARIABLE = "SUZURI_SETTINGS_MODULE"


@dataclass
class Settings():
  """
  settings data class
  """
  def __init__(self, settings_module=None):
    # update this dict from global settings (but only for ALL_CAPS settings)
    for key in dir(global_settings):
      if key.isupper():
        setattr(self, key, getattr(global_settings, key))

    self.default_settings = global_settings
    self.settings_module = settings_module
    if self.settings_module:
      mod = import_module(self.settings_module)
    else:
      return

    tuple_settings = (
      "INSTALLED_APPS",
      "LOCALE_PATHS",
      "TEMPLATE_CONTEXT_PROCESSORS",
    )
    for key in dir(mod):
      if key.isupper():
        value = getattr(mod, key)
        if (key in tuple_settings and
            not isinstance(value, (list, tuple))):
          raise ValueError("The %s setting must be a list or a tuple. " % key)
        setattr(self, key, value)

    self.setup()

  def __setattr__(self, name, value):
    self.__dict__.pop(name, None)
    super(self.__class__, self).__setattr__(name, value)  # pylint: disable=bad-super-call

  def __repr__(self):
    return '<%(cls)s "%(settings_module)s">' % {
      'cls': self.__class__.__name__,
      'settings_module': self.settings_module,
    }

  def __dir__(self):
    return sorted(
      s for s in [*self.__dict__, *dir(self.default_settings)]
    )

  def __getattr__(self, name):
    val = None
    try:
      val = getattr(self, name)
    except RecursionError:
      pass

    self.__dict__[name] = val
    return val

  def setup(self):
    logging_config.dictConfig(self.LOGGING)


settings = Settings(os.environ.get(ENVIRONMENT_VARIABLE))
