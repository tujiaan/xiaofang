import base64

from flask import g, request
from flask_restplus import Namespace, Resource, abort

from app.ext import db
from app.models import Community, Ins, Home, UserRole, Role, Location, UserAlarmRecord, User
from app.utils.auth import user_require
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.utils.tools.upload_file import upload_file
from app.views.api_v1 import homes

from app.views.api_v1.communities.parser import community_parser, community_parser1


api = Namespace('Community', description='社区相关操作')
from app.views.api_v1.communities.models import community_model, _community_model, home_model


@api.route('/')
class CommunitiesView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser', 'stationuser', 'admin', '119user', 'superadmin'])
    @api.doc('查询所有的社区列表')
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    def get(self):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        query = Community.query.order_by(Community.id)
        total = query.count()
        query = query.filter(Community.disabled == False).offset((int(page) - 1) * limit).limit(limit)

        _=[]
        for i in query.all():
            __={}
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
            # if g.role.name in['propertyuser', 'stationuser']:
            #     for j in i.ins.all():
            #      if g.user.id == j.admin_user_id:
            #          _ .append(__)
            #      else:pass
            # else:
            #     _.append(__)
        result = {
            'code': 0,
            'message': 'ok',
            'count': total,
            'data': _
        }
        return result, 200

    @api.route('/showlist')
    class CommunitiesView1(Resource):
        @api.header('jwt', 'JSON Web Token')
        @ role_require(['homeuser', '119user', 'propertyuser', 'stationuser', 'admin', '119user', 'superadmin'])
        @api.doc('查询所有的社区名称')
        @page_format(code=0, msg='ok')
        @api.marshal_with(_community_model, as_list=True)
        @api.response(200, 'ok')
        @api.doc(params={'page': '页数', 'limit': '数量'})
        @page_range()
        def get(self):
            community = Community.query.filter(Community.disabled == False)
            try:
                return community, 200
            except:return None, 201

    @api.doc('新增社区')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @api.expect(community_parser, validate=True)
    @api.response(200, 'ok')
    def post(self):
        args = community_parser.parse_args()
        community = Community()
        if 'name'in args:
            community.name = args.get('name', None)
        else:pass
        if 'ins_id'in args:
            community.ins_id = args.get('ins_id', None)
        else:pass
        if 'longitude'in args:
            community.longitude = args.get('longitude', None)
        else:pass
        if 'latitude'in args:
            community.latitude = args.get('latitude', None)
        else:pass
        if 'save_distance'in args:
            community.save_distance = args.get('save_distance', None)
        else:pass
        if 'eva_distance'in args:
            community.eva_distance = args.get('eva_distance', None)
        else:pass
        if 'detail_address'in args:
            community.detail_address = args.get('detail_address', None)
        else:pass
        if args['community_picture']:
            community.community_picture = upload_file(args['community_picture'])
        else:pass
        if args['location_id']:
            community.location_id = args['location_id']
        else:pass
        db.session.add(community)
        db.session.commit()
        return None, 200


