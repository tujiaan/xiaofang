from flask_restplus.reqparse import RequestParser

sensoralarms_parser=RequestParser()
sensoralarms_parser.add_argument('sensor_id',type=str,help='传感器id',required=True,location='form')
sensoralarms_parser.add_argument('sensor_type',type=str,help='报警项目',required=True,location='form')
sensoralarms_parser.add_argument('alarm_value',type=str,help='报警值',required=True,location='form')
sensoralarms_parser.add_argument('alarm_time',type=str,help='报警时间',required=True,location='form')
sensoralarms_parser.add_argument('confirm_time',type=str,help='确认时间',required=True,location='form')
sensoralarms_parser.add_argument('is_timeout',type=str,help='是否超时',required=True,location='form')
sensoralarms_parser.add_argument('is_confirm',type=str,help='是否确认',required=True,location='form')
sensoralarms_parser.add_argument('user_id',type=str,help='用户id',required=True,location='form')


sensoralarms_parser1=RequestParser()
sensoralarms_parser1.add_argument('sensor_id',type=str,help='传感器id',required=False,location='form')
sensoralarms_parser1.add_argument('sensor_type',type=str,help='报警项目',required=False,location='form')
sensoralarms_parser1.add_argument('alarm_value',type=str,help='报警值',required=False,location='form')
sensoralarms_parser1.add_argument('alarm_time',type=str,help='报警时间',required=False,location='form')
sensoralarms_parser1.add_argument('confirm_time',type=str,help='确认时间',required=False,location='form')
sensoralarms_parser1.add_argument('is_timeout',type=str,help='是否超时',required=False,location='form')
sensoralarms_parser1.add_argument('is_confirm',type=str,help='是否确认',required=False,location='form')
sensoralarms_parser1.add_argument('user_id',type=str,help='用户id',required=False,location='form')
sensoralarms_parser1.add_argument('note',type=str,help='备注',required=False,location='form')


