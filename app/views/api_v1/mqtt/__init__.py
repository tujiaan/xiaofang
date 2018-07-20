import datetime

from flask import request, json
from flask_restplus import Namespace, Resource
from flask_restplus.reqparse import RequestParser
from app.ext import mqtt
api=Namespace('Mqtt',description='MQTT操作')
payload_parser=RequestParser()
payload_parser.add_argument('sensor_id', type=str,help='传感器id', required=True,location='form')
payload_parser.add_argument('order', type=int, help='指令', required=True, location='form')


@api.route('/<gatewayid>/')
class Command(Resource):
    @api.expect(payload_parser, validate=False)
    def post(self, gatewayid):
        args = payload_parser.parse_args()
        data = {'d': {
           args['sensor_id']: [args['order']]
        },
            'time': datetime.datetime.now()
        }
        theme = str(gatewayid)+'/cmd'
        mqtt.publish(theme, json.dumps(data))

        return None, 200