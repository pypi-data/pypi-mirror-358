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
    entities = self._request.get('entities')
    for entity in entities:
      stdout = self._validate(entity)
      typed_entities[stdout.message].append(entity)

    avail_entities = typed_entities['available']
    if avail_entities:
      # update the request's entities
      self._request['entities'] = avail_entities
      return STDOut(200,'available',avail_entities)
    else:
      return STDOut(500,'no available briefs',typed_entities)

  def _validate(self,entity)->STDOut:
    if not Checker.is_legal_brief(entity):
      return STDOut(500,'illegal',entity)

    if self.querier.exist(entity):
      return STDOut(500,'exist',entity)
    
    return STDOut(200,'available',entity)
