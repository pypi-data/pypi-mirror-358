import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from sele.browser.BrowserFactory import BrowserFactory   

class BrowserCMD(Command):

  name = __name__

  def execute(self):

    executor_model = self._context['executor']
    executor_config = executor_model.config
    browser_config = executor_config.get('browser')

    browser_mode = browser_config.get('mode') 
    executable_path = browser_config.get('path')

    loginer_model = self._context['loginer']
    if loginer_model :
      loginer_config = loginer_model.config
      browser = BrowserFactory(browser_mode).create(executable_path=executable_path,loginer_schema=loginer_config)
    else:
      browser = BrowserFactory(browser_mode).create(executable_path=executable_path)

    if not browser:
      raise Exception('[Spider] Failed to create the browser!')

    self._context['browser'] = browser
