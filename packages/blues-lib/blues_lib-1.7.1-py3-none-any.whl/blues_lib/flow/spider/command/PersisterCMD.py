import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from material.dao.mat.MatMutator import MatMutator 

class PersisterCMD(Command):

  name = __name__
  mutator = MatMutator()

  def execute(self):
    executor_model = self._context.get('executor')
    executor_config = executor_model.config

    persistent = executor_config.get('persistent')
    if not persistent:
      return 

    entities = self._context['entities']
    stdout = self.mutator.insert(entities)
    self._context['persister'] = stdout

    if stdout.code != 200:
      raise Exception('Failed to insert the items to the DB!')
