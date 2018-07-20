import dateutil
from flask import g, request, json
from flask_restplus import Namespace, abort
from flask_restplus import  Resource
from sqlalchemy import and_, func

from app.ext import db, mqtt
from app.models import Facility, Sensor, Home, SensorAlarm, SensorHistory, HomeUser, UserRole, Role, User, SensorTime
from app.utils.auth.auth import role_require
#from app.utils.myutil.url import getResponse
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.sensoralarms import sensoralarms_model
from app.views.api_v1.sensorhistory import sensorhistory_model
from app.views.api_v1.sensors.parsers import sensor_parser, sensor_parser1, sensor_parser2, sensortime_parser
import datetime
import time

api = Namespace('Sensors', description='传感器相关接口')
from .model import *


@api.route('/')
class SensorsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'admin', 'superadmin'])
    @api.doc('查询传感器列表')
    @api.doc(params={'page': '页数', 'limit': '数量', 'sensor_type': '类型'})
    @api.response(200, 'ok')
    def get(self):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        sensor_type = request.args.get('sensor_type', None)
        homeuser = HomeUser.query.filter(HomeUser.user_id == g.user.id).all()
        home = Home.query.filter(Home.id.in_(i.home_id for i in homeuser)).all()
        if g.role.name == 'homeuser':
            if sensor_type:
                query = db.session.query(Sensor, Home).join(Home, Home.gateway_id == Sensor.gateway_id).\
                    filter(Sensor.sensor_type == sensor_type).filter(Sensor.online==True).filter(Sensor.gateway_id.in_(i.gateway_id for i in home)).order_by(Sensor.id)\
                    .offset((int(page) - 1) * limit).limit(limit)
            else:  query = db.session.query(Sensor,Home).join(Home,Home.gateway_id == Sensor.gateway_id).\
                  filter(Sensor.gateway_id.in_(i.gateway_id for i in home)).filter(Sensor.online==True).order_by(Sensor.id)\
                    .offset((int(page) - 1) * limit).limit(limit)
        else:
            if sensor_type:
                query = db.session.query(Sensor, Home).join(Home, Home.gateway_id == Sensor.gateway_id).\
                    filter(Sensor.sensor_type == sensor_type).filter(Sensor.online==True).order_by(Sensor.id).offset((int(page) - 1) * limit).limit(limit)
            else:     query = db.session.query(Sensor, Home).join(Home, Home.gateway_id == Sensor.gateway_id) \
                .filter(Sensor.online == True).order_by(Sensor.id).offset((int(page) - 1) * limit).limit(limit)
        total = Sensor.query.filter(Sensor.online==True).count()
        _ = []
        for i in query.all():
            __ = {}
            __['sensor_id'] = i[0].id
            __['sensor_type'] = i[0].sensor_type
            __['sensor_place'] = i[0].sensor_place
            __['gateway_id'] = i[0].gateway_id
            __['home_id'] = i[1].id
            __['home_name'] = i[1].name
            _.append(__)
        result = {
             'code': 0,
             'msg': '200',
             'count': total,
             'data': _
         }
        return result, 200

    @api.doc('新增传感器')
    @api.header('jwt', 'JSON Web Token')
    @role_require([])
    @api.response(200, 'ok')
    @api.expect(sensor_parser, validate=True)
    def post(self):
        # url = 'http://119.28.155.88:8080/data/api/v1/dataPoint/53/list'
        # result = getResponse(url)
        # list = result.get('data')
        # for i in list:
        #     name = i.get('name')
        #     str = name.split('-')
        #     sensor= Sensor(id=str[1],sensor_type=str[0])
        #     db.session.add(sensor)
        # db.session.commit()##########################################待修改
        return None,200


