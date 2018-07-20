from flask_restplus.reqparse import RequestParser

test_parser = RequestParser()
test_parser.add_argument('userid', type=str, required=True, location='form')
test_parser.add_argument('cid', type=str, required=True, location='form')

test_parser1 = RequestParser()
test_parser1.add_argument('cid', type=str, required=False, location='form')
test_parser1.add_argument('taskid', type=str, required=True, location='form')

test_parser2 = RequestParser()
test_parser2.add_argument('useralarmrecord_id', type=str, required=True, location='form')