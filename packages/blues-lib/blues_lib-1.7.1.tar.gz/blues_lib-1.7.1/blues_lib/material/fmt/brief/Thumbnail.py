import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut
from material.file.MatFile import MatFile

class Thumbnail(AllMatchHandler):

  def resolve(self)->STDOut:
    try:
      entities = self._request.get('entities')
      for entity in entities:
        self._set(entity)
      return STDOut(200,'ok',entities)
    except Exception as e:
      return STDOut(500,'Thumbnail resolve failed %s' % e,None)

  def _set(self,entity):
      # convert online image to local image
      site = entity.get('material_site')
      id = entity.get('material_id')
      url = entity.get('material_thumbnail')
      stdout = MatFile.get_download_image(site,id,url)
      if stdout.code==200:
        entity['material_thumbnail'] = stdout.data

