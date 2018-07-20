from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Role
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.roles.parser import roles_parser, roles_parser1

api=Namespace('Roles',description='角色相关操作')
from .models import *


@api.route('/')
class RolesView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @page_format(code=0, msg='ok')
    @api.doc('查询角色列表')
    @api.marshal_with(role_model, as_list=True)
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self):
        list=Role.query
        return list,200

    @api.doc('新建角色')
    @api.expect(roles_parser)
    @api.response(200,'ok')
    def post(self):
        args=roles_parser.parse_args()
        role=Role(**args)
        db.session.add(role)
        db.session.commit()
        return None,200


@api.route('/<roleid>')
class RoleView(Resource):
    @api.doc('删除角色')
    @api.response(200,'ok')
    def delete(self,roleid):
        role=Role.query.get_or_404(roleid)
        db.session.delete(role)
        db.session.commit()
        return None,200

    @api.doc('更新角色信息')
    @api.expect(roles_parser1)
    @api.response(200,'ok')
    def put(self,roleid):
     role=Role.query.get_or_404(roleid)
     args=roles_parser1.parse_args()
     if 'name'in args and args['name']:
         role.name=args['name']
     else:pass
     if 'disabled'in args and args['disabled']:
         role.disabled=args['disabled']
     else:pass
     if 'description'in args and  args['description']:
         role.description=args['description']
     else:pass
     db.session.commit()
     return None,200
