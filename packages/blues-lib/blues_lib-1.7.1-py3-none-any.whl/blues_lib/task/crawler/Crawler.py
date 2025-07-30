import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.BhvExecutor import BhvExecutor
from type.output.STDOut import STDOut

class Crawler():

  def __init__(self,request:dict) -> None:
    '''
    Parameter:
      request {dict} : 
        - schema: dict, the schema configuration for crawling
        - browser: object, the browser instance to use
        - entity: dict, optional entity data
    '''
    self._request = request

  def crawl(self)->STDOut:
    
    browser = self._request.get('browser')
    keep_alive = self._request.get('keep_alive',False)
    model = self._request.get('model')
    try:
      executor = BhvExecutor(model,browser)
      return executor.execute()
    except Exception as e:
      return STDOut(500,'Crawl failed %s' % e)
    finally:
      if browser and not keep_alive:
        browser.quit()


