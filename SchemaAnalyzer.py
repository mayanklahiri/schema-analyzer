# SchemaAnalyzer.py
# Copyright 2013 Mayank Lahiri
# mlahiri@gmail.com
# Released under the terms of the BSD License.
import types

class SchemaAnalyzer:
  """A class for guessing an object schema from object examples."""
  def __init__(self):
    self.schema = {}
    
  def observe(self, example, root = None):
    """Add an example object to the set of observations."""
    # Sanity checks
    if root == None:
      root = self.schema
    if not isinstance(example, dict):
      raise("Non-dict type passed to SchemaAnalyzer.observe()")
    if not 'keys' in root: root['keys'] = {}
    if not 'count' in root: root['count'] = 0
    root['count'] += 1

    # Increment present/missing count on various keysets
    def new_key_(key): 
      root['keys'][key] = {
        'present':  0,
        'absent':   root['count'] - 1,
        'values':   {},
      }
    def missing_key_(key): root['keys'][key]['absent'] += 1
    def present_key_(key): root['keys'][key]['present'] += 1
    missing_keys = set(root['keys'].keys()) - set(example.keys())
    new_keys = set(example.keys()) - set(root['keys'].keys())
    map (new_key_, new_keys)
    map (missing_key_, missing_keys)
    map (present_key_, example.keys())

    # Handle values
    for (key, value) in example.iteritems():
      subtree = root['keys'][key]['values']
      value_type = type(value).__name__

      # Increment counts of this type
      if not value_type in subtree: 
        subtree[value_type] = {
          'count':      0,
          'exemplars':  {},
        }
      subtree[value_type]['count'] += 1

      # Record values of primitive types directly
      primitive_types = (int, long, float, complex, str, unicode)
      is_primitive = filter(lambda t: isinstance(value, t), primitive_types)
      if len(is_primitive):
        v = subtree[value_type]['exemplars'].get(value, 0)
        v += 1
        subtree[value_type]['exemplars'][value] = v
      elif isinstance(value, dict):
        subtree[value_type]['subtree'] = {}
        self.observe(value, root = subtree[value_type]['subtree'])
      # TODO: handle list, tuple, set types

  def analysis(self):
    """Return the schema analysis tree built up so far."""
    return self.schema
