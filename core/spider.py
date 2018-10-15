from utils.log import logger


class Recurse(Exception):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def recurse(*args, **kwargs):
    raise Recurse(*args, **kwargs)


def tail_recursive(f):
    def decorated(*args, **kwargs):
        while True:
            try:
                return f(*args, **kwargs)
            except Recurse as r:
                args = r.args
                kwargs = r.kwargs
                continue

    return decorated


class Spider:
    def __init__(self):
        pass

    def get_data(self, url):
        try:
            pass
        except Exception as x:
            logger.error('Unexpected error when get data. Error details: {}'.format(x))
