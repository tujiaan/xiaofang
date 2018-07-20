from flask_restplus.reqparse import RequestParser

sensor_parser = RequestParser()
sensor_parser.add_argument('gateway_id', type=str, help='网关id', required=True, location='form')
sensor_parser.add_argument('sensor_type', type=str, help='传感器类型', required=True, location='form')
sensor_parser.add_argument('sensor_place', type=str, help='传感器位置', required=True, location='form')
sensor_parser.add_argument('home_id', type=str, help='家庭id', required=True, location='form')
sensor_parser.add_argument('start_time', type=str, help='开始时间', required=True, location='form')
sensor_parser.add_argument('end_time', type=str, help='结束时间', required=True, location='form')
sensor_parser.add_argument('max_value', type=float, help='最大值', required=True, location='form')





sensor_parser1 = RequestParser()
sensor_parser1.add_argument('gateway_id', type=str, help='网关id', required=False, location='form')
sensor_parser1.add_argument('sensor_type', type=str, help='传感器类型', required=False, location='form')
sensor_parser1.add_argument('sensor_place', type=str, help='传感器位置', required=False, location='form')
sensor_parser1.add_argument('home_id', type=str, help='家庭id', required=False, location='form')
sensor_parser1.add_argument('max_value', type=float, help='最大值', required=False, location='form')
sensor_parser1.add_argument('set_type',type=str,help='设定类型',required=False,location='form')

sensor_parser2= RequestParser()
sensor_parser2.add_argument('sensor_id',type=str,help='传感器id',required=True,location='form')
sensor_parser2.add_argument('start_time',type=str,help='开启时间',required=True,location='form')
sensor_parser2.add_argument('end_time',type=str,help='关闭时间',required=True,location='form')


sensortime_parser=RequestParser()
sensortime_parser.add_argument('switch_on',type=str,required=False,location='form')
