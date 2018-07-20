from flask import g, request
from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Ins, User, FacilityIns, UserRole, Role, Location, UserAlarmRecord
from app.utils.auth import user_require
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.utils.tools.upload_file import upload_file
from app.views.api_v1.institutes.parser import institutes_parser, institutes_parser1
from app.views.api_v1.homes import *
import math

from app.views.api_v1.useralarms import useralarmrecord_model

api = Namespace('Institutes', description='组织相关接口')

from .model import *


@api.route('/')
class InstitutesViews(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','admin', 'superadmin', 'propertyuser', 'stationuser', '119user'])
    @api.doc('查询所有机构列表')
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    def get(self):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        list = Ins.query.filter(Ins.disabled == False)
        total = list.count()
        if g.role.name in ['propertyuser', 'stationuser', 'admin', '119user', 'superadmin']:
           query=list
        else:
            query = list.filter(Ins.admin_user_id == g.user.id)
        query = query.order_by(Ins.id).offset((page - 1) * limit).limit(limit)
        _ = []
        for i in query.all():
            __={}
            __['ins_id'] = i.id
            __['ins_type'] = i.type
            __['ins_name'] = i.name
            __['ins_picture'] = i.ins_picture
            __['location_id'] = i.location_id
            __['location_district'] = Location.query.get_or_404(i.location_id).district
            __['ins_address'] = i.ins_address
            __['ins_note'] = i.note
            __['longitude'] = str(i.longitude)
            __['latitude'] = str(i.latitude)
            __['admin_user_id'] = i.admin_user_id
            __['admin_name'] = User.query.filter(User.id == i.admin_user_id).filter(User.disabled == False).first().username
            __['admin_contract_tel'] = User.query.filter(User.id == i.admin_user_id).filter(User.disabled == False).first().contract_tel
            _.append(__)
        result = {
            'code': 0,
            'msg': 'ok',
            'count': total,
            'data': _
        }
        return result, 200

    @api.doc('新增机构')
    @api.expect(institutes_parser, validate=True)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @api.response(200, 'ok')
    @user_require
    def post(self):
        args = institutes_parser.parse_args()
        institute = Ins()
        user = User.query.filter(User.id == args['admin_user_id']).filter(User.disabled == False).first()
        if user:
            user_role = UserRole.query.filter(UserRole.user_id == user.id).all()
            roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
            if not Ins.query.filter(and_(Ins.latitude == args['latitude'], Ins.longitude == args['longitude'])).first():
                institute.name = args['name']
                if 'propertyuser' in [i.name for i in roles] or 'stationuser'in [i.name for i in roles]:
                    institute.admin_user_id = args['admin_user_id']
                else:institute.admin_user_id = g.user.id
                institute.type = args['type']
                institute.ins_address = args['ins_address']
                institute.note = args['note']
                institute.latitude = args['latitude']
                institute.longitude = args['longitude']
                institute.ins_address = args['ins_address']
                if args['ins_picture']:
                    institute.ins_picture = upload_file(args['ins_picture'])
                else:institute.ins_picture = '/static/upload/20180601/094457fault.jpg'
                institute.location_id = args['location_id']
                db.session.add(institute)
                institute.user.append(user)
                db.session.commit()
                return '创建成功', 200
            else:return '机构位置已被占用', 201
        else: return'输入的用户不存在', 201


@api.route('/list/')
class InsList(Resource):
    @api.doc('查询所有机构列表')
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    def get(self):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        lst = Ins.query.filter(Ins.disabled == False).order_by(Ins.id).offset((page - 1) * limit).limit(limit).all()
        total = len(lst)
        _=[]
        for i in lst:
            __ = {}
            __['ins_id'] = i.id
            __['ins_type'] = i.type
            __['ins_name'] = i.name
            __['longitude'] = str(i.longitude)
            __['latitude'] = str(i.latitude)
            _.append(__)
        result = {
            'code': 0,
            'msg': 'ok',
            'count': total,
            'data': _
        }
        return result, 200


@api.route('/<insid>/')
class InstituteView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'propertyuser', '119user', 'stationuser', 'admin', 'superadmin'])
    @api.doc('根据机构id查询机构')
    @api.response(200, 'ok')
    def get(self, insid):
        ins = Ins.query.filter(Ins.disabled == False).filter(Ins.id == insid).first()
        if ins:
            instute = {
                'ins_id': ins.id,
                'ins_admin': ins.admin_user_id,
                'admin_name': User.query.filter(User.disabled == False).filter(User.id == ins.admin_user_id).first().username,
                'admin_tel': User.query.filter(User.disabled == False).filter(User.id == ins.admin_user_id).first().contract_tel,
                'type': ins.type,
                'ins_name': ins.name,
                'ins_picture': ins.ins_picture,
                'ins_address': ins.ins_address,
                'location_id': ins.location_id,
                'location_district': Location.query.get_or_404(ins.location_id).district,
                'longitude': str(ins.longitude),
                'latitude': str(ins.latitude),
                'note': ins.note
            }
            # if g.role.name in ['propertyuser','stationuser']:
            #     if ins.admin_user_id!=g.user.id:
            #         return '权限不足',201
            #     else: return instute,200
            # else:
            return instute, 200
        else:return '机构不存在', 201

    @api.doc('根据id更新机构信息')
    @api.expect(institutes_parser1)
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser', 'stationuser', 'admin', 'superadmin'])
    def put(self, insid):
        institute = Ins.query.filter(Ins.disabled == False).filter(Ins.id == insid).first()
        args = institutes_parser1.parse_args()
        if institute:
            if 'name'in args and args['name']:
                institute.name = args['name']
            else:pass
            if 'admin_user_id'in args and args['admin_user_id']:
                if g.role.name in ['admin', 'superadmin']:
                    institute.admin_user_id = args['admin_user_id']
                else: pass
            else:pass
            if 'type'in args and args['type']:
                institute.type = args['type']
            else:pass
            if 'ins_address'in args and args['ins_address']:
                institute.ins_address = args['ins_address']
            else:pass
            if 'note'in args and args['note']:
                institute.note = args['note']
            else:pass
            if 'longitude'in args and args['longitude']:
                institute.longitude = args['longitude']
            else:pass
            if args['location_id']:
                institute.location_id = args['location_id']
            else:pass
            if 'latitude'in args and args['latitude']:
                institute.latitude = args['latitude']
            else:pass
            try:
                if args['ins_picture']:
                    institute.ins_picture = upload_file(args['ins_picture'])
                else:pass
            except:pass
            if g.role.name in ['propertyuser', 'stationuser']:
                if institute.admin_user_id == g.user.id:
                    db.session.commit()
                    return '修改成功', 200
                else:return '权限不足', 301
            elif g.role.name in ['admin', 'superadmin']:
                db.session.commit()
                return '修改成功', 200
            else:return'权限不足', 301
        else: return '机构不存在', 201

    @api.doc('根据id删除机构')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @api.response(200, 'ok')
    def delete(self, insid):
        institute = Ins.query.filter(Ins.disabled == False).filter(Ins.id==insid).first()
        if institute:
            institute.disabled = True
            # facilityins=FacilityIns.query.filter(FacilityIns.ins_id==insid).all()
            # for i in facilityins:
            #  db.session.delete(i)
            # list=institute.user
            # for i in list:
            #     institute.user.remove(i)
            # for i in  institute.community:
            #     institute.community.remove(i)
            # db.session.delete(institute)
            db.session.commit()
            return '删除成功', 200
        else:return '机构不存在', 201


