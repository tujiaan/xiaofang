from flask_restplus.reqparse import RequestParser

gateway_parser=RequestParser()
gateway_parser.add_argument('id',type=str,help='网关id',required=True,location='form')
gateway_parser.add_argument('useable',type=bool,help='是否可用',required=True,location='form')
gateway_parser.add_argument('home_id',type=str,help='家庭id',required=False,location='form')

