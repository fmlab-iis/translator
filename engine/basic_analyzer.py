import os
import subprocess

__paths_g = {}
__default_args_g = []

def set_paths(paths):
  assert not (paths["bin_file"]=="" or paths["conf_file"]=="" or paths["output_dir"]=="")
  global __paths_g, __default_args_g
  __paths_g = paths

  __default_args_g = [ paths["bin_file"] ]
  __default_args_g.extend(["-config", paths["conf_file"]])
  __default_args_g.extend(["-outputpath", paths["output_dir"]])

  out = paths["output_dir"]
  if not os.path.exists(out):
    os.makedirs(out)
  else:
    __clean_output_dir()

def __clean_output_dir():
  global __paths_g
  out = __paths_g["output_dir"]
  assert os.path.exists(out)
  for f in os.listdir(out):
    os.remove(out+'/'+f)

def analyze(rf_prog, entry_func="main"):
  __clean_output_dir()

  global __default_args_g, __paths_g
  assert __default_args_g
  args = list(__default_args_g) # copy

  # Set Entry Function
  args.extend(["-entryfunction", entry_func])
  # Set design to be verified
  args.append( rf_prog.create_file() )
  with open(os.devnull, "w") as null_file:
    # Call Verifier
    out_str = subprocess.check_output(args, universal_newlines=True, stderr=null_file)
    # TODO logging
    # logging.info(out_str)
  null_file.close()

  func_names = map(lambda f: f.get_name(), rf_prog.get_unwound_funcs())

  return AnalysisResultFactory.build_result("CPA", func_names, __paths_g["output_dir"])

class AnalysisResultFactory(object):
  factories = {}
  @staticmethod
  def add_factory(fid, result_factory):
    AnalysisResultFactory.factories[fid] = result_factory

  @staticmethod
  def build_result(fid, func_names, output_dir):
    return AnalysisResultFactory.factories[fid].build(func_names, output_dir)

class AnalysisResult(object):
  def __init__(self, func_names, output_dir):
    raise NotImplementedError
  def __str__(self):
    return self._getResult()
  def __repr__(self):
    return self._getResult()
  def __eq__(self, rhs):
    return rhs == self._getResult()
  def __ne__(self, rhs):
    return not self.__eq__(rhs)
  def _getResult(self):
    raise NotImplementedError

class Error(AnalysisResult):
  def _getResult(self):
    return 'Error'

class Pass(AnalysisResult):
  def _getResult(self):
    return 'Pass'
  def get_invariant_pairs(self, func_name):
    raise NotImplementedError

class Unknown(AnalysisResult):
  def __init__(self, func_names, output_dir):
    pass
  def _getResult(self):
    return 'Unknown'