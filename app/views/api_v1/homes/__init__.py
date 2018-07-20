import datetime
from flask import request, g
from flask_restplus import Namespace, Resource, abort
from sqlalchemy import and_, null
from app.ext import db
from app.models import Home, Ins, User, HomeUser, Sensor, SensorHistory, UserRole, Role, Community, Gateway
from app.utils.auth import decode_jwt, user_require
from app.utils.auth.auth import role_require
from app.utils.scheduler.test import getDistance
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.gateways import gateway_model
from app.views.api_v1.homes.parser import home_parser, home_parser1
from app.views.api_v1.users import user_model
import math

api = Namespace('Home', description='家庭相关接口')
from.model import *


@api.route('/')
class HomesView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'homeuser', 'superadmin'])
    @api.doc('查询家庭列表')
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    def get(self):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        list = Home.query.filter(Home.disabled == False)
        total = list.count()
        homeuser = HomeUser.query.filter(HomeUser.user_id == g.user.id)
        if g.role.name == 'homeuser':
           query = list.filter(g.user.id.in_(homeuser.user_id))
        else: query = list
        query1 = query.order_by(Home.id).offset((int(page) - 1) * limit).limit(limit)

        _ = []
        for i in query1.all():
            __={}
            __['home_id'] = i.id
            __['home_name'] = i.name
            __['community_id'] = i.community_id
            __['community_name'] = Community.query.filter(Community.id == i.community_id).filter(Community.disabled == False).first().name
            __['detail_address'] = i.detail_address
            __['link_name'] = i.link_name
            __['tephone'] = i.telephone
            __['longitude'] = str(i.longitude)
            __['latitude'] = str(i.latitude)
            __['gateway_id'] = i.gateway_id
            __['alternate_phone'] = i.alternate_phone
            __['admin_user_id'] = i.admin_user_id
            __['admin_name'] = User.query.filter(User.disabled == False).filter(User.id == i.admin_user_id).first().username
            _.append(__)
        result = {
            'code': 0,
            'msg': 'ok',
            'count': total,
            'data': _
        }
        return result, 200

    @api.doc('新增家庭')
    @api.expect(home_parser)
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    def post(self):
        args = home_parser.parse_args()
        home = Home(**args)
        if g.user.contract_tel != args.get('telephone'):
            return '联系方式与该用户号码不一致', 200
        elif home.gateway_id in [i.gateway_id for i in Home.query.all()]:
            return '网关被占用', 201
        else:
            db.session.add(home)
            db.session.commit()
            homeuser = HomeUser()
            homeuser.if_confirm = True
            homeuser.home_id = home.id
            homeuser.user_id = g.user.id
            homeuser.confirm_time = datetime.datetime.now()
            db.session.add(homeuser)
            db.session.commit()
            gateway = Gateway.query.get_or_404(args['gateway_id'])
            gateway.home_id = home.id
            gateway.useable = True
            db.session.commit()
            return '创建成功', 201


@api.route('/<homeid>')
class HomeView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'propertyuser', 'stationuser', '119user', 'admin', 'superadmin'])
    @api.doc('根据家庭id查找家庭')
    @api.marshal_with(home_model)
    @api.response(200, 'ok')
    def get(self, homeid):
        home = Home.query.filter(Home.id == homeid).filter(Home.disabled == False).first()
        if home:
            homeuser = HomeUser.query.filter(HomeUser.home_id == homeid).all()
            if g.role.name == 'homeuser':
                if g.user.id in [i.user_id for i in homeuser]:
                    return home, 200
                else: return '权限不足', 201
            else: return home, 200
        else: return '家庭不存在', 201

    @api.doc('根据家庭id删除家庭')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'admin', 'superadmin'])
    @api.response(200, 'ok')
    def delete(self, homeid):
        home = Home.query.filter(Home.id == homeid).filter(Home.disabled == False).first()
        if home:
            gateway = Gateway.query.filter(Gateway.home_id == homeid).filter(Gateway.useable == True).first()
            gateway.useable = True
            gateway.home_id = None
            home.gateway_id = None
            home.disabled = True
            if g.role.name in ['admin', 'superadmin']:
                db.session.commit()
                return None, 200
            elif home.admin_user_id == g.user.id:
               db.session.commit()
               return None, 200
            else: return '权限不足', 200
        else:return '家庭不存在', 201

    @api.doc('根据家庭id更新家庭')
    @api.expect(home_parser1, validate=True)
    @api.marshal_with(home_model)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'admin', 'superadmin'])
    @api.response(200, 'ok')
    def put(self, homeid):
        args = home_parser1.parse_args()
        home1 = Home(**args)
        home = Home.query.filter(Home.disabled == False).filter(Home.id == homeid).first()
        if home:
            if home.admin_user_id == g.user.id or g.role.name in['admin', 'superadmin']:
                if home1.admin_user_id:
                    home.admin_user_id = home1.admin_user_id
                else:pass
                if home1.detail_address:
                    home.detail_address = home1.detail_address
                if home1.alternate_phone:
                    home.alternate_phone = home1.alternate_phone
                else:pass
                if home1.gateway_id:
                    home.gateway_id = home1.gateway_id
                else:pass
                if home1.community:
                    home.community = home1.community
                else:pass
                if home1.community_id:
                 home.community_id = home1.community_id
                else:pass
                if home1.latitude:
                 home.latitude = home1.latitude
                else:pass
                if home1.longitude:
                 home.longitude = home1.longitude
                else:pass
                if home1.link_name:
                 home.link_name = home1.link_name
                else:pass
                if home1.telephone:
                    home.telephone = home1.telephone
                else:pass
                if home1.name:
                 home.name = home1.name
                else:pass
                if home1.admin_user_id:
                    if g.role.name in ['admin', 'superadmin']:
                     home.admin_user_id = home1.admin_user_id
                db.session.commit()
                return home, 200
            else: return '权限不足', 200
        else:return '家庭不存在', 201


