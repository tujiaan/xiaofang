from flask_restplus.reqparse import RequestParser

from werkzeug.datastructures import FileStorage


facility_parser=RequestParser()
facility_parser.add_argument('facility_id' , type=str, help='设施id', required=True, location='form' )
facility_parser.add_argument('ins_id' , type=str, help='机构id', required=True, location='form' )
facility_parser.add_argument('count' , type=int,help='设施数量', required=True, location='form' )
facility_parser.add_argument('expire_time', type=str, help='过期日期', required=True, location='form' )
facility_parser.add_argument('note', type=str, help='备注', required=True, location='form' )



facility_parser1=RequestParser()
#facility_parser1.add_argument('facility_id' , type=str, help='设施id', required=True, location='form' )
facility_parser1.add_argument('ins_id' , type=str, help='机构id', required=False, location='form' )
facility_parser1.add_argument('count' , type=int,help='设施数量', required=False, location='form' )
facility_parser1.add_argument('expire_time', type=str, help='过期日期', required=False, location='form' )

f_parser = RequestParser()

f_parser.add_argument('facility_name', type=str, help='设施名', required=True, location='form')
f_parser.add_argument('note', type=str, help='备注', required=True, location='form')
f_parser.add_argument('facility_picture', type=FileStorage, help='设施图片', required=True, location='files')

f1_parser = RequestParser()
f1_parser.add_argument('facility_name', type=str, help='设施名', required=False, location='form')
f1_parser.add_argument('note', type=str, help='备注', required=False, location='form')
f1_parser.add_argument('facility_picture', type=FileStorage, help='设施图片', required=False, location='files')
