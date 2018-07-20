from flask_restplus import fields

from . import api


user_model = api.model('UserModel', {
    'id': fields.String,
    'disabled': fields.Boolean,
    'contract_tel': fields.String,
    'username': fields.String,
    'email': fields.String,
    'createTime': fields.DateTime,
    'lastTime': fields.DateTime,
    'real_name': fields.String
})

home_model = api.model('HomeModel', {
    'id': fields.String,
    'name': fields.String,
    'community_id': fields.String,
    'admin_user_id':fields.String,
    'detail_address': fields.String,
    'link_name': fields.String,
    'telephone': fields.String,
    'longitude': fields.Float,
    'latitude':fields.Float,
    'alternate_phone':fields.String
})
role_model=api.model('RoleModel',{
    'id':fields.String,
    'name':fields.String,
    'disabled':fields.Boolean,
    'description':fields.String

})
role_user_model=api.model('RoleUserModel',{
    'user_id':fields.String,
    'user_name':fields.String,
    'user_email':fields.String,
    'contract_tel':fields.String,
    'role_id':fields.String,
    'role_name':fields.String,
    'role_disable':fields.Boolean






})

