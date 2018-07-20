import functools

from flask import request, g

from app.models import User
from .jwt import decode_jwt


def user_require(method):
    @functools.wraps(method)
    def warpper(*args, **kwargs):
        jwt_str = request.headers.get('jwt', None)
        g.user = None
        if jwt_str:
            try:
                identity = decode_jwt(jwt_str)
                g.user = User.query.get(identity['user_id']) if identity['user_id'] else None

            except Exception as e:
                print(e)
        else:return {'message':'请登录'},401
        if g.user is None:
            return {'message': '请注册'}, 401
        return method(*args, **kwargs)

    return warpper
