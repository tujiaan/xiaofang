from flask_restplus import Namespace, Resource

from app.models import Alarm
from app.utils.tools.page_range import page_format, page_range

api = Namespace('Alarm', description='报警相关操作')


@api.route('/')
class AlarmsView(Resource):
    @page_format(code=0, msg='ok')
    @api.doc('查询所有报警记录')
    @api.marshal_with()
    @page_range()
    def get(self):
        alarms = Alarm.query
        return alarms, 200