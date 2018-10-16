from examples.ebook_crawler import TestCrawler

if __name__ == '__main__':
    with TestCrawler('ebook_updated.csv') as crawler:
        crawler.process_data()