@api.route('/<sensorid>/')
class SensorsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'propertyuser', 'stationuser', '119user', 'admin', 'superadmin'])
    @api.doc('获取传感器详情')
    @api.response(200, 'ok')
    def get(self, sensorid):
        sensor = Sensor.query.filter(Sensor.id ==sensorid).filter(Sensor.online==True).first()
        if sensor:
            home = Home.query.filter(Home.gateway_id == sensor.gateway_id).filter(Home.disabled == False).first()
            user = User.query.filter(User.id == home.admin_user_id).filter(User.disabled == False).first()
            if home and user:
                homeuser = HomeUser.query.filter(HomeUser.home_id == home.id).all()

                _=[]
                __ = {}
                __['sensor_id'] = sensor.id
                __['sensor_type'] = sensor.sensor_type
                __['max_value'] = sensor.max_value
                __['set_type'] = sensor.set_type
                __['sensor_place'] = sensor.sensor_place
                __['sensor_state'] = tuple(SensorHistoryView.get(SensorTimeView, sensor.id))[0].get('sensor_state')
                __['gateway_id'] = sensor.gateway_id
                __['home_id'] = home.id
                __['home_name'] = home.name
                _.append(__)
                result = {
                    'code': 0,
                    'msg': 'ok',
                    'data': _
                }
                if user.sensor_visable==False:
                    if g.role.name =='homeuser':
                        if g.user.id not in [i.user_id for i in homeuser]:
                            return '权限不足', 201
                        else: return result, 200
                    elif g.role.name in['propertyuser', 'stationuser', '119user']:
                        return '权限不足', 201
                    else:return result, 200
                else:
                    if g.role.name == 'homeuser':
                        if g.user.id not in [i.user_id for i in homeuser]:
                            return '权限不足', 201
                        else:return result, 200
                    else:
                        return result, 200
            else: return '信息有误',201
        else:return '信息有误',201

    @api.doc('更新传感器信息')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    @api.response(200, 'ok')
    @api.expect(sensor_parser1)
    def put(self, sensorid):
        sensor1 = Sensor.query.filter(Sensor.id == sensorid).filter(Sensor.online ==True).first()
        if sensor1:
            home = Home.query.filter(Home.gateway_id == sensor1.gateway_id).first()
            args = sensor_parser1.parse_args()
            if args['gateway_id']:
                sensor1.gateway_id = args.get('gateway_id')
            else: pass
            if args['sensor_type']:
                 sensor1.sensor_type = args.get('sensor_type')
            else:pass
            if args['sensor_place']:
                sensor1.sensor_place = args.get('sensor_place')
            else:pass
            if args['home_id']:
                sensor1.home_id = args.get('home_id')
            else:
                pass
            if args['max_value']:
                sensor1.max_value = args.get('max_value')
                if sensor1.sensor_type == 3:
                    sensor1.set_type = '1'
                    data = {'d': {
                        sensor1.id: [int(args.get('max_value'))]
                    },
                        'time': datetime.datetime.now()
                    }
                    theme = str(sensor1.gateway_id) + '/config'
                    mqtt.publish(theme, json.dumps(data))
                   # print(data)
                else: pass
            else: pass
            if args['set_type']:
                sensor1.set_type = args['set_type']
            else:pass
            if g.user.id == home.admin_user_id:
                db.session.commit()
                return None, 200
            else:return '权限不足', 301
        else:return '传感器不存在',201


@api.route('/<sensorid>/sensoralarm')
class SensorAlarmsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'propertyuser', 'stationuser', '119user''admin', 'superadmin'])
    @page_format(code=0, msg='ok')
    @api.doc('查询传感器的报警历史')
    @api.marshal_with(sensoralarms_model, as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.response(200, 'ok')
    @page_range()
    def get(self, sensorid):
        sensor = Sensor.query.filter(Sensor.id == sensorid).filter(Sensor.online ==True).first()
        if sensor:
            home = Home.query.filter(Home.gateway_id == sensor.gateway_id).filter(Home.disabled == False).first()
            try:
                homeuser = HomeUser.query.filter(HomeUser.home_id == home.id).all()
                sensoralarm = SensorAlarm.query.filter(SensorAlarm.sensor_id == sensorid)
                if g.role.name == 'homeuser':
                    if g.user.id in [i.user_id for i in homeuser]:
                      return sensoralarm, 200
                    else:
                        pass
                elif g.role.name in ['119user', 'stationuser', 'propertyuser']:
                    return sensoralarm.filter(SensorAlarm.is_confirm == False).filter(SensorAlarm.is_timeout == True).\
                           filter(SensorAlarm.sensor_id == sensorid)
                else:
                    return sensoralarm, 200
            except: return None,201
        else: return '传感器不存在',201


@api.route('/<sensorid>/sensorhistory')
class SensorHistoryView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'insuser', '119user''admin', 'superadmin'])
    @api.doc('查询最近的一条传感器历史')
    @api.marshal_with(sensorhistory_model)
    @api.response(200, 'ok')
    def get(self, sensorid):
        sensor = Sensor.query.filter(Sensor.id==sensorid).filter(Sensor.online ==True).first()
        if sensor:
            home = Home.query.filter(Home.gateway_id == sensor.gateway_id).first()
            sensorhistory = SensorHistory.query.filter(SensorHistory.sensor_id == sensorid).\
                order_by(SensorHistory.time.desc()).first()
            if g.role.name == 'homeuser':
                if g.user.id in [i.user_id for i in (HomeUser.query.filter(HomeUser.home_id == home.id))]:
                    return sensorhistory, 200
                else:return '权限不足', 201
            else:
                return sensorhistory, 200
        else:return '暂无相关信息',201


