# import jpush
from flask_restplus import Namespace, Resource
# from app.ext import Jpush
from app.models import  UserAlarmRecord
from app.views.api_v1.getui.parser import test_parser, test_parser1
api = Namespace('Test', description='测试接口')
from .parser import *
from app.ext.getui import getui


@api.route('/getuibind/')
class test1(Resource):
    @api.expect(test_parser)
    def post(self):
        args = test_parser.parse_args()
        userid = args['userid']
        cid = args['cid']
        # print(getui.__dict__)################
        return getui.bind(userid, cid)
            # return
            # getui.sendList('你好guitui',['123456789'])


@api.route('/getuiunbind/')
class test4(Resource):
    @api.expect(test_parser)
    def post(self):
        args = test_parser.parse_args()
        userid = args['userid']
        cid = args['cid']
        return getui.unbind(userid, cid)


@api.route('/getuisend/')
class test2(Resource):
    @api.expect(test_parser1)
    def post(self):
        args = test_parser1.parse_args()
        list = []
        id = args['cid'].split(',')
        for i in id:
            list.append(str(i))
        alias = list
        taskid = args['taskid']
        return getui.sendList(alias, taskid)


@api.route('/gettaskid/')
class test3(Resource):
    @api.expect(test_parser2)
    def post(self):
        args = test_parser2.parse_args()
        useralarmrecord = UserAlarmRecord.query.get(args['useralarmrecord_id'])
        taskid = getui.getTaskId(useralarmrecord.id, useralarmrecord.content)
        return taskid, 200
#
# @api.route('/jpush/')
# class JPush(Resource):
#     def post(self):
#         push = Jpush.create_push()
#         push.audience = jpush.all_
#         push.notification = jpush.notification(alert="hello python jpush api")
#         push.platform = jpush.all_
#         try:
#             response = push.send()
#         except Exception as e:
#             print(e)
#
#
# @api.route('/jpush2/')
# class JPush2(Resource):
#     def post(self):
#         push = Jpush.create_push()
#         push.audience = jpush.all_
#         push.platform = jpush.all_
#         #ios = jpush.ios(alert="Hello, IOS JPush!", sound="a.caf", extras={'k1': 'v1'})
#         android = jpush.android(alert="Hello, Android msg", priority=1, style=1, alert_type=1, big_text='jjjjjjjjjj',
#                                 extras={'k1': 'v1'})
#         push.notification = jpush.notification(alert="Hello, JPush!", android=android)#,ios=ios)
#         try:
#             response = push.send()
#         except Exception as e:
#             print(e)
