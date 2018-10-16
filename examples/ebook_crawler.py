import csv
import logging
import os
import re
from collections import OrderedDict
from multiprocessing import Semaphore, Value
from multiprocessing.pool import Pool
from bs4 import BeautifulSoup
from core.spider import Spider
import utils.log as log

logger = logging.getLogger(__name__)


class TestCrawler(Spider):
    __start_url = 'http://www.allitebooks.in/page/{}/'
    __url_cache = []
    __total = Value('i', 0)
    __lock = Semaphore()

    def __init__(self, output_csv):
        Spider.__init__(self)
        self.__output_csv = output_csv + '.csv' if not str(output_csv).endswith('.csv') else output_csv

    def __enter__(self):
        log.setup_stream_logger()
        log.setup_rotating_file_logger('ebook.log')

        hdr = [('name', 'Name'),
               ('year', 'Year'),
               ('url', 'Map URL')]

        self.__csv_header = OrderedDict(hdr)

        self.__field_names = list(self.__csv_header.keys())
        self.__field_values = list(self.__csv_header.values())

        # If output csv file already exists, then cache old website lists, so script will skip hitting existing records
        if os.path.exists(self.__output_csv):
            with open(self.__output_csv, 'r+', encoding='utf-8') as f:
                reader = csv.DictReader(f, self.__field_names)
                for row in reader:
                    self.__url_cache.append(row['url'])

        # If header not yet written then write csv header first
        if self.__csv_header['url'] not in self.__url_cache:
            self.__write_data(self.__csv_header)
            self.__url_cache.append(self.__csv_header['url'])

        with self.__total.get_lock():
            self.__total.value = len(self.__url_cache)
        logger.info('Total Previous Records Found: {}'.format(self.__total.value))

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info('Total records: {}'.format(self.__total.value))
        logger.info('Finish!!!')
        del self

    def process_data(self):
        try:
            with Pool(32) as pool:
                pool.map(self.do_process, range(1, 456))
        except Exception as x:
            print(x)

    def do_process(self, n):
        try:
            response = self.fetch_data(self.__start_url.format(n))
            if not response:
                return

            data, redirected_url = response

            soup = BeautifulSoup(data, 'html5lib')
            if not soup:
                return

            item_divs = soup.find_all('div', class_='td-item-details')
            for item_div in item_divs:
                link_a = item_div.find('a', {'rel': 'bookmark'})
                if not link_a:
                    continue

                link = link_a.get('href')
                if link in self.__url_cache:
                    logger.warning('Link: {} already grabbed!'.format(link))
                    continue

                item = {'url': link, 'name': link_a.text.strip()}
                desc_div = item_div.find('div', class_='td-excerpt')
                if desc_div:
                    year_m = re.search(r'Year\:\s*?(\d{4})', desc_div.text.strip())
                    if year_m:
                        item['year'] = year_m.group(1)

                self.__write_item(item)
        except Exception as x:
            logger.error(x)

    def __write_item(self, item):
        """
        Write item to csv file and write logs, lock writing to csv file as we've used multi-thread
        :param item:
        :return:
        """
        try:
            self.__lock.acquire()
            logger.info('Data: {}'.format(item))
            self.__write_data(item)
            self.__url_cache.append(item['url'])
        except Exception as ex:
            logger.error('Error write csv: {}'.format(ex))
        finally:
            self.__lock.release()

    def __write_data(self, row, mode='a+'):
        try:
            with open(self.__output_csv, mode, newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.__field_names, quoting=csv.QUOTE_ALL)
                writer.writerow(row)

                with self.__total.get_lock():
                    self.__total.value += 1
                    logger.info('Total: {}'.format(self.__total.value))
        except Exception as x:
            logger.error('Error printing csv output: {}'.format(x))


if __name__ == '__main__':
    with TestCrawler('ebook_data.csv') as crawler:
        crawler.process_data()
