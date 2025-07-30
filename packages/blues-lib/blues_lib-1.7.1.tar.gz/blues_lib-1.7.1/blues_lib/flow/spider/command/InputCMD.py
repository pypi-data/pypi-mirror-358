import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command

class InputCMD(Command):

  name = __name__

  def execute(self):

    executor_model = self._context.get('executor')
    if not executor_model:
      raise Exception('[Spider] The param executor is missing!')

    if not executor_model.config:
      raise Exception('[Spider] The param executor.config is missing!')