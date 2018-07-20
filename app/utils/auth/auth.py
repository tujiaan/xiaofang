import functools
import types

from flask import request, g
from flask.views import MethodView

from app.models import User, Role, UserRole
from app.utils.auth import decode_jwt


def role_function(r):
    def decorator(method):
        @functools.wraps(method)
        def warpper(*args, **kwargs):
            jwt_str = request.headers.get('jwt', None)
            g.user = None
            if jwt_str:
                try:
                    identity = decode_jwt(jwt_str)
                    g.user = User.query.get(identity['user_id']) if identity['user_id'] else None
                    g.role= Role.query.get(identity['role_id']) if identity['role_id'] else None

                except Exception as e:
                    print(e)

            if g.user is None:
                return {'message': '请登陆'}, 401
            if isinstance(r, list):
                roles = r
            else:
                roles = [r]
            r_list = []
            for role in roles:
                _ = Role.query.filter_by(name=role).first()
                _ and r_list.append(_)

            for i in r_list:
                if  i==g.role:
                    return method(*args, **kwargs)
            else:
                return {'message': '权限不足'}, 402

        return warpper

    return decorator


def role_require(r):
    def decorator(fuction_or_class):
        if isinstance(fuction_or_class, types.FunctionType):
            return role_function(r)(fuction_or_class)
        elif isinstance(fuction_or_class, type(MethodView)):
            for m in fuction_or_class.methods:
                setattr(fuction_or_class,
                m.lower(),#获取类下的方法并转小写
                role_function(r)(getattr(fuction_or_class, m.lower())))
                #@role functions（r）
                # def getattr(...)
            return fuction_or_class
        else:
            return fuction_or_class

    return decorator