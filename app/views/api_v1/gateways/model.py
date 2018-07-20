from flask_restplus import Model, fields
from . import api
gateway_model = api.model('Gateway', {
    'id': fields.String,
     'home_id':fields.String,
    'useable':fields.Boolean


})