@api.route('/<insid>/<distance>/ins/')
class InsIns(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser', 'stationuser', 'admin', 'superadmin'])
    @api.doc('查询机构附近的机构')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.response(200, 'ok')
    def get(self, insid, distance):
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
        distance = request.args.get('distance', distance)
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        ins = Ins.query.filter(Ins.disabled == False).filter(Ins.id == insid).first()
        if ins:
            query = Ins.query.offset((int(page) - 1) * limit).limit(limit)
            total = query.count()
            _ = []
            for i in query.all():
                __={}
                __['ins_id'] = i.id
                __['ins_type'] = i.type
                __['ins_name'] = i.name
                __['longitude'] = str(i.longitude)
                __['latitude'] = str(i.latitude)
                __['ins_picture'] = i.ins_picture
                __['distance'] = round(getDistance(i.latitude, i.longitude, ins.latitude, ins.longitude))
                if getDistance(i.latitude, i.longitude, ins.latitude, ins.longitude) < float(distance) \
                        and getDistance(i.latitude, i.longitude, ins.latitude, ins.longitude) != 0:
                  _.append(__)
                else: continue

            result = {
                'code': 0,
                'msg': 'ok',
                'count': total,
                'data': _
            }
            return result, 200
        else:return '机构不存在', 201


@api.route('/<insid>/users/')
class InsUsesrView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser', 'stationuser', 'admin', 'superadmin'])
    @api.doc('查询机构下面的用户列表')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    def get(self, insid):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        if g.role.name == 'propertyuser':
            ins = Ins.query.filter(Ins.id == insid).filter(Ins.disabled == False).filter(Ins.type == '物业').first()
        elif g.role.name == 'stationuser':
            ins = Ins.query.filter(Ins.id == insid).filter(Ins.disabled == False).filter(Ins.type == '微型消防站').first()
        else:
            ins = Ins.query.filter(Ins.disabled == False).filter(Ins.id == insid).first()
        if ins:
            users = User.query.filter(User.id.in_(i.id for i in ins.user.all())).filter(User.disabled == False).order_by(User.id).offset((int(page)-1)*limit).\
            limit(limit).all()
            total = len(users)
            _ = []
            for user in users:
                __ = {}
                __['user_id'] = user.id
                __['user_name'] = user.username
                __['telephone'] = user.contract_tel
                _.append(__)

            result = {
                'code': 0,
                'message': "ok",
                "count": total,
                "data": _
            }
            return result, 200
        else:return '机构不存在', 201


@api.route('/<insid>/users/<userid>/')
class InsUserView(Resource):
    @api.doc('增加机构成员/用户绑定机构')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser', 'stationuser', 'admin', 'superadmin'])
    @api.response(200, 'ok')
    def post(self, insid, userid):
     ins = Ins.query.filter(Ins.disabled == False).filter(Ins.id == insid).first()
     user = User.query.filter(User.disabled == False).filter(User.id == userid).first()
     if ins.type == '物业':
        userrole = UserRole.query.filter(UserRole.user_id == userid).filter(UserRole.role_id == '2').first()
     else: userrole = UserRole.query.filter(UserRole.user_id == userid).filter(UserRole.role_id == '3').first()
     if ins and user:
         if user not in ins.user:
             if g.user.id == ins.admin_user_id or g.role.name in ['admin', 'superadmin']:
                    ins.user.append(user)
                    db.session.commit()
                    userrole.if_usable = True
                    db.session.commit()
                    return '添加成功', 200
             else: return '权限不足', 201
         else:return '用户已存在', 301
     else:return '信息有误', 401

    @api.doc('删除机构成员/解除用户绑定机构')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser', 'stationuser', 'admin', 'superadmin'])
    def delete(self, insid, userid):
        ins = Ins.query.filter(Ins.disabled == False).filter(Ins.id == insid).first()
        user = User.query.filter(User.disabled == False).filter(User.id == userid).first()
        if ins and user:
          if  user in ins.user:
              if g.user.id == ins.admin_user_id or g.role.name in ['admin', 'superadmin']:
                    ins.user.remove(user)
                    db.session.commit()
                    return '删除成功', 200
              else:return '权限不足', 201

          else:return '成员不存在', 301


@api.route('/<insid>/community')
class InsCommunityView(Resource):
    @api.doc('查询机构覆盖的社区')
    @ api.header('jwt', 'JSON Web Token')
    @ role_require(['propertyuser', 'stationuser', 'admin', 'superadmin'])
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    def get(self, insid):
        ins = Ins.query.filter(Ins.disabled == False).filter(Ins.id == insid).first()
        if ins:
            _ = []
            for i in ins.community.all():
                __ = {}
                __['id'] = i.id
                __['name'] = i.name
                __['detail_address'] = i.detail_address
                __['save_distance'] = i.save_distance
                __['eva_distance'] = i.eva_distance
                __['longitude'] = str(i.longitude)
                __['latitude'] = str(i.latitude)
                __['location_id'] = i.location_id
                __['location_district'] = Location.query.get_or_404(i.location_id).district
                __['community_picture'] = i.community_picture
                _.append(__)
            result = {
                'code': 0,
                'message': 'ok',
                'total': len(_),
                'data': _
            }
            return result, 200
        else: return '机构不存在', 201


@api.route('/<insid>/subuseralarmrecord')
class InsUseralarmrecordViews(Resource):
    @api.doc('查询机构管辖范围内的报警')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser', 'stationuser', 'admin', 'superadmin'])
    def get(self, insid):
        ins1 = Ins.query.filter(Ins.disabled == False).filter(Ins.id == insid).first()
        if ins1:
            user = ins1.user.all()
            if g.user in user or g.role.name in ['admin', 'superadmin']:
                if g.role.name == 'propertyuser':
                    ins = Ins.query.filter(Ins.type == '物业').filter(Ins.disabled == False).filter(Ins.id == insid).first()
                elif g.role.name == 'stationuser':
                    ins = Ins.query.filter(Ins.type == '微型消防站').filter(Ins.disabled == False).filter(Ins.id == insid).first()
                else:ins = Ins.query.filter(Ins.disabled == False).filter(Ins.id == insid).first()
                if ins:
                    community = ins.community.all()
                    home = []
                    for i in community:
                        home.extend(i.homes.all())
                    useralarmrecord = UserAlarmRecord.query.filter(UserAlarmRecord.home_id.in_(i.id for i in home)).all()
                    _ = []
                    total = len(useralarmrecord)
                    for i in useralarmrecord:
                        __={}
                        __['id'] = i.id
                        __['type'] = i.type
                        __['content'] = i.content
                        __['time'] = str(i.time)
                        __['home_id'] = i.home_id
                        __['home_name'] = Home.query.filter(Home.disabled == False).filter(Home.id == i.home_id).first().name
                        __['user_id'] = i.user_id
                        __['note'] = i.note
                        __['reference_alarm_id'] = i.reference_alarm_id
                        __['if_confirm'] = i.if_confirm
                        _.append(__)
                    result = {
                        'code': 0,
                        'msg': 'ok',
                        'total': total,
                        'data': _
                    }
                    return result, 200
                else:return '机构不存在', 201
        else:return '机构不存在', 201


@api.route('/useralarmrecord/')
class InsUseralarmrecordViews1(Resource):
    @api.doc('查询机构的报警')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['119user', 'admin', 'superadmin'])
    def get(self):
        useralarmrecord = UserAlarmRecord.query.filter(UserAlarmRecord.ins_id).all()
        _=[]
        for i in useralarmrecord:
            __ = {}
            __['id'] = i.id
            __['type'] = i.type
            __['content'] = i.content
            __['time'] = str(i.time)
            __['home_id'] = i.home_id
            __['ins_id'] = i.ins_id
            __['ins_name'] = Ins.query.filter(Ins.disabled == False).filter(Ins.id == i.ins_id).first().name
            __['user_id'] = i.user_id
            __['note'] = i.note
            __['reference_alarm_id'] = i.reference_alarm_id
            __['if_confirm'] = i.if_confirm
            _.append(__)
        result = {
            'data': _
        }
        return result, 200















