from multiprocessing.pool import Pool
from core.spider import Spider
from utils.log import logger
import utils.log as log


class TestCrawler(Spider):
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
            with Pool(5) as pool:
                pool.map(self.do_process, range(1000))
        except Exception as x:
            print(x)

    def do_process(self, n):
        try:
            logger.info(n)
        except Exception as x:
            logger.error()


if __name__ == '__main__':
    with TestCrawler() as crawler:
        crawler.process_data()