@api.route('/<homeid>/gateway/')
class HomeGatewayView(Resource):
    @api.doc('查询家庭网关的状态')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'admin', 'superadmin'])
    def get(self, homeid):
        home = Home.query.filter(Home.id == homeid).filter(Home.disabled == False).first()
        if home:
            gateway = Gateway.query.filter(Gateway.home_id == homeid).first()
        else:return '家庭不存在', 201
        if gateway:
            if g.role.name == 'homeuser':
                if g.user.id in (i.user_id for i in (HomeUser.query.filter(HomeUser.home_id==homeid).all())):
                    return gateway.useable, 200
                else:return '权限不足', 201
            else:return gateway.useable, 200
        else:return '家庭尚未绑定网关', 201


@api.route('/<homeid>/<gatewayid>')
class HomeGatewayView(Resource):
    @api.doc('更改家庭绑定网关')
    @api.response(200, 'ok')
    @api.marshal_with(home_model)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'admin', 'superadmin'])
    def post(self, homeid, gatewayid):
        home = Home.query.filter(Home.disabled == False).filter(Home.id == homeid).first()
        g1 = Gateway.query.filter(Gateway.home_id==homeid).filter(Gateway.useable==True).first()
        gateway=Gateway.query.filter(Gateway.id==gatewayid).filter(Gateway.useable==True).first()
        if home and gateway:
            if g.role.name == 'homeuser'and g.user.id != home.admin_user_id:
                return '权限不足', 301
            else:
                if g1:
                    g1.home_id=None
                else:pass
                home.gateway_id = gatewayid
                gateway.home_id=homeid
                db.session.commit()
                return home, 200
        else:return None,201

    @api.doc('删除家庭的网关')#############################可能有问题
    @api.response(200, 'ok')
    @role_require(['homeuser', 'admin', 'superadmin'])
    @api.header('jwt', 'JSON Web Token')
    def delete(self, homeid, gatewayid):
        home = Home.query.filter(Home.id==homeid).filter(Home.disabled==False).first()
        gateway = Gateway.query.filter_by(id=gatewayid).first()
        home.disabled=True
        home.gateway_id=None
        gateway.home_id=None
        if g.role.name == 'homeuser' and g.user.id != home.admin_user_id:
            return '权限不足', 301
        else:
            db.session.delete(home)
            db.session.commit()
            return None, 200


@api.route('/<homeid>/users')
class HomeUsersView(Resource):
    @role_require(['homeuser', 'propertyuser', 'stationuser', '119user', 'admin', 'superadmin'])
    @page_format(code=0, msg='ok')
    @api.doc('查找家庭下的所有用户')
    @api.header('jwt', 'JSON Web Token')
    @api.response(401, '权限不足')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.marshal_with(user_model, as_list=True)
    @page_range()
    def get(self, homeid):
        home = Home.query.filter(Home.id == homeid).filter(Home.disabled == False).first()
        try:
            homeuser = HomeUser.query.filter(HomeUser.home_id == homeid).all()
            return User.query.filter(User.id.in_(i.user_id for i in homeuser)), 200
        except:return None,201

    @api.doc('用户退出家庭')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    def delete(self, homeid):
        home = Home.query.filter(Home.id == homeid).filter(Home.disabled==False).first()
        user = g.user
        if home:
            homeuser = HomeUser.query.filter(and_(HomeUser.home_id == home.id, HomeUser.user_id == user.id)).first()
            if homeuser:
                db.session.delete(homeuser)
                db.session.commit()
                return '退出家庭成功', 200

            else:return '不是该家庭成员', 301
        else: return '家庭不存在', 201


