from flask_restplus import Resource
from app.ext import db
from . import api


class InitDatabase(Resource):
    @api.doc('初始化数据库')
    def put(self):
        try:
            db.drop_all()
        except :
            pass
        db.create_all()
        return 'a'
