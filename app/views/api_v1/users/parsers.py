from flask_restplus.reqparse import RequestParser

login_parser = RequestParser()
login_parser.add_argument('role_id', type=str, help='角色id', required=True, location='form')
login_parser.add_argument('password', type=str, help='用户名', required=True, location='form')
login_parser.add_argument('contract_tel', type=str, help='电话', required=True, location='form')
#login_parser.add_argument('cid', type=str, help='客户端id', required=False, location='form')

login_parser1 = RequestParser()
login_parser1.add_argument('role_id', type=str, help='角色id', required=True, location='form')


register_parser = RequestParser()
register_parser.add_argument('username', type=str, help='用户名', required=True, location='form')
register_parser.add_argument('password', type=str, help='密码', required=True, location='form')
register_parser.add_argument('contract_tel', type=str, help='电话号码', required=True, location='form')
register_parser.add_argument('email', type=str, help='邮箱', required=True, location='form')

password_parser = RequestParser()
password_parser.add_argument('old_password', type=str, help='原密码', required=True, location='form')
password_parser.add_argument('password', type=str, help='新密码', required=True, location='form')

telephone_parser = RequestParser()
telephone_parser.add_argument('old_contract_tel', type=str, help='原电话', required=True, location='form')
telephone_parser.add_argument('contract_tel', type=str, help='新电话', required=True, location='form')

email_parser = RequestParser()
email_parser.add_argument('old_email', type=str, help='原邮箱', required=True, location='form')
email_parser.add_argument('email', type=str, help='新邮箱', required=True, location='form')

username_parser=RequestParser()
username_parser.add_argument('old_username',type=str,help='原用户名',location='form')
username_parser.add_argument('username',type=str,help='新用户名',location='form')

user_parser=RequestParser()
user_parser.add_argument('username',type=str,help='用户名',required=False,location='form')
user_parser.add_argument('contract_tel',type=str,help='电话',required=False,location='form')
user_parser.add_argument('email',type=str,help='邮箱',required=False,location='form')
user_parser.add_argument('disabled',type=str,help='是否可用',required=False,location='form')

userpassword_parser=RequestParser()
userpassword_parser.add_argument('password',type=str,help='密码',required=True,location='form')

role_parser=RequestParser()
role_parser.add_argument('propertyuser',type=str,help='物业用户',required=False,location='form')
role_parser.add_argument('stationuser',type=str,help='消防站用户',required=False,location='form')
role_parser.add_argument('119user',type=str,help='119用户',required=False,location='form')
role_parser.add_argument('admin',type=str,help='平台管理员',required=False,location='form')
#role_parser.add_argument('superadmin',type=bool,help='超级管理员',required=False,location='form')
role_parser.add_argument('knowledgeadmin',type=str,help='知识管理员',required=False,location='form')