@api.route('/<sensorid>/sensortime')
class SensorTimeView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    @api.doc('查询特定传感器定时')
    @api.marshal_with(sensortime_model, as_list=True)
    def get(self, sensorid):

        sensor = Sensor.query.filter(Sensor.id == sensorid).filter(Sensor.online == True).first()
        home = Home.query.filter(Home.gateway_id == sensor.gateway_id).filter(Home.disabled==False).first()
        if sensor and home:
            homeuser = HomeUser.query.filter(HomeUser.home_id == home.id).all()
            sensortime = SensorTime.query.filter(SensorTime.sensor_id == sensorid).all()
            if g.user.id in [i.user_id for i in homeuser]:
                return sensortime, 200
            else:return '权限不足', 201
        else:return '家庭不存在',201


@api.route('/<sensortimeid>/sensortime')
class SensorTimeView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    @api.doc('删除特定传感器定时')
    def delete(self, sensortimeid):
        sensortime = SensorTime.query.get_or_404(sensortimeid)
        sensor = Sensor.query.filter(Sensor.id==sensortime.sensor_id).filter(Sensor.online == True).first()
        home = Home.query.filter(Home.gateway_id == sensor.gateway_id).filter(Home.disabled == False).first()
        if home:
            db.session.delete(sensortime)
            if g.user.id == home.admin_user_id:
                db.session.commit()
                return '删除成功', 200
            else:return '权限不足', 201
        else:return '家庭不存在', 404

    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    @api.doc('开启定时传感器')
    @api.expect(sensortime_parser)
    def put(self, sensortimeid):
        sensortime = SensorTime.query.get_or_404(sensortimeid)
        sensor = Sensor.query.filter(Sensor.id==sensortime.sensor_id).filter(Sensor.online == True).first()
        home = Home.query.filter(Home.gateway_id == sensor.gateway_id).filter(Home.disabled == False).first()
        if home:
            args = sensortime_parser.parse_args()
            if args['switch_on']:
                sensortime.switch_on = args['switch_on']
            else:pass
            if g.user.id == home.admin_user_id:
                db.session.commit()
                return '开启成功', 200
            else: return '权限不足', 201
        else:return '家庭不存在', 404


@api.route('/sensortime/')
class SensorTimeView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'superadmin'])
    @api.doc('新增传感器定时')
    @api.expect(sensor_parser2)
    def post(self):
        args = sensor_parser2.parse_args()
        sensortime = SensorTime()
        if args['sensor_id']:
            sensor = Sensor.query.filter(Sensor.id==args['sensor_id']).filter(Sensor.online ==True).first()
            assert sensor!=None
            home = Home.query.filter(Home.gateway_id == sensor.gateway_id).first()
            sensortime.sensor_id = args['sensor_id']
        if args['start_time']:
            sensortime.start_time = args['start_time']
        else:pass
        if args['end_time']:
            sensortime.end_time = args['end_time']
        else:pass
        db.session.add(sensortime)
        if g.role.name == 'homeuser':
            if g.user.id == home.admin_user_id:
                db.session.commit()
                return '添加成功', 200
               # return {'start_time': str(sensortime.start_time), 'type': str(type(sensortime.start_time))}, 200
            else:
                return '权限不足', 201
        else:
            db.session.commit()
            return '添加成功', 200
            #return {'start_time': str(sensortime.start_time), 'type': str(type(sensortime.start_time))}, 200


@api.route('/<start_time>/<end_time>/<sensorid>/maxvalue')
class SensorTimeViews(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'superadmin'])
    @api.doc('智能电流设定')
    def get(self, start_time, end_time, sensorid):
        sensor = Sensor.query.filter(Sensor.id==sensorid).filter(Sensor.online==True).first()
        if sensor:
            sensorhistorys = SensorHistory.query.filter(SensorHistory.sensor_id == sensorid). \
                order_by(SensorHistory.sensor_value.desc()).all()
            if len(sensorhistorys) > 0:
                sensorhistory = None
                for i in sensorhistorys:
                    time = str(i.time.hour) + ":"+str(i.time.minute)
                    if start_time < time < end_time:
                        sensorhistory = i
                        break
                    else:
                        pass
                sensor.max_value = sensorhistory.sensor_value
                sensor.set_type = '2'
                db.session.commit()
                data = {'d': {
                    sensor.id: [int(sensor.max_value if sensor.max_value else 0)]
                },
                    'time': datetime.datetime.now()
                }
                theme = str(sensor.gateway_id) + '/config'
                mqtt.publish(theme, json.dumps(data))
                result = {
                    'start_time': start_time,
                    'end_time': end_time,
                    'max_value': sensorhistory.sensor_value
                    }
                return result, 200
            else:
                return {'start_time': start_time, 'end_time': end_time, 'max_value': None}, 201


        else:return None,201








