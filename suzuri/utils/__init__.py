# -*- coding: utf-8 --

#
# https://stackoverflow.com/questions/53559115/
#
def get_all_routes(app):
  routes_list = []

  def get_children(node):
    length = len(node.children)
    if length:
      for child_node in node.children:
        get_children(child_node)
    else:
      routes_list.append((node.uri_template, node.resource))

  roots = app._router._roots  # pylint: disable=protected-access
  for node in roots:
    get_children(node)

  return routes_list
