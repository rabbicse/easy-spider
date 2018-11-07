from examples.ebook_crawler import EbookCrawler

if __name__ == '__main__':
    with EbookCrawler('ebook_updated.csv') as crawler:
        crawler.process_data()