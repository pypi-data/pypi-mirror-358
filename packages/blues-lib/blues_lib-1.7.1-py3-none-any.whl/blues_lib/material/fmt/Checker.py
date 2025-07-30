import sys,os,re

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesType import BluesType    

class Checker():

  REQUIRED_BRIEF_FIELDS = ['material_id','material_site','material_title','material_url']
  REQUIRED_DETAIL_FIELDS = ['material_id','material_site','material_title','material_url','material_thumbnail','material_body']
  
  @classmethod
  def is_legal_brief(cls,entity):
    if not entity:
      return False
    return BluesType.is_field_satisfied_dict(entity,cls.REQUIRED_BRIEF_FIELDS,True)

  @classmethod
  def is_legal_detail(cls,entity):
    if not entity:
      return False
    return BluesType.is_field_satisfied_dict(entity,cls.REQUIRED_DETAIL_FIELDS,True)