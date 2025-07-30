import sys,os,re,json
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.chain.AllMatchHandler import AllMatchHandler
from material.file.MatFile import MatFile

class Image(AllMatchHandler):

  def resolve(self):
    try:
      entities = self._request.get('entities')
      for entity in entities:
        self._set(entity)
      return STDOut(200,'ok',entities)
    except Exception as e:
      return STDOut(500,'The image resolve failed %s' % e,None)


  def _set(self,entity:dict):
    schema = self._request.get('schema')
    paras = entity.get('material_body')
    if not paras or not schema:
      return

    max_image_count = int(schema.get('max_image_count',0))
    image_count = 0

    images:List[str] = [] 
    for para in paras:
      # download and deal image
      success = self._download(entity,para,images)
      if success:
        image_count+=1
      if max_image_count and image_count>=max_image_count:
        break

    self._pad_image(entity,images)
    self._pad_thumbnail(entity,images)
    
  def _download(self,entity:dict,para:dict,images:List[str])->bool:
    if para['type'] != 'image':
      return False

    site = entity.get('material_site')
    id = entity.get('material_id')
    url = para['value']
    stdout = MatFile.get_download_image(site,id,url)
    if stdout.code!=200:
      return False

    para['value'] = stdout.data
    images.append(stdout.data)
    return True

  def _pad_image(self,entity:dict,images:List[str]):
    material_thumbnail = entity.get('material_thumbnail')
    paras = entity.get('material_body')
    if not images and material_thumbnail:
      paras.append({'type':'image','value':material_thumbnail})
  
  def _pad_thumbnail(self,entity:dict,images:List[str]):
    if not entity.get('material_thumbnail') and images:
      entity['material_thumbnail'] = images[0]
