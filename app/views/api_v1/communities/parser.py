from flask_restplus.reqparse import RequestParser
from werkzeug.datastructures import FileStorage

community_parser = RequestParser()
community_parser.add_argument('name', type=str, help='社区名称', required=True, location='form')
community_parser.add_argument('detail_address', type=str, help='详细地址', required=True, location='form')
#community_parser.add_argument('ins_id',type=str,help='机构id',required=True,location='form')
community_parser.add_argument('longitude', type=float, help='社区经度', required=True, location='form')
community_parser.add_argument('latitude', type=float, help='社区纬度', required=True, location='form')
community_parser.add_argument('save_distance', type=int, help='求救距离', required=True, location='form')
community_parser.add_argument('eva_distance', type=int, help='疏散距离', required=True, location='form')
community_parser.add_argument('community_picture', type=FileStorage, help='社区图片', required=True, location='files')
community_parser.add_argument('location_id', type=str, help='位置id', required=True, location='form')

community_parser1 = RequestParser()
community_parser1.add_argument('name', type=str, help='社区名称', required=False, location='form')
community_parser1.add_argument('detail_address', type=str, help='详细地址', required=False, location='form')
#community_parser1.add_argument('ins_id',type=str,help='机构id',required=False,location='form')
community_parser1.add_argument('longitude',type=float,help='社区经度',required=False,location='form')
community_parser1.add_argument('latitude',type=float,help='社区纬度',required=False,location='form')
community_parser1.add_argument('save_distance',type=int,help='求救距离',required=False,location='form')
community_parser1.add_argument('eva_distance',type=int,help='疏散距离',required=False,location='form')
community_parser1.add_argument('community_picture',type=FileStorage,help='社区图片',required=False,location='files')
community_parser1.add_argument('location_id',type=str,help='位置id',required=False,location='form')
