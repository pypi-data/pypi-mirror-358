from typing import List
import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut

class Body(AllMatchHandler):

  def resolve(self)->STDOut:
    try:
      entities = self._request.get('entities')
      for entity in entities:
        entity['material_body'] = self._get(entity.get('material_body'))
      return STDOut(200,'ok',entities)
    except Exception as e:
      return STDOut(500,'The body resolve failed %s' % e,None)

  def _get(self,rows:List[dict])->List[dict]:
    paras:List[dict] = []
    for row in rows: 
      image = row.get('image')
      text = row.get('text')
      if image:
        paras.append({'type':'image','value':image})
      else:
        paras.append({'type':'text','value':text})
    return paras

