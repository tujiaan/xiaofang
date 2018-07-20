from flask_restplus.reqparse import RequestParser
from werkzeug.datastructures import FileStorage

institutes_parser=RequestParser()
institutes_parser.add_argument('type',type=str,help='机构类型',required=True,location='form')
institutes_parser.add_argument('name',type=str,help='机构名称',required=True,location='form')
institutes_parser.add_argument('ins_picture',type=FileStorage,help='机构图片',required=False,location='files')
institutes_parser.add_argument('ins_address',type=str,help='机构地址',required=True,location='form')
institutes_parser.add_argument('note',type=str,help='备注',required=True,location='form')
institutes_parser.add_argument('admin_user_id',type=str,help='管理员id',required=True,location='form')
institutes_parser.add_argument('longitude',type=float,help='机构经度',required=True,location='form')
institutes_parser.add_argument('latitude',type=float,help='机构纬度',required=True,location='form')
institutes_parser.add_argument('admin_user_id',type=str,help='机构管理员id',required=True,location='form')
institutes_parser.add_argument('location_id',type=str,help='位置id',required=True,location='form')



institutes_parser1=RequestParser()
institutes_parser1.add_argument('type',type=str,help='机构类型',required=False,location='form')
institutes_parser1.add_argument('name',type=str,help='机构名称',required=False,location='form')
institutes_parser1.add_argument('ins_picture',type=FileStorage,help='机构图片',required=False,location='files')
institutes_parser1.add_argument('ins_address',type=str,help='机构地址',required=False,location='form')
institutes_parser1.add_argument('note',type=str,help='备注',required=False,location='form')
institutes_parser1.add_argument('admin_user_id',type=str,help='管理员id',required=False,location='form')
institutes_parser1.add_argument('longitude',type=float,help='机构经度',required=False,location='form')
institutes_parser1.add_argument('latitude',type=float,help='机构纬度',required=False,location='form')
institutes_parser1.add_argument('admin_user_id',type=str,help='机构管理员id',required=False,location='form')
institutes_parser1.add_argument('location_id',type=str,help='位置id',required=False,location='form')
