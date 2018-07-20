from flask_restplus import fields

from app.views.api_v1.useralarms import api

useralarmrecord_model=api.model('UserAlarmRecord', {
    'id': fields.String,
    'type': fields.Integer,
    'content': fields.String,
    'time': fields.DateTime,
    'home_id': fields.String,
    'ins_id': fields.String,
    'user_id': fields.String,
    'note': fields.String,
    'reference_alarm_id': fields.String,
    'if_confirm': fields.Boolean


})


