from multiprocessing.pool import Pool
from core.spider import Spider
from utils.log import logger
import utils.log as log


class TestCrawler(Spider):
    __start_url = 'http://www.allitebooks.in/page/{}/'

    def __init__(self):
        Spider.__init__(self)

    def __enter__(self):
        log.init_logger(__name__)
        log.setup_stream_logger()
        log.setup_rotating_file_logger('test.log')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self

    def process_data(self):
        try:
            with Pool(1) as pool:
                pool.map(self.do_process, range(1, 2))
        except Exception as x:
            print(x)

    def do_process(self, n):
        try:
            response = self.fetch_data(self.__start_url.format(n))
            if not response:
                return

            data, redirected_url = response


        except Exception as x:
            logger.error(x)


if __name__ == '__main__':
    with TestCrawler() as crawler:
        crawler.process_data()
