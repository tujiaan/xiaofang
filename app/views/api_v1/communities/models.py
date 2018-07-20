import base64

from app.views.api_v1.communities import api
from flask_restplus import Model, fields

community_pic_model = api.model('CommunityPictureModel', {
   # 'id':fields.String,
    'community_picture':fields.String(attribute=lambda x: base64.b64encode(x).decode() if x else None)
})
community_model = api.model('CommunityModel', {
    'id': fields.String,
    'name': fields.String,
    'detail_address': fields.String,
    'save_distance': fields.Integer,
    'eva_distance': fields.Integer,
    # 'ins_id':fields.String,
    'longitude': fields.Float,
    'latitude': fields.Float,
    'location_id': fields.String,
    'community_picture': fields.String#fields.Nested(community_pic_model)

})
home_model = api.model('HomeModel', {
    'id': fields.String,
    'name': fields.String,
    'community_id': fields.String,

    'detail_address': fields.String,
    'link_name': fields.String,
    'telephone': fields.String,
    'longitude': fields.Float,
    'latitude':fields.Float,
    'alternate_phone': fields.String
})

_community_model = api.model('CommunityModel', {
    'id': fields.String,
    'name': fields.String
})
