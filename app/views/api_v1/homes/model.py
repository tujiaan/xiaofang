from flask_restplus import fields
from . import api

home_model = api.model('HomeModel', {
    'id': fields.String,
    'name': fields.String,
    'community_id': fields.String,

    'detail_address': fields.String,
    'link_name': fields.String,
    'telephone': fields.String,
    'longitude': fields.Float,
    'latitude':fields.Float,
    'gateway_id':fields.String,
    'alternate_phone':fields.String,
    'admin_user_id':fields.String
})
home_apply_view=api.model('HomeApplyModel',{
    'user_id':fields.String,
    'user_name':fields.String,
    'contract_tel':fields.String,
    'home_name':fields.String,
    'home_id':fields.String
})