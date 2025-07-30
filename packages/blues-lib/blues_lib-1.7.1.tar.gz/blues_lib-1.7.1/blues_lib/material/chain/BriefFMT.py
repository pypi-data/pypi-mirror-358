import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut
from material.fmt.brief.Extender import Extender
from material.fmt.brief.Filter import Filter
from material.fmt.brief.Thumbnail import Thumbnail

class BriefFMT(AllMatchHandler):
  
  def resolve(self)->STDOut:
    chain = self._get_chain()
    return chain.handle()
  
  def _get_chain(self)->AllMatchHandler:
    extender = Extender(self._request)
    filter = Filter(self._request)
    thumbnail = Thumbnail(self._request)
    
    extender.set_next(filter).set_next(thumbnail)
    return extender
