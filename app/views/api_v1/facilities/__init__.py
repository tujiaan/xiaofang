from flask import g, request
from flask_restplus import Namespace, Resource, abort

from app.ext import db
from app.models import Facility, FacilityIns, Knowledge, UserRole, Role, Ins
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.utils.tools.upload_file import upload_file
from app.views.api_v1.facilities.parser import facility_parser, facility_parser1, f_parser, f1_parser

api = Namespace('Facilities', description='设备相关接口')

from .models import *


@api.route('/')
class FacilitiesInsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser', 'stationuser','admin', 'superadmin'])
    @page_format(code=0, msg='ok')
    @api.doc('查询设施列表')
    @api.marshal_with(facility_data_model, as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self):
        list = Facility.query.filter(Facility.disabled == False)
        try:
            return list, 200
        except:return None, 201

    @api.doc('新增设施')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @api.expect(f_parser)
    def post(self):
        args = f_parser.parse_args()
        facility_data = Facility()
        facility_data.facility_name = args['facility_name']
        p = args['facility_picture']
        facility_data.facility_picture = upload_file(p)
        facility_data.note = args['note']
        db.session.add(facility_data)
        db.session.commit()
        return None, 200


@api.route('/<facilityid>/')
class FacilityDataView(Resource):
    @api.doc('根据设施id查询详情')
    @api.marshal_with(facility_data_model)
    @api.response(200, 'ok')
    def get(self, facilityid):
        facility_data = Facility.query.filter(Facility.disabled == False).filter(Facility.id == facilityid).first()
        if facility_data:
            return facility_data, 200
        else:return '设施不存在', 201

    @api.doc('更新设施详情')
    @api.expect(f1_parser)
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin', 'propertyuser', 'stationuser'])
    def put(self, facilityid):
        facility = Facility.query.filter(Facility.id == facilityid).filter(Facility.disabled == False).first()
        if facility:
            args = f1_parser.parse_args()
            if args['facility_name']:
                facility.facility_name = args['facility_name']
            else:pass
            if args['facility_picture']:
                facility.facility_picture = upload_file(args['facility_picture'])
            else:pass
            if args['note']:
                facility.note = args['note']
            else:pass
            if g.role.name in['admin', 'superadmin']:
                db.session.commit()
                return'修改成功', 200
            elif g.role.name in ['stationuser', 'propertyuser']:
                facilityins = FacilityIns.query.filter(FacilityIns.facility_id == facilityid).first()
                ins = Ins.query.filter(Ins.id == facilityins.ins_id).first()
                if g.user.id == ins.admin_user_id:
                    db.session.commit()
                    return '修改成功', 200
            else: return'权限不足', 201
        else:
            return '设施不存在', 201

    @api.doc('删除设施')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    def delete(self, facilityid):
        facility = Facility.query.filter(Facility.disabled == False).filter(Facility.id == facilityid).first()
        if facility:
            facility.disabled = True
            db.session.commit()
        else:return '设施不存在', 201
        # knowledge = facility.knowledge
        # try:
        #     facilityins=FacilityIns.query.filter(FacilityIns.facility_id==facilityid).first()
        #     db.session.delete(facilityins)
        # except: pass
        # db.session.commit()
        # for i in knowledge:
        #     FacilityKnowledgeView.delete(self,facilityid,i.id)
        #     db.session.commit()
        # db.session.delete(facility)
        # db.session.commit()
        # return None,200


@api.route('/facility-ins/')
class FacilitesInsView(Resource):
    @page_format(code=0, msg='ok')
    @api.doc("查询设施关联机构列表")
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.marshal_with(facility_model, as_list=True)
    @api.response(200, 'ok')
    @page_range()
    def get(self):
       list = FacilityIns.query
       return list, 200

    @api.doc('新增设施机构关联')
    @api.response(200, 'ok')
    @api.expect(facility_parser)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    def post(self):
        args = facility_parser.parse_args()
        facilityins = FacilityIns(**args)
        ins = Ins.query.filter(Ins.disabled == False).filter(Ins.id == facilityins.ins_id).first()
        facility = Facility.query.filter(Facility.disabled == False).filter(Facility.id == facilityins.facility_id).first()
        if ins and facility:
            db.session.add(facilityins)
            db.session.commit()
            return None, 200
        else:return '信息有误', 201


