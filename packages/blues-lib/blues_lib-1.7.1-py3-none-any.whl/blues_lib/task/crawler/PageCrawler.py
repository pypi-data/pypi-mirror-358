import sys,os,re
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.model.Model import Model
from task.crawler.Crawler import Crawler

class PageCrawler():

  def __init__(self,request:dict) -> None:
    '''
    Parameter:
      request {dict} : 
        - browser: Browser
        - mdoel: Model
    '''
    self._browser = request.get('browser')
    self._model = request.get('model')
    self._meta = self._model.meta
    self._bizdata = self._model.bizdata
    self._config = self._model.config

  def crawl(self)->STDOut:
    try:
      return self._crawl()
    except Exception as e:
      return STDOut(500,'Briefs crawl failed %s' % e)
    finally:
      self._browser and self._browser.quit()
      
  def _crawl(self)->STDOut:
    # firstly : crawl the briefs
    briefs = self._crawl_briefs()
    if not briefs:
      return STDOut(500,'Briefs crawl failed')

    # secondly : loop to crawl the details
    materials = []
    count = int(self._config.get('count',0))

    for brief in briefs:
      self._append(brief,materials)
      if count and len(materials) >= count:
        break
    
    if materials:
      return STDOut(200,'ok',materials)
    else:
      return STDOut(500,'Materials crawl failed')
    
  def _append(self,brief,materials):
    bizdata = {
      'detail_url':brief.get('material_url'),
    }
    entity = self._crawl_detail(bizdata)
    if entity:
      materials.append(entity)

  def _crawl_briefs(self)->List[dict]:
    config = self._config.get('brief') # use the initial config
    model = Model(config)
    request = self._get_request(model)
    crawler = Crawler(request)
    stdout = crawler.crawl()
    return self._get_entity(stdout)
  
  def _crawl_detail(self,bizdata:dict)->dict:
    meta = self._meta.get('detail') # use the meta
    bd = {**self._bizdata,**bizdata} # interpolate with the mixed bizdata 
    model = Model(meta,bd)
    request = self._get_request(model)
    crawler = Crawler(request)
    stdout = crawler.crawl()
    return self._get_entity(stdout)

  def _get_request(self,model):
    return {
      'browser':self._browser,
      'model':model,
      'keep_alive':True,
    }
  
  def _get_entity(self,stdout):
    if stdout.code == 200 and stdout.data:
      return stdout.data.get('entity')
    return None
