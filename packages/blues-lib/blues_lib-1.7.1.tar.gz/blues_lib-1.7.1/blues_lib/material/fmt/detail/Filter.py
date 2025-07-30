import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut
from material.fmt.Checker import Checker
from material.dao.mat.MatQuerier import MatQuerier

class Filter(AllMatchHandler):

  querier = MatQuerier()

  def resolve(self):
    typed_entities = {
      'illegal':[],
      'exist':[],
      'available':[],
    } 
    errors = []
    entities = self._request.get('entities')
    for entity in entities:
      stdout = self._validate(entity)
      typed_entities[stdout.message].append(entity)
      if stdout.code!=200:
        errors.append(stdout.detail)

    avail_entities = typed_entities['available']
    if avail_entities:
      # update the request's entities
      self._request['entities'] = avail_entities
      return STDOut(200,'available',avail_entities,errors)
    else:
      return STDOut(500,'no available details',typed_entities,errors)

  def _validate(self,entity)->STDOut:
    if not Checker.is_legal_detail(entity):
      return STDOut(500,'illegal',entity,'illegal detail')
    
    if self.querier.exist(entity):
      return STDOut(500,'exist',entity)

    stdout = self._validate_limit(entity)
    if stdout.code!=200:
      return stdout
    
    return STDOut(200,'available',entity)

  def _validate_limit(self,entity:dict)->STDOut:
    schema = self._request.get('schema')
    if not schema:
      return STDOut(200,'available',entity)

    text_length = len(entity.get('material_body_text',''))
    min_text_length = int(schema.get('min_text_length',0))
    if min_text_length and text_length<min_text_length:
      return STDOut(500,'illegal',entity,'text length is less than min_text_length')

    max_text_length = int(schema.get('max_text_length',0))
    if max_text_length and text_length>max_text_length:
      return STDOut(500,'illegal',entity,'text length is greater than max_text_length')

    return STDOut(200,'available',entity)