@api.route('/<homeid>/<distance>/ins')
class HomeInsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'admin', 'superadmin'])
    @api.doc('查询家庭附近的机构')
    @api.response(200, 'ok')
    def get(self, homeid, distance):
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        home = Home.query.filter(Home.id == homeid).filter(Home.disabled == False).first()
        if home:
            homeuser = HomeUser.query.filter(HomeUser.user_id == g.user.id).all()

            def getDistance(lat0, lng0, lat1, lng1):
                lat0 = math.radians(lat0)
                lat1 = math.radians(lat1)
                lng0 = math.radians(lng0)
                lng1 = math.radians(lng1)

                dlng = math.fabs(lng0 - lng1)
                dlat = math.fabs(lat0 - lat1)
                a = math.sin(dlat / 2) ** 2 + math.cos(lat0) * math.cos(lat1) * math.sin(dlng / 2) ** 2
                c = 2 * math.asin(math.sqrt(a))
                r = 6371  # 地球平均半径，单位为公里
                return c * r * 1000
            query = Ins.query
            total = query.count()
            query = query.offset((int(page) - 1) * limit).limit(limit)
            _ = []
            for i in tuple(query.all()):
                __ = {}
                __['ins_id'] = i.id
                __['ins_longitude'] = str(i.longitude)
                __['ins_latitude'] = str(i.latitude)
                __['ins_type'] = i.type
                __['ins_name'] = i.name
                __['distance'] = round(getDistance(i.latitude, i.longitude, home.latitude, home.longitude))
                if getDistance(i.latitude, i.longitude, home.latitude, home.longitude) < float(distance):
                  _.append(__)
            result = {
                'code': 0,
                'msg': '200',
                'count': total,
                'data': _
            }
            if homeid in [i.home_id for i in homeuser] or g.role.name in ['admin', 'superadmin']:
                    return result, 200
            else:return '权限不足', 201
        else:return '家庭不存在', 201


@api.route('/<homeid>/ins/')
class HomeInsView8(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'stationuser','propertyuser','119user','admin', 'superadmin'])
    @api.doc('查询家庭附近的机构')
    @api.response(200, 'ok')
    def get(self,homeid):
        home=Home.query.filter(Home.id == homeid).filter(Home.disabled == False).first()
        if home:
            ins=Ins.query.filter(Ins.disabled==False).all()
            total=len(ins)
            _=[]
            for i in ins:
                __ = {}
                __['ins_id'] = i.id
                __['ins_longitude'] = str(i.longitude)
                __['ins_latitude'] = str(i.latitude)
                __['ins_type'] = i.type
                __['ins_name'] = i.name
                __['distance'] = round(getDistance(i.latitude, i.longitude, home.latitude, home.longitude))
                _.append(__)
            return {
                'code': 0,
                'msg': '200',
                'count': total,
                'data': _
            },200
        else:return '家庭不存在',201




@api.route('/<homeid>/sensors')
class HomeSensorView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', '119user', 'propertyuser', 'stationuser', 'admin', 'superadmin'])
    @api.doc('查询家中的传感器')
    def get(self, homeid):
        home = Home.query.filter(Home.id == homeid).filter(Home.disabled == False).first()
        if home:
            homeuser = HomeUser.query.filter(HomeUser.home_id == homeid).all()
            if g.role.name =='homeuser':
                if g.user.id in [i.user_id for i in homeuser]:
                    query = Sensor.query.filter(Sensor.gateway_id == home.gateway_id).filter(Sensor.online ==True)
                else:pass
            else:
                query = Sensor.query.filter(Sensor.online ==True)
            _ = []
            total = Sensor.query.count()
            for i in query.all():
                __={}
                __['sensor_id'] = i.id
                __['sensor_place'] = i.sensor_place
                __['sensor_type'] = i.sensor_type
                sensorhistory = SensorHistory.query.filter(SensorHistory.sensor_id == i.id).order_by(SensorHistory.time.desc()).first()
                if sensorhistory:
                 __['state'] = sensorhistory.sensor_state
                _.append(__)
            result = {
                'code': 0,
                'msg': 'ok',
                'total': total,
                'data': _
             }
            return result, 200
        else:return '家庭不存在', 201


@api.route('/applies/')
class HomeApplyView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    @api.doc('显示自己家庭申请')
    @api.response(200, 'ok')
    @user_require
    def get(self):
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        query = db.session.query(User, Home).join(HomeUser, User.id == HomeUser.user_id).\
            filter(HomeUser.if_confirm == False).join(Home, HomeUser.home_id == Home.id)\
            .filter(Home.admin_user_id == g.user.id).order_by(Home.id)
        total = query.count()
        query = query.offset((int(page) - 1) * limit).limit(limit)
        _ = []
        for i in query.all():
            __ = {}
            __['user_id'] = i[0].id
            __['contract_tel'] = i[0].contract_tel
            __['user_name'] = i[0].username
            __['home_id'] = i[1].id
            __['home_name'] = i[1].name

            _.append(__)
        result = {
            'code': 200,
            'msg': 'ok',
            'count': total,
            'data': _
        }
        return result


# @api.route('/<id>/ifhome')
# class IfHome(Resource):
#     def ifhomeid(id):
#         home = Home.query.filter(Home.id == id).filter(Home.disabled == False).first()
#         if home:
#             return True
#         else: return False


