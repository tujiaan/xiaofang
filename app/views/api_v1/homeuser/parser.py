from flask_restplus.reqparse import RequestParser


# homeuser_parser=RequestParser()
# homeuser_parser.add_argument('home_id',type=str,help='家庭id',required=True,location='form')



homeuser_parser1=RequestParser()
homeuser_parser1.add_argument('home_id',type=str,help='家庭id',required=True,location='form')
homeuser_parser1.add_argument('user_id',type=str,required=True,help='用户id',location='form')