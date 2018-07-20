from flask_restplus import fields

from app.views.api_v1.roles import api

role_model=api.model('RoleModel',{
    'id':fields.String,
    'name':fields.String,
    'disabled':fields.Boolean,
    'description':fields.String

})