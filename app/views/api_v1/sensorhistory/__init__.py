
from flask import g
from flask_restplus import Namespace, Resource, abort

from app.models import SensorHistory, Sensor, Home, HomeUser, UserRole, Role
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_format, page_range

api = Namespace('SensorHistory', description='传感器历史相关接口')
from .models import *


@api.route('/')
class SensorHistoriesView(Resource):
    @page_format(code=0, msg='ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','propertyuser', 'stationuser', 'admin', 'superadmin'])
    @api.doc('查询所有传感器的历史')
    @api.marshal_with(sensorhistory_model, as_list=True)
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self):
        homeuser = HomeUser.query.filter(HomeUser.user_id == g.user.id).all()
        home = Home.query.filter(Home.id.in_(i.home_id for i in homeuser)).filter(Home.disabled == False).all()
        try:
            sensor = Sensor.query.filter(Sensor.gateway_id.in_(i.gateway_id for i in home)).filter(Sensor.online ==True).all()
            if g.role.name == 'homeuser':
                return SensorHistory.query.filter(SensorHistory.sensor_id.in_(i.id for i in sensor)), 200
            else: return SensorHistory.query, 200
        except: return None,201


@api.route('/<sensorid>')
class SensorHistoryView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','propertyuser', 'stationuser', 'admin', 'superadmin'])
    @page_format(code=0, msg='ok')
    @api.header('jwt', 'JSON Web Token')
    @api.marshal_with(sensorhistory_model, as_list=True)
    @api.doc('查询特定传感器的历史')
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self, sensorid):
            sensor = Sensor.query.filter(Sensor.id==sensorid).filter(Sensor.online == True).first()
            home = Home.query.filter(Home.gateway_id == sensor.gateway_id).filter(Home.disabled == False).first()
            try:
                sensorhistory = SensorHistory.query.filter(SensorHistory.sensor_id == sensorid)
                homeuser = HomeUser.query.filter(HomeUser.home_id == home.id).all()
                if g.role.name == 'homeuser':
                    if g.user.id in [i.user_id for i in homeuser]:
                        return sensorhistory, 200
                    else: pass
                else:
                    return sensorhistory, 200
            except:return None, 201




