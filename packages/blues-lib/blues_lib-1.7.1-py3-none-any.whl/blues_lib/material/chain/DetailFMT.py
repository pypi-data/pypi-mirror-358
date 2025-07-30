import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut
from material.fmt.detail.Body import Body
from material.fmt.detail.Extender import Extender
from material.fmt.detail.Filter import Filter
from material.fmt.detail.Image import Image

class DetailFMT(AllMatchHandler):
  
  def resolve(self)->STDOut:
    chain = self._get_chain()
    return chain.handle()
  
  def _get_chain(self)->AllMatchHandler:
    body = Body(self._request)
    image = Image(self._request)
    extender = Extender(self._request)
    filter = Filter(self._request)

    body.set_next(image).set_next(extender).set_next(filter)
    return body
