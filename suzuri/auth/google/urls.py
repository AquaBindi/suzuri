# -*- coding: utf-8 -*-
from .resources import AuthResource

urlpatterns = [
  ('/auth/google/{method}', AuthResource),
]
