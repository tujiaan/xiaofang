from flask_restplus import fields

from app.views.api_v1.sensoralarms import api

sensoralarms_model=api.model('Sensoralarms',{
    'id':fields.String,
    'gateway_id':fields.String,
    'sensor_id':fields.String,
    'alarm_value':fields.String,
    'alarm_time':fields.DateTime,
    'is_timeout':fields.Boolean,
    'is_confirm':fields.Boolean,
    'note':fields.String,
    'sensor_type':fields.Integer,
    'var_type':fields.String,
    'unit':fields.String


})








