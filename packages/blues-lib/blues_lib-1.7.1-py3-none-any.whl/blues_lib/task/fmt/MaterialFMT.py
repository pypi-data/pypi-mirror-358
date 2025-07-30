import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut

# brief chain
from material.chain.BriefFMT import BriefFMT
from material.chain.DetailFMT import DetailFMT

class MaterialFMT(AllMatchHandler):
  
  def resolve(self)->STDOut:
    chain = self._get_chain()
    return chain.handle()
  
  def _get_chain(self)->AllMatchHandler:
    brief_fmt = BriefFMT(self._request)
    detail_fmt = DetailFMT(self._request)

    brief_fmt.set_next(detail_fmt)
    return brief_fmt
