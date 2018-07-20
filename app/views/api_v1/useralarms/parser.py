from flask_restplus.reqparse import RequestParser

useralarmrecord_parser=RequestParser()
useralarmrecord_parser.add_argument('type',type=int,help='报警信息类型',required=True,location='form')
useralarmrecord_parser.add_argument('content',type=str,help='报警内容',required=False,location='form')
useralarmrecord_parser.add_argument('user_id',type=str,help='用户id',required=True,location='form')
useralarmrecord_parser.add_argument('home_id',type=str,help='家庭id',required=False,location='form')
useralarmrecord_parser.add_argument('ins_id',type=str,help='机构id',required=False,location='form')
useralarmrecord_parser.add_argument('reference_alarm_id',type=str,help='参考报警信息id',required=False,location='form')

useralarmrecord1_parser=RequestParser()
#useralarmrecord1_parser.add_argument('type',type=int,help='报警信息类型',required=False,location='form')
useralarmrecord1_parser.add_argument('note',type=str,help='报警备注',required=False,location='form')
#useralarmrecord1_parser.add_argument('user_id',type=str,help='用户id',required=False,location='form')
useralarmrecord1_parser.add_argument('reference_alarm_id',type=str,help='参考报警信息id',required=False,location='form')
useralarmrecord1_parser.add_argument('if_confirm',type=str,help='是否确认',required=False,location='form')
useralarmrecord2_parser=RequestParser()
useralarmrecord2_parser.add_argument('if_confirm',type=str,help='是否确认',required=False,location='form')



