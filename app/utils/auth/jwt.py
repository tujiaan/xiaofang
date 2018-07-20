import datetime

import jwt
from flask import current_app

pk_path = current_app.config.get('JWT_PK')
puk_path = current_app.config.get('JWT_PUK')

with open(pk_path) as f:
    pk = f.read()
with open(puk_path) as f:
    puk = f.read()


def encode_jwt(user_id=None,role_id=None, exp=None, nbf=None):
    now = datetime.datetime.utcnow()
    exp = exp or current_app.config.get('JWT_EXP', 300)
    nbf = nbf or current_app.config.get('JWT_NBF', 0)

    identity = {'user_id': user_id,'role_id':role_id, 'exp': now + datetime.timedelta(seconds=exp),
                'nbf': now - datetime.timedelta(seconds=nbf), 'iat': now}
    encoded_jwt = jwt.encode(identity, pk, algorithm='RS256').decode()
    return encoded_jwt


def decode_jwt(jwt_str):
    decoded_jwt = jwt.decode(jwt_str, puk, algorithms='RS256')
    return decoded_jwt