@api.route('/<communityid>/')
class CommunityView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', '119user', 'propertyuser', 'stationuser', 'superadmin'])
    @api.doc('查询特定的小区信息')
    @api.response(200, 'ok')
    def get(self, communityid):
        community = Community.query.filter(Community.id == communityid).filter(Community.disabled == False).first()
        if community:
            ins = community.ins.all()
            _=[]
            for i in ins:
                __={}
                __['ins_id'] = i.id
                __['ins_type'] = i.type
                __['ins_name']=i.name
                _.append(__)
            community = {
                'community_id': community.id,
                'community_name': community.name,
                'community_longitude': float(community.longitude),
                'community_latitude': float(community.latitude),
                'detail_address': community.detail_address,
                'save_distance': float(community.save_distance),
                'eva_distance': float(community.eva_distance),
                'location_id': community.location_id,
                'community_picture': community.community_picture,
                'ins_count': len(ins),
                'ins_data':_

            }
            if g.role.name == 'propertyuser'or g.role.name == 'stationuser':
                if g.user.id in[i.admin_user_id for i in ins]:
                    return community, 200
                else:return'权限不足', 201
            else:return community, 200
        else: return'社区不存在', 201

    @api.doc('更新社区的信息')
    @api.expect(community_parser1)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin' ])
    @api.response(200, 'ok')
    def put(self, communityid):
        args = community_parser1.parse_args()
        community = Community.query.filter(Community.id == communityid).filter(Community.disabled==False).first()
        if community:
            if 'name' in args and args['name']:
                community.name = args.get('name')
            else:
                pass
            if 'longitude' in args and args['longitude']:
                community.longitude = args.get('longitude')
            else:
                pass
            if 'latitude' in args and args['latitude']:
                community.latitude = args.get('latitude')
            else:
                pass
            if 'save_distance' in args and args['save_distance']:
                community.save_distance = args.get('save_distance')
            else:
                pass
            if 'eva_distance' in args and args['eva_distance']:
                community.eva_distance = args.get('eva_distance')
            else:
                pass
            if 'detail_address' in args and args['detail_address']:
                community.detail_address = args.get('detail_address')
            else:
                pass
            if args['community_picture']:
                community.community_picture = upload_file(args['community_picture'])
            else:
                pass
            if args['location_id']:
                community.location_id = args['location_id']
            else:pass
            db.session.commit()
            return None, 200
        else:
            return '社区不存在', 201

    @api.doc('删除社区')################################################
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin',  'superadmin'])
    @api.response(200, 'ok')
    def delete(self, communityid):
        community = Community.query.filter(Community.id == communityid).filter(Community.disabled == False).first()
        community.disabled = True
        # home = Home.query.filter(Home.id.in_(i.id for i in community.homes))
        # list = community.ins
        # for i in home:
        #   useralarmrecord = UserAlarmRecord.query.filter(UserAlarmRecord.home_id == i.id)
        #   db.session.delete(useralarmrecord)
        #   homes.HomeView.delete(self, i.id)
        # for i in list:
        #     community.ins.remove(i)
        # db.session.delete(community)
        db.session.commit()
        return None, 200


@api.route('/<communityid>/homes')
class CommunityHome(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', '119user', 'propertyuser', 'stationuser', 'superadmin'])
    @api.doc('查询社区覆盖的家庭')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.response(200, 'ok')
    def get(self, communityid):
        community = Community.query.filter(Community.id == communityid).filter(Community.disabled == False).first()
        if community:
                _ = []
                for i in community.homes.all():
                    __ = {}
                    __['home_id'] = i.id
                    __['home_name'] = i.name
                    __['community_id'] = i.community_id
                    __['community_name'] = Community.query.filter(Community.id == i.community_id).filter(
                        Community.disabled == False).first().name
                    __['detail_address'] = i.detail_address
                    __['link_name'] = i.link_name
                    __['tephone'] = i.telephone
                    __['longitude'] = str(i.longitude)
                    __['latitude'] = str(i.latitude)
                    __['gateway_id'] = i.gateway_id
                    __['alternate_phone'] = i.alternate_phone
                    __['admin_user_id'] = i.admin_user_id
                    __['admin_name'] = User.query.filter(User.disabled == False).filter(
                        User.id == i.admin_user_id).first().username
                    _.append(__)
                result = {
                    'code': 0,
                    'msg': 'ok',
                    'count': len(_),
                    'data': _
                }
                return result, 200
        else:abort(404, message='社区不存在')


@api.route('/<communityid>/ins/<insid>')
class CommunityInsViews(Resource):
    @api.doc('增加机构和社区绑定')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin',  'superadmin'])
    def post(self, communityid, insid):
        community = Community.query.filter(Community.id == communityid).filter(Community.disabled == False).first()
        try:
            if community:
                ins = Ins.query.filter(Ins.id == insid).filter(Ins.disabled == False).first()
                if ins:
                    community.ins.append(ins)
                    db.session.commit()
                    return '绑定成功', 200
                else: return '机构不存在', 201
            else:return'社区不存在', 201
        except:return'请不要重复绑定', 201

    @api.doc('解除机构和社区绑定')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    def delete(self, communityid, insid):
        community = Community.query.filter(Community.id == communityid).filter(Community.disabled == False).first()
        if community:
            ins = Ins.query.filter(Ins.disabled == False).filter(Ins.id == insid).first()
            if ins:
                community.ins.remove(ins)
                db.session.commit()
                return '解除成功', 200
            else: return '机构不存在', 201
        else:
            return '社区不存在', 201






