import sys,os,re,json
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.chain.AllMatchHandler import AllMatchHandler

class Extender(AllMatchHandler):

  def resolve(self):
    try:
      entities = self._request.get('entities')
      for entity in entities:
        self._set(entity)
      return STDOut(200,'ok',entities)
    except Exception as e:
      return STDOut(500,'The extenter resolve failed %s' % e,None)


  def _set(self,entity:dict):

    paras = entity.get('material_body')
    body_dict = self._get_body_dict(paras)

    # append extend fields
    entity['material_body_text'] = body_dict['text']
    entity['material_body_image'] = body_dict['image']

  def _get_body_dict(self,paras:List[dict]):

    body_dict = {
      'text':[],
      'image':[],
    }
    for para in paras:
      body_dict[para['type']].append(para['value'])
    
    return body_dict




