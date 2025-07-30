import sys, os
from . import pathtool
import importlib
IMPORT_RESOURCE = True
try:
  from importlib.resources import files
except ImportError:
  import pkg_resources
  IMPORT_RESOURCE = False
from types import ModuleType

try: _reloader = importlib.reload
except AttributeError: _reloader = reload

def add_path (directory):
  sys.path.insert (0, directory)

def remove_path (directory):
  for i, k in enumerate (sys.path):
    if k == directory:
      sys.path.pop (i)
      break

def from_file (hname, path):
  if sys.version_info [:2] >= (3, 5):
    import importlib.util
    spec = importlib.util.spec_from_file_location (hname, path)
    mod = importlib.util.module_from_spec (spec)
    mod.__file__ = path

    with open (path) as f:
      code = f.read ()

    if '__pyarmor__' in code:
      globals_dict = {"__file__": mod.__file__}
      exec (code, globals_dict)
      for item in [x for x in globals_dict ["__builtins__"]]:
        if hasattr (mod, item):
          continue
        setattr (mod, item, globals_dict ["__builtins__"].get (item))
    else:
      spec.loader.exec_module (mod)
    sys.modules [hname] = mod

  else:
    from importlib import machinery
    loader = machinery.SourceFileLoader (hname, path)
    mod = loader.load_module ()
  return mod

def from_pkg (resource_package, resource_path):
  if IMPORT_RESOURCE:
    template = files (resource_package).joinpath (resource_path).read_bytes()
  else:
    template = pkg_resources.resource_string (resource_package, resource_path)
  compiled = compile (template, '', 'exec')
  mod = ModuleType ("temp")
  exec (compiled, mod.__dict__)
  return mod

def importer (directory, libpath, module = None):
  add_path (directory)
  fn = not libpath.endswith (".py") and libpath + ".py" or libpath
  modpath = os.path.join (directory, fn)
  hname = fn.split (".")[0]
  p = directory.replace ("\\", "/")
  if p.find (":") !=- 1:
    p = "/" + p.replace (":", "")

  while 1:
    if "skitai.mounted." + hname in sys.modules:
      p, l = os.path.split (p)
      if not l:
        raise SystemError ('module %s already imported, use reload')
      hname = l + "." + hname
    else:
      hname = "skitai.mounted." + hname
      break
  mod = from_file (hname, modpath)
  remove_path (directory)
  return mod, mod.__file__

def reimporter (module, directory = None, libpath = None):
  if directory is None:
    directory, libpath = os.path.split (module.__file__)

  try:
    del sys.modules [module.__name__]
  except KeyError:
    return

  try:
    return importer (directory, libpath)
  except:
    sys.modules [module.__name__] = module
    raise

#----------------------------------------------
# will be deprecated
#----------------------------------------------

def reloader (module):
  directory = os.path.split (module.__file__) [0]
  add_path (directory)
  _reloader (module)
  remove_path (directory)

def importer_old (directory, libpath):
  sys.path.insert(0, directory)
  __import__ (libpath, globals ())
  libpath, abspath = pathtool.modpath (libpath)
  module = sys.modules [libpath]
  if abspath [-4:] in (".pyc", ".pyo"):
    abspath = abspath [:-1]
  sys.path.pop (0)
  return module, abspath
