from flask_restplus import Namespace

api = Namespace('Tool', description='工具类接口')

from .database import InitDatabase
api.add_resource(InitDatabase,'/init_database/')