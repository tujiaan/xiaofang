import functools

import parse
from flask import request
from flask_restplus import reqparse

range_parser = reqparse.RequestParser()
range_parser.add_argument('page', type=int, help='页数', required=False, location='args')
range_parser.add_argument('limit', type=int, help='数量', required=False, location='args')


class Range(object):
    page = None
    limit= None

    def __init__(self, string):
        if string is not None:
            a = parse.search("items={page:d}-{limit:d}", string)
            b = parse.search("items={page:d}-", string)
            c = parse.search("items=-{limit:d}", string)
            s = a or b or c
            if s:
                s = s.named
                self.page = s.get('page', None)
                self.limit = s.get('limit', None)


def page_range(s=1, o=10):
    def decorator(method):
        @functools.wraps(method)
        def warpper(*args, **kwargs):
            result = method(*args, **kwargs)

            code = None
            header = {}
            if isinstance(result, tuple):
                l = len(result)
                code = result[1] if l > 1 else None
                header = result[2] if l > 2 else {}
                result = result[0]
            r = Range(request.headers.get('Range'))
            r2 = range_parser.parse_args()
            page = r.page or r2.get('page') or s
            limit = r.limit or r2.get('limit') or o
            totle =result.count()
            result = result.offset((int(page)-1)*limit).limit(limit)
            print(f'items {page}-{limit if page*limit<totle else totle}/{totle}')
            header['Content-Range'] = f'items {page}-{limit if page*limit<totle else totle}/{totle}'
            return result.all(), code, header
        return warpper
    return decorator


def page_format(code=0,msg=''):
    def decorator(method):
        @functools.wraps(method)
        def warpper(*args, **kwargs):
            result = method(*args, **kwargs)
            c = None
            header = {}
            if isinstance(result, tuple):
                l = len(result)
                c = result[1] if l > 1 else None
                header = result[2] if l > 2 else {}
                result = result[0]
           # print(header.get('Content-Range'))
            try:
                a = parse.search("items {page:d}-{limit:d}/{total:d}", header.get('Content-Range'))

                s = a.named
            except:
                s={'total':None}
            result={
                'code':code,
                'msg':msg,
                'count':s.get('total', None),
                'data':result
            }

            return result, c, header

        return warpper

    return decorator
