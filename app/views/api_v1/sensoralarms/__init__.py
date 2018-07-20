import datetime

from flask import g, request
from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import SensorAlarm, Home, Community, HomeUser, UserRole, Role, Sensor, AlarmHandle
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.sensoralarms.parser import sensoralarms_parser, sensoralarms_parser1

api=Namespace('Sensoralarms',description='传感器报警相关操作')
from .models import *


@api.route('/')
class SensorAlarmsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'propertyuser', 'stationuser', 'admin', 'superadmin'])
    @api.doc('查询传感器报警记录列表')
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量', 'start': '开始时间见', 'end': '结束时间', 'type': '传感器类型'})
    def get(self):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        start = request.args.get('star', 2018-1-1)
        end = request.args.get('end', datetime.datetime.now())
        type = request.args.get('type', None)
        homeuser = HomeUser.query.filter(HomeUser.user_id == g.user.id).all()
        home = Home.query.filter(Home.id.in_(i.home_id for i in homeuser)).filter(Home.disabled == False).all()
        if home or g.role.name in['propertyuser', 'stationuser', 'admin', 'superadmin']:
            sensors = Sensor.query.filter(Sensor.gateway_id.in_(i.gateway_id for i in home)).all()
            if g.role.name == 'homeuser':
                if type:
                    query = db.session.query(SensorAlarm) .filter(SensorAlarm.alarm_time.between(start, end))\
                        .filter(SensorAlarm.sensor_type == type).filter(SensorAlarm.sensor_id.in_(i.id for i in sensors)).\
                        order_by(SensorAlarm.id).offset((int(page) - 1) * limit).limit(limit)
                else:query = db.session.query(SensorAlarm) .filter(SensorAlarm.alarm_time.between(start, end))\
                        .filter(SensorAlarm.sensor_id.in_(i.id for i in sensors)).\
                        order_by(SensorAlarm.id).offset((int(page) - 1) * limit).limit(limit)
            else:
                if type:
                    query = db.session.query(SensorAlarm) .filter(SensorAlarm.alarm_time.between(start,end)).filter(SensorAlarm.sensor_type==type)\
                        .order_by(SensorAlarm.id).offset((int(page) - 1) * limit).limit(limit)
                else:
                    query = db.session.query(SensorAlarm) .filter(SensorAlarm.alarm_time.between(start, end))\
                        .order_by(SensorAlarm.id).offset((int(page) - 1) * limit).limit(limit)

            total = SensorAlarm.query.count()
            _=[]
            for i in query.all():
             sensor = Sensor.query.get_or_404(i.sensor_id)
             home = Home.query.filter(Home.gateway_id == sensor.gateway_id).filter(Home.disabled==False).first()
             __={}
             __['sensoralarms_id'] = i.id
             __['sensoralarms_sensor_id'] = i.sensor_id
             __['sensoralarms_sensor_type'] = i.sensor_type
             __['sensoralarms_alarm_value'] = i.alarm_value
             __['sensoralarms_note'] = i.note
             if home:
                 __['home_name'] = home.name
                 __['home_id'] = home.id
                 __['home_admin_id'] = home.admin_user_id
                 __['detail_address'] = home.detail_address
                 __['community_name'] = home.community.name
             __['sensoralarm_is_confirm'] = i.is_confirm
             __['sensoralarms_alarm_time'] = str(i.alarm_time)
             _.append(__)
            result = {
                'code': 0,
                'msg': 'ok',
                'count': total,
                'data': _
            }
            return result, 200
        else:return '家庭不存在', 201

    @api.doc('新增传感器报警记录')
    @api.header('jwt', 'JSON Web Token')
    @role_require([])
    @api.expect(sensoralarms_parser)
    @api.response(200, 'ok')
    def post(self):
     args = sensoralarms_parser.parse_args()
     sensoralarm = SensorAlarm(**args)
     db.session.add(sensoralarm)
     db.session.commit()
     return None, 200


@api.route('/<sensoralarmid>')
class SensorAlarmView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'propertyuser', 'stationuser', '119user', 'admin', 'superadmin'])
    @api.doc('根据报id查询详情')
    @api.marshal_with(sensoralarms_model)
    @api.response(200, 'ok')
    @api.response(404, 'Not Found')
    def get(self, sensoralarmid):
        sensoralarm = SensorAlarm.query.filter_by(id=sensoralarmid).order_by(SensorAlarm.alarm_time.desc()).first()
        sensor = sensoralarm.sensor
        home = Home.query.filter(Home.gateway_id == sensor.gateway_id).filter(Home.disabled == False).first()
        if home:
            homeuser = HomeUser.query.filter(HomeUser.home_id == home.id).all()
            if g.role.name == 'homeuser':
                if g.user.id not in[i.user_id for i in homeuser]:
                    return '权限不足', 301
                else: return sensoralarm, 200
            else: return sensoralarm, 200
        else: return '家庭不存在', 201

    @api.doc('删除报警记录')
    @api.header('jwt', 'JSON Web Token')
    @role_require([])
    @api.response(200, 'ok')
    def delete(self, sensoralarmid):
        sensoralarm = SensorAlarm.query.get_or_404(sensoralarmid)
        db.session.delete(sensoralarm)
        db.session.commit()
        return None, 200

    @api.doc('更新传感器的报警记录')
    @api.expect(sensoralarms_parser1, validate=True)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', '119user', 'admin', 'superadmin'])
    @api.response(200, 'ok')
    def put(self, sensoralarmid):
        sensoralarm = SensorAlarm.query.get_or_404(sensoralarmid)
        args = sensoralarms_parser1.parse_args()
        if args['note']:
            sensoralarm.note = args['note']
        else:pass
        if g.role.name == 'homeuser':
            home = Home.query.filter(Home.disabled == False).filter(Home.gateway_id == sensoralarm.gateway_id).first()
            if home:
                if home.admin_user_id == g.user.id:
                    sensoralarm.is_confirm = True
                    db.session.commit()
                    return None, 200
                else: return '权限不足', 301
            else:pass
        else:
            sensoralarm.is_confirm = True
            db.session.commit()
        alarmhandle = AlarmHandle(type='0', handle_type='203', handle_time=datetime.datetime.now(), user_id=g.user.id, note=args['note'])
        db.session.add(alarmhandle)
        db.session.commit()
        return None, 200

    @api.doc('发送报警')
    @api.expect(sensoralarms_parser1, validate=True)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', '119user', 'admin', 'superadmin'])
    @api.response(200, 'ok')
    def post(self):
        pass







