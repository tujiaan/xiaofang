import datetime

from flask_restplus import Model, fields
from . import api

sensor_model = api.model('SensorModel', {
    'id': fields.String,
    'gateway_id': fields.String,
    'sensor_type': fields.Integer,
    'sensor_place': fields.String,
    'home_id':fields.String,
    'max_value':fields.Float,
    'set_type':fields.String
})
sensortime_model=api.model('SensorTime',{
    'id':fields.String,
    'sensor_id':fields.String,
    'start_time':fields.String(attribute=lambda x: x.start_time.strftime('%H:%M')),
    'end_time':fields.String(attribute=lambda x: x.end_time.strftime('%H:%M'))
})