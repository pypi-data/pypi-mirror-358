import sys,os,re

from .command.InputCMD import InputCMD
from .command.BrowserCMD import BrowserCMD
from .command.CrawlerCMD import CrawlerCMD
from .command.PersisterCMD import PersisterCMD

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.CommandFlow import CommandFlow

class Spider(CommandFlow):
  
  def load(self):

    input_cmd = InputCMD(self._context)
    browser_cmd = BrowserCMD(self._context)
    crawler_cmd = CrawlerCMD(self._context)
    persister_cmd = PersisterCMD(self._context)

    # check if the input context is legal
    self.add(input_cmd)
    
    # add the context.browser
    self.add(browser_cmd)
  
    # add the items
    self.add(crawler_cmd)

    # add the db_response
    self.add(persister_cmd)

    