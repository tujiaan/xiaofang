from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Gateway

from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.gateways.parser import gateway_parser
from app.views.api_v1.sensors import sensor_model

api = Namespace('Gateway', description='网关相关接口')
from .model import *


@api.route('/')
class GatewayView1(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin','superadmin'])
    @page_format(code=0,msg='ok')
    @api.doc('查询所有的网关')
    @api.marshal_with(gateway_model,as_list=True)
    @api.response(200,'ok')
    @api.doc(params={'page':'页数', 'limit': '数量'})
    @page_range()
    def get(self):
        list=Gateway.query
        return list,200

    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @api.doc('新增网关')
    @api.response(200, 'ok')
    @api.response(409, '重复')
    @api.marshal_with(gateway_model)
    @api.expect(gateway_parser)
    def post(self):
        args=gateway_parser.parse_args()
        gateway=Gateway(**args)
        db.session.add(gateway)
        db.session.commit()
        return gateway,200


@api.route('/<gatewayid>')
class GatewayView2(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @api.doc('删除网关')
    @api.response(200,'ok')
    @api.response(404, '记录不存在')
    def put(self,gatewayid):
        gateway=Gateway.query.get_or_404(gatewayid)
        gateway.useable=False
        db.session.commit()
        return None,200

    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'propertyuser', 'stationuser', '119user''admin', 'superadmin'])
    @api.doc('查询特定的网关')
    @api.marshal_with(gateway_model)
    @api.response(200, 'ok')
    def get(self, gatewayid):
        gateway = Gateway.query.get_or_404(gatewayid)
        return gateway

@api.route('/<gatewayid>/sensor')
class GatewayView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @page_format(code=0, msg='ok')
    @api.doc('查询网关下的传感器')
    @api.marshal_with(sensor_model, as_list=True)
    @api.response(200, 'ok')
    @page_range()
    def get(self, gatewayid):
        gateway = Gateway.query.get_or_404(gatewayid)
        return gateway.sensors,200









