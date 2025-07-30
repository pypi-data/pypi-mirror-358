import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from task.crawler.PageCrawler import PageCrawler

class CrawlerCMD(Command):

  name = __name__

  def execute(self):
    browser = self._context.get('browser')
    executor_model = self._context.get('executor')

    request = {
      'browser':browser,
      'model':executor_model,
    }

    crawler = PageCrawler(request)
    stdout = crawler.crawl()
    if stdout.code != 200 or not stdout.data:
      raise Exception('[Spider] Failed to crawl items!')

    self._context['entities'] = stdout.data

