import datetime
from urllib.parse import quote

import os
from flask import current_app
from flask_restplus import Namespace, Resource, abort
from werkzeug.utils import secure_filename
from app.ext import db
from app.models import Knowledge, Facility
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.facilities import facility_model, FacilitesView, facility_data_model
from app.views.api_v1.knowledges.parser import knowledge_parser, knowledge_parser1, upload_parser, allowed_file

api = Namespace('Knowledges', description='知识相关接口')
from .models import *


@api.route('/')
class Knowledges(Resource):
    @page_format(code=0, msg='ok')
    @api.doc('查询知识列表')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.marshal_with(knowledges_model, as_list=True)
    @api.response(200, 'ok')
    @page_range()
    def get(self):
            list=Knowledge.query.filter(Knowledge.disabled == False)
            try:
                return list, 200
            except: return None,201

    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin', 'knowledgeadmin'])
    @api.doc('添加知识')
    @api.expect(knowledge_parser)
    @api.response(200, 'ok')
    def post(self):
        args = knowledge_parser.parse_args()
        knowledge = Knowledge(**args)
        db.session.add(knowledge)
        db.session.commit()
        return None, 200


@api.route('/<knowledgetype>')
class KnowledgeView(Resource):
    @page_format(code=0, msg='ok')
    @api.doc('根据类型查询知识列表')
    @api.marshal_with(knowledges_model)
    @api.response(200, 'ok')
    @page_range()
    def get(self, knowledgetype):
     list=Knowledge.query.filter(Knowledge.type == knowledgetype).filter(Knowledge.disabled == False)
     try:
        return list, 200
     except: return None, 201


@api.route('/<knowledgeid>/')
class KnowledgeView(Resource):
    @api.doc('根据id查询知识详情')
    @api.marshal_with(knowledges_model)
    @api.response(200, 'ok')
    def get(self, knowledgeid):
        knowledge = Knowledge.query.filter(Knowledge.disabled == False).filter(Knowledge.id == knowledgeid).first()
        if knowledge:
            return knowledge, 200
        else:return '知识不存在',201

    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin', 'knowledgeadmin'])
    @api.doc('根据id更新知识')
    @api.expect(knowledge_parser1)
    @api.response(200, 'ok')
    def put(self, knowledgeid):
        args = knowledge_parser1.parse_args()
        knowledge = Knowledge.query.filter(Knowledge.disabled==False).filter(Knowledge.id == knowledgeid).first()
        if knowledge:
            if args['type']:
                knowledge.type = args.get('type')
            else:pass
            if args['content']:
                knowledge.content = args.get('content')
            else:pass
            if args['title']:
                knowledge.title = args.get('title')
            else:pass
            if args['publish_from']:
                knowledge.publish_from = args['publish_from']
            db.session.commit()
            return '更新成功', 200
        else: return '知识不存在', 201

    @api.doc('根据id删除知识')
    @api.response(200, 'ok')
    @api.response(404, 'Not Found')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin', 'knowledgeadmin'])
    def delete(self, knowledgeid):
        knowledge = Knowledge.query.filter(Knowledge.id == knowledgeid).filter(Knowledge.disabled == False).first()
        if knowledge:
            knowledge.disabled = True
        # facility=knowledge.facility.all()
        # for i in facility:
        #     KnowledgeFacilityView1.delete(self,knowledgeid,i.id)
        # db.session.delete(knowledge)
            db.session.commit()
            return None, 200
        else: return '知识不存在', 201


@api.route('/<knowledgeid>/facility')
class KnowledgeFacilityView(Resource):
    @page_format(code='200', msg='successs')
    @api.doc('根据知识查找对应的设施')
    @api.marshal_with(facility_data_model, as_list=True)
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self, knowledgeid):
        knowledge = Knowledge.query.filter(Knowledge.id == knowledgeid).filter(Knowledge.disabled == False).first()
        try:
            return knowledge.facility, 200
        except: return None,201


@api.route('/<knowledgeid>/facility/<facilityid>')
class KnowledgeFacilityView1(Resource):
    @api.doc('设施绑定知识')
    @api.response(200, 'ok')
    @api.response(404, 'Not Found')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    def post(self, knowledgeid, facilityid):
            facility = Facility.query.filter(Facility.disabled == False).filter(Facility.id == facilityid).first()
            knowledge = Knowledge.query.filter(Knowledge.disabled == False).filter(Knowledge.id == knowledgeid).first()
            if facility and knowledge:
                knowledge.facility.append(facility)
                db.session.commit()
                return '绑定成功', 200
            else: return '信息有误', 201

    @api.doc('解除知识绑定')
    @api.response(200, 'ok')
    @api.response(404, 'Not Found')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    def delete(self, knowledgeid, facilityid):
            facility = Facility.query.filter(Facility.disabled == False).filter(Facility.id == facilityid).first()
            knowledge = Knowledge.query.filter(Knowledge.disabled == False).filter(Knowledge.id == knowledgeid).first()
            if facility and knowledge:
                facility.knowledge.remove(knowledge)
                db.session.commit()
                return None, 200
            else:return '信息有误', 201


@api.route('/picture')
class Upload(Resource):
    @api.doc('上传文件')
    # @api.header('jwt', 'JSON Web Token')
    # @role_require(['knowledgeadmin', 'superadmin'])
    @api.expect(upload_parser, validate=True)
    @api.response(200, '已创建')
    @api.response(415, '格式不支持')
    def post(self):
        args = upload_parser.parse_args()
        file = args.get('file')
        if file.filename == 'blob': file.filename = 'blob.png'
        if not allowed_file(file.filename):
            return None, 415
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d')
        filename = now.strftime('%H%M%S') + secure_filename(quote(file.filename))
        path = current_app.config.get('UPLOAD_FOLDER', None) + date
        src = current_app.config.get('UPLOADED_URL', None) + date + '/' + filename
        pre_fix=current_app.config.get('PRE_FIX')
        if not os.path.exists(path):
            os.makedirs(path)
        file.save(path + '/' + filename)
        result={
            'errno':0,
            'code':0,
            'message':'ok',
            'data':[pre_fix+src]
        }
        return result, 200