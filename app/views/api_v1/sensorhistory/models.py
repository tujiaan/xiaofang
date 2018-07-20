from flask_restplus import fields

from app.views.api_v1.sensorhistory import api

sensorhistory_model=api.model('SensorHistoryModel',{
    'id':fields.String,
    'sensor_id':fields.String,
    'sensor_state':fields.String,
    'time':fields.DateTime


})