@api.route('/facility-ins/<insid>')
class FacilitesInsView(Resource):
    @api.doc("查询设施机构关联设施列表")
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.response(200, 'ok')
    def get(self, insid):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        query = FacilityIns.query
        total = query.count()
        query = query.filter(FacilityIns.ins_id == insid).offset((int(page) - 1) * limit).limit(limit)
        _=[]
        for i in query.all():
            __={}
            __['id'] = i.id
            __['ins_id'] = i.ins_id
            __['ins_name'] = Ins.query.filter(Ins.disabled == False).filter(Ins.id == i.ins_id).first().name
            __['facility_id'] = i.facility_id
            __['facility_name'] = Facility.query.filter(Facility.disabled == False).\
                filter(Facility.id == i.facility_id).first().facility_name
            __['facility_picture'] = Facility.query.filter(Facility.disabled == False).\
                filter(Facility.id == i.facility_id).first().facility_picture
            __['count'] = i.count
            __['expire_time'] = str(i.expire_time)
            __['note'] = i.note
            _.append(__)

        result = {
            'code': 0,
            'msg': 'ok',
            'count': len(_),
            'result': _
        }
        return result, 200


@api.route('/facility-ins/<facilityid>/')
class FacilitesView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser', 'stationuser', 'admin', 'superadmin'])
    @api.doc('删除机构设施关联')
    @api.response(200, 'ok')
    def delete(self, facilityid):
        facilityins = FacilityIns.query.filter(FacilityIns.facility_id == facilityid).first()
        ins = Ins.query.filter(Ins.id == facilityins.ins_id).first()
        db.session.delete(facilityins)
        if g.role.name not in ['propertyuser', 'stationuser']:
            db.session.commit()
            return None, 200
        elif g.user.id == ins.admin_user_id:
            db.session.commit()
            return'删除成功', 200
        else:return'权限不足', 201

    @api.doc('更新机构设施关联')
    @api.response(200, 'ok')
    @api.expect(facility_parser1)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin', 'propertyuser', 'stationuser'])
    def put(self, facilityid):
        args = facility_parser1.parse_args()
        facilityins = FacilityIns.query.filter(FacilityIns.facility_id == facilityid).first()
        if args.get('ins_id'):
            facilityins.ins_id = args.get('ins_id')
        else:pass
        if args.get('count'):
            facilityins.count = args.get('count')
        else:pass
        if args.get('expire_time'):
            facilityins.expire_time = args.get('expire_time')
        else:pass
        if args.get('note'):
            facilityins.expire_time = args.get('note')
        else:pass
        db.session.commit()
        return None, 200
       ##############################有问题########################


@api.route('/<facilityid>/knowledges/')
class FacilityKnowledgesView(Resource):
    @page_format(code=0, msg='ok')
    @api.doc('查询设施的知识')
    @role_require(['homeuser', 'propertyuser', 'stationuser', '119user', 'admin', 'superadmin'])
    @api.marshal_with(knowledges_model, as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.response(200, 'ok')
    @ page_range()
    def get(self, facilityid):
        facility = Facility.query.filter(Facility.id == facilityid).filter(Facility.disabled == False).first()
        try:
            return facility.knowledge, 200
        except: return None, 201


@api.route('/<facilityid>/knowledges/<knowledgeid>/')
class FacilityKnowledgeView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @api.doc('给设施绑定知识')
    @api.response(200, 'ok')
    @api.response(404, 'Not Found')
    def post(self, facilityid, knowledgeid):
        facility = Facility.query.filter(Facility.disabled == False).filter(Facility.id == facilityid).first()
        knowledge = Knowledge.query.filter(Knowledge.disabled == False).filter(Knowledge.id == knowledgeid).first()
        if facility and knowledge:
            facility.knowledge.append(knowledge)
            db.session.commit()
            return '绑定成功', 200
        else:
            return '参数有误', 201

    @api.doc('解除设施绑定知识')
    @api.response(200, 'ok')
    @api.response(404, 'Not Found')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    def delete(self, facilityid, knowledgeid):
        facility = Facility.query.filter(Facility.disabled == False).filter(Facility.id == facilityid).first()
        knowledge = Knowledge.query.filter(Knowledge.disabled == False).filter(Knowledge.id == knowledgeid).first()
        if facility and knowledge:
            facility.knowledge.remove(knowledge)
            db.session.commit()
            return '解除成功', 200
        else:
            return '参数有误', 201










