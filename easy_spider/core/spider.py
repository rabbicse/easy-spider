import gzip
import http.cookiejar
import logging
import random
import socket
import urllib
from urllib import request
from urllib.error import HTTPError, URLError

from easy_spider.utils import tail_recursive

logger = logging.getLogger(__name__)


class Spider:
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    HEADERS = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    HTTP_RESPONSES = {
        100: ('Continue', 'Request received, please continue'),
        101: ('Switching Protocols', 'Switching to new protocol; obey Upgrade header'),
        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted', 'Request accepted, processing continues off-line'),
        203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
        204: ('No Content', 'Request fulfilled, nothing follows'),
        205: ('Reset Content', 'Clear input form for further input.'),
        206: ('Partial Content', 'Partial content follows.'),
        300: ('Multiple Choices', 'Object has several resources -- see URI list'),
        301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('See Other', 'Object moved -- see Method and URL list'),
        304: ('Not Modified', 'Document has not changed since given time'),
        305: ('Use Proxy', 'You must use proxy specified in Location to access this resource.'),
        307: ('Temporary Redirect', 'Object moved temporarily -- see URI list'),
        400: ('Bad Request', 'Bad request syntax or unsupported method'),
        401: ('Unauthorized', 'No permission -- see authorization schemes'),
        402: ('Payment Required', 'No payment -- see charging schemes'),
        403: ('Forbidden', 'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed', 'Specified method is invalid for this server.'),
        406: ('Not Acceptable', 'URI not available in preferred format.'),
        407: ('Proxy Authentication Required', 'You must authenticate with this proxy before proceeding.'),
        408: ('Request Timeout', 'Request timed out; try again later.'),
        409: ('Conflict', 'Request conflict.'),
        410: ('Gone', 'URI no longer exists and has been permanently removed.'),
        411: ('Length Required', 'Client must specify Content-Length.'),
        412: ('Precondition Failed', 'Precondition in headers is false.'),
        413: ('Request Entity Too Large', 'Entity is too large.'),
        414: ('Request-URI Too Long', 'URI is too long.'),
        415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
        416: ('Requested Range Not Satisfiable', 'Cannot satisfy request range.'),
        417: ('Expectation Failed', 'Expect condition could not be satisfied.'),
        500: ('Internal Server Error', 'Server got itself in trouble'),
        501: ('Not Implemented', 'Server does not support this operation'),
        502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
        503: ('Service Unavailable', 'The server cannot process the request due to a high load'),
        504: ('Gateway Timeout', 'The gateway server did not receive a timely response'),
        505: ('HTTP Version Not Supported', 'Cannot fulfill request.')
    }
    HTTP_RETRY_CODES = [403, 404, 408, 413, 500, 502, 503, 504]
    MAX_RETRY = 5

    def __init__(self, proxies=None, headers=None):
        socket.setdefaulttimeout(60)
        self.__proxies = proxies
        if headers:
            self.HEADERS = headers

    @tail_recursive
    def fetch_data(self, url, retry=0):
        try:
            logger.info('Fetching data from: {}'.format(url))
            # Create opener object
            opener = self.__create_opener()

            # open url
            # we'll get response
            response = opener.open(url)

            # we'll get response header from info()
            response_header = response.info()
            content_type = 'plain'
            if 'Content-Encoding' in response_header:
                content_type = response_header['Content-Encoding']

            # read the redirected url
            redirected_url = response.geturl()
            logger.info('Redirected URL: {}'.format(redirected_url))

            # Read data from response
            chunk_size = 128 * 1024  # 128 * 1024 bytes
            data = response.read(chunk_size)
            while True:
                chunk_data = response.read(chunk_size)
                if not chunk_data:
                    break
                data += chunk_data

            # We've specified gzip on request header for faster download
            # If server doesn't support gzip then it should return data without compression.
            try:
                if content_type == 'gzip':
                    data = gzip.decompress(data).decode('utf-8', 'ignore')
                else:
                    data = data.decode('utf-8', 'ignore')
            except:
                data = data.decode('utf-8', 'ignore')

            return data, redirected_url
        except HTTPError as e:
            if e.code in self.HTTP_RESPONSES:
                logger.error('Http Error! Error Code: {}; Error: {}; Error Details: {}!'
                             .format(e.code, self.HTTP_RESPONSES[e.code][0], self.HTTP_RESPONSES[e.code][1]))

            if retry < self.MAX_RETRY and e.code in self.HTTP_RETRY_CODES:
                return self.fetch_data(url, retry + 1)
        except URLError as e:
            logger.error('URLError: Failed to reach a server. Reason: {}'.format(e.reason))
            if retry < self.MAX_RETRY:
                return self.fetch_data(url, retry + 1)
        except Exception as x:
            logger.error('Unexpected error when get data. Error details: {}'.format(x))
            if retry < self.MAX_RETRY:
                return self.fetch_data(url, retry + 1)

    def __get_random_proxy(self):
        try:
            if not self.__proxies or len(self.__proxies) == 0:
                return

            proxy = random.choice(self.__proxies)
            logger.info('Proxy: {}'.format(proxy))

            if proxy['https'] == 'yes':
                return {'https': 'https://{}:{}'.format(proxy['ip'], proxy['port'])}
            else:
                return {'http': 'http://{}:{}'.format(proxy['ip'], proxy['port'])}
        except Exception as x:
            logger.error('Error when get random proxies. {}'.format(x))

    def __create_opener(self):
        try:
            proxy = self.__get_random_proxy()
            if proxy:
                proxy_handler = urllib.request.ProxyHandler(proxy)
                opener = urllib.request.build_opener(proxy_handler,
                                                     urllib.request.HTTPCookieProcessor(),
                                                     urllib.request.UnknownHandler(),
                                                     urllib.request.HTTPHandler(),
                                                     urllib.request.HTTPSHandler(),
                                                     urllib.request.HTTPRedirectHandler(),
                                                     urllib.request.HTTPDefaultErrorHandler(),
                                                     urllib.request.HTTPErrorProcessor())

                opener.addheaders.clear()
                for key in self.HEADERS:
                    if key not in opener.addheaders:
                        opener.addheaders.append((key, self.HEADERS[key]))

                return opener
            else:
                cj = http.cookiejar.CookieJar()
                opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                                     urllib.request.UnknownHandler(),
                                                     urllib.request.HTTPHandler(),
                                                     urllib.request.HTTPSHandler(),
                                                     urllib.request.HTTPRedirectHandler(),
                                                     urllib.request.HTTPDefaultErrorHandler(),
                                                     urllib.request.HTTPErrorProcessor())

                opener.addheaders.clear()
                for key in self.HEADERS:
                    opener.addheaders.append((key, self.HEADERS[key]))

                return opener
        except Exception as x:
            logger.error('Error when create opener.{}'.format(x))
