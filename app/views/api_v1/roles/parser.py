from flask_restplus.reqparse import RequestParser

roles_parser=RequestParser()
roles_parser.add_argument('name',type=str,help='角色名称',required=True,location='form')
roles_parser.add_argument( 'disabled',type=bool,help='是否可用',required=True,location='form')
roles_parser.add_argument('description',type=str,help='角色描述',required=True,location='form')
roles_parser1=RequestParser()
roles_parser1.add_argument('name',type=str,help='角色名称',required=False,location='form')
roles_parser1.add_argument( 'disabled',type=bool,help='是否可用',required=False,location='form')
roles_parser1.add_argument('description',type=str,help='角色描述',required=False,location='form')