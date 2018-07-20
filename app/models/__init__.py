import datetime

from bson import ObjectId
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from app.ext import db


def objectid():
    return str(ObjectId())


t_role_menu = db.Table(
    'role_menu',
    db.Column('role_id', db.String(24), db.ForeignKey('role.id')),
    db.Column('menu_id', db.String(24), db.ForeignKey('menu.id')),
    db.UniqueConstraint('menu_id', 'role_id', name='uix_role_menu')

)

t_facility_knowledge = db.Table(
    'facility_knowledge',
    db.Column('knowledge_id', db.String(24), db.ForeignKey('knowledge.id')),
    db.Column('facility_id', db.String(24), db.ForeignKey('facility.id')),
    db.UniqueConstraint('knowledge_id', 'facility_id', name='uix_facility_knowledge')
)

t_user_ins = db.Table(
    'user_ins',
    db.Column('user_id', db.String(24), db.ForeignKey('user.id')),
    db.Column('ins_id', db.String(24), db.ForeignKey('ins.id')),
    db.UniqueConstraint('user_id', 'ins_id', name='uix_ins_user')
)
t_community_ins = db.Table(
    'community_ins',
    db.Column('community_id', db.String(24), db.ForeignKey('community.id')),
    db.Column('ins_id', db.String(24), db.ForeignKey('ins.id')),
    db.UniqueConstraint('community_id', 'ins_id', name='uix_ins_community')
)


class UserRole(db.Model):
    __tablename__ = 'user_role'
    id = db.Column(db.String(24), default=objectid, primary_key=True)
    user_id = db.Column('user_id', db.String(24), db.ForeignKey('user.id'), primary_key=True)
    if_usable = db.Column('if_usable', db.Boolean, comment='是否可用')
    role_id = db.Column('role_id', db.String(24), db.ForeignKey('role.id'), primary_key=True)


class HomeUser(db.Model):
    __tablename__ = 'homeuser'
    id = db.Column(db.String(24), default=objectid, primary_key=True)
    user_id = db.Column('user_id', db.String(24), db.ForeignKey('user.id'))
    home_id = db.Column('home_id', db.String(24), db.ForeignKey('home.id'))
    db.UniqueConstraint('user_id', 'home_id', name='uix_home_user')
    apply_time = db.Column('apply_time', db.DateTime, default=datetime.datetime.now, comment='申请时间')
    if_confirm = db.Column('if_confirm', db.Boolean, default=False, comment='是否批准')
    confirm_time = db.Column('confirm_time', db.DateTime, comment='批准时间')


class Ins(db.Model):
    __tablename__ = 'ins'
    id = db.Column(db.String(24), default=objectid, primary_key=True)
    type = db.Column(db.String(255), comment='机构类型')
    name = db.Column(db.String(50), comment='机构名称')
    ins_picture = db.Column(db.String(255), comment='机构图片')
    location_id = db.Column(db.String(50), db.ForeignKey('location.id'), comment='位置')
    ins_address = db.Column(db.String(255), comment='机构地址')
    note = db.Column(db.Text, comment='备注')
    latitude = db.Column(db.Float(asdecimal=True), comment='纬度')
    longitude = db.Column(db.Float(asdecimal=True), comment='经度')
    admin_user_id = db.Column(db.String(24), db.ForeignKey('user.id'), comment='管理员id')
    community = db.relationship('Community', secondary=t_community_ins, backref=db. backref('f1_community', lazy='dynamic'), lazy='dynamic')
    user = db.relationship('User', secondary=t_user_ins,backref=db.backref('f_user', lazy='dynamic'), lazy='dynamic' )
    disabled = db.Column(db.Boolean,nullable=False,default=False,comment='是否可用')


class Location (db.Model):
        __tablename__ = 'location'
        id = db.Column(db.String(24), default=objectid, primary_key=True)
        province = db.Column(db.String(25), comment='省/市')
        district = db.Column(db.String(50), comment='区')
        street = db.Column(db.String(50), comment='街道')


class Community(db.Model):
    __tablename__ = 'community'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    name = db.Column(db.String(255), comment='社区名')
    community_picture = db.Column(db.String(200), comment='社区图片')
    detail_address = db.Column(db.String(255), comment='详细地址')
    save_distance = db.Column(db.Integer, comment='求救距离')
    eva_distance = db.Column(db.Integer, comment='疏散距离')
    longitude = db.Column(db.Float(asdecimal=True), comment='经度')
    latitude = db.Column(db.Float(asdecimal=True), comment='纬度')
    ins = db.relationship('Ins', secondary=t_community_ins, backref=db.backref('f1_ins', lazy='dynamic'), lazy='dynamic')
    homes = db.relationship('Home', lazy='dynamic')
    location_id = db.Column(db.String(50), db.ForeignKey('location.id'), comment='位置')
    disabled = db.Column(db.Boolean, nullable=False,default=False, comment='是否可用')


class FacilityIns(db.Model):

    __tablename__ = 'facility_ins'
    id = db.Column(db.String(24), default=objectid, primary_key=True)
    facility_id = db.Column(db.String(24), db.ForeignKey('facility.id'), comment='设施id')
    facility = db.relationship('Facility')
    ins_id = db.Column(db.String(24), db.ForeignKey('ins.id'), comment='机构id')
    ins = db.relationship('Ins')
    note = db.Column(db.String(200), comment='备注')
    count = db.Column(db.Integer, comment='设施数量')
    expire_time = db.Column(db.DateTime, comment='过期时间')


class Facility(db.Model):
    __tablename__ = 'facility'
    id = db.Column(db.String(24), default=objectid, primary_key=True)
    facility_name = db.Column(db.String(50), comment='设施名')
    facility_picture = db.Column(db.String(200), comment='设施图片')
    note = db.Column(db.String(200),comment='备注')
    knowledge = db.relationship('Knowledge', secondary=t_facility_knowledge,
                                 backref=db.backref('f_knowledge', lazy='dynamic'),lazy='dynamic')
    disabled = db.Column(db.Boolean, nullable=False,default=False, comment='是否可用')


class Gateway(db.Model):
    __tablename__ = 'gateway'
    id = db.Column(db.String(24), default=objectid, primary_key=True)
    useable = db.Column(db.Boolean, default=True, comment='是否可用')
    home_id = db.Column(db.String(24), comment='家庭id')
    sensors = db.relationship('Sensor', lazy='dynamic')


class Home(db.Model):
    __tablename__ = 'home'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    name = db.Column(db.String(255), comment='家庭名称')
    community_id = db.Column(db.String(24), db.ForeignKey('community.id'), comment='社区id')
    community = db.relationship('Community')
    admin_user_id=db.Column(db.String(24), db.ForeignKey('user.id'), comment='创建者id')
    detail_address = db.Column(db.String(255), comment='家庭地址')
    link_name = db.Column(db.String(50), comment='主人姓名')
    telephone = db.Column(db.String(50), comment='电话号码')
    longitude = db.Column(db.Float(asdecimal=True), comment='经度')
    latitude = db.Column(db.Float(asdecimal=True), comment='纬度')
    alternate_phone = db.Column(db.String(50), comment='备用电话')
    gateway_id=db.Column(db.String(50),db.ForeignKey('gateway.id'), comment='网关id')
    disabled = db.Column(db.Boolean, nullable=False, default=False, comment='是否可用')


class Knowledge(db.Model):
    __tablename__ = 'knowledge'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    type = db.Column(db.String(50), comment='知识类型   (0.消防 1.逃生 2.灭火 3.新闻 4.其他)')
    content = db.Column(db.Text, comment='知识正文')
    title = db.Column(db.String(50), comment='知识标题')
    publish_time = db.Column(db.DateTime, default=datetime.datetime.now)
    publish_from = db.Column(db.String(100))
    facility = db.relationship('Facility', secondary=t_facility_knowledge, backref=db.backref('f_facility', lazy='dynamic'), lazy='dynamic')
    disabled = db.Column(db.Boolean, nullable=False, default=False, comment='是否可用')

class Menu(db.Model):
    __tablename__ = 'menu'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    p_id = db.Column(db.String(24), db.ForeignKey('menu.id'), comment='父id')
    children = db.relationship("Menu")
    parent = db.relationship("Menu", remote_side=[id])
    label = db.Column(db.String(20), nullable=False, comment='标签')
    level = db.Column(db.SmallInteger, comment='层级')
    type = db.Column(db.SmallInteger,  comment='类型')
    style = db.Column(db.String(50), comment='样式')
    disabled = db.Column(db.Boolean, default=False, comment='是否可用')
    roles = db.relationship('Role', secondary=t_role_menu,
                            backref=db.backref('menu_roles', lazy='dynamic'), lazy='dynamic')
    path = db.Column(db.String(200), comment='和url什么区别???')
    order = db.Column(db.SmallInteger, comment='?????')
    url = db.Column(db.String(200), comment='和path什么区别???')


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    disabled = db.Column(db.Boolean, nullable=False,default=True, comment='是否可用')
    description = db.Column(db.String(60), comment='权限描述')
    user_role=db.relationship('UserRole', foreign_keys=[UserRole.role_id], backref=db.backref('F_user_role', lazy='joined'),lazy='dynamic')
    menus = db.relationship('Menu', secondary=t_role_menu,
                            backref=db.backref('role_menus', lazy='dynamic'), lazy='dynamic')


class Sensor(db.Model):
    __tablename__ = 'sensor'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    gateway_id = db.Column(db.String(24), db.ForeignKey('gateway.id'), comment='网关id')
    gateway = db.relationship('Gateway')
    set_type = db.Column(db.String(24),default='0',comment='0:不设定，1:自设定，2:智能设定')
    online = db.Column(db.Boolean,comment='是否在线')
    sensor_place = db.Column(db.String(255), comment='位置')
    sensor_type = db.Column(db.Integer, comment='传感器类型   (0.烟雾,1.温度 2.燃气 3.智能插座,4.电磁阀)')
    max_value = db.Column(db.Float, comment='阈值')
    alarms_history = db.relationship('SensorAlarm', lazy='dynamic')


class SensorTime(db.Model):
    __tablename__ = 'sensor_time'
    id = db.Column(db.String(24), default=objectid, primary_key=True)
    sensor_id = db.Column(db.String(50), db.ForeignKey('sensor.id'), comment='传感器id')
    start_time = db.Column(db.Time, comment='开始时间')
    end_time = db.Column(db.Time, comment='结束时间')
    switch_on = db.Column(db.Boolean, default=False, comment='定时开关')


class MessageSend(db.Model):
    __tablename__ = 'messagesend'
    id = db.Column(db.String(24), default=objectid, primary_key=True)
    message_id = db.Column(db.String(24), comment='报警id')
    message_type = db.Column(db.String(24), comment='报警信息类型')
    role_id = db.Column(db.String(24), db.ForeignKey('role.id'), comment='角色id')
    user_id = db.Column(db.String(24), db.ForeignKey('user.id'), comment='接受用户id')
    if_send = db.Column(db.Boolean, default=False, nullable=False, comment='是否已经发送')
    if_read = db.Column(db.Boolean, default=False, nullable=False,comment='是否阅读')


class SensorHistory(db.Model):
    __tablename__ = 'sensorhistory'
    id = db.Column(db.String(24), default=objectid, primary_key=True)
    sensor = db.relationship('Sensor')
    sensor_id = db.Column(db.String(24), db.ForeignKey('sensor.id'), comment='传感器id')
    sensor_state = db.Column(db.String(24), comment='传感器状态 ')
    sensor_code = db.Column(db.Boolean, comment='是否正常 ')
    sensor_value = db.Column(db.String(255), comment='当前值')
    time = db.Column(db.DateTime, comment='时间')


class SensorAlarm(db.Model):
    __tablename__ = 'sensor_alarm'

    id = db.Column(db.String(24), default=objectid, primary_key=True, comment='')
    sensor_id = db.Column(db.String(24), db.ForeignKey('sensor.id'), comment='网关id')
    sensor = db.relationship('Sensor')
    gateway_id = db.Column(db.String(24), db.ForeignKey('gateway.id'), comment='关联网关id')
    note = db.Column(db.String(255), comment='报警内容')
    sensor_type = db.Column(db.Integer, comment='传感器类型   (0.烟雾 1.温度 2.燃气 3.电流,4)')
    var_type = db.Column(db.String(24), comment='变量类型')
    unit = db.Column(db.String(24), comment='变量单位')
    alarm_value = db.Column(db.String(24), comment='报警数值')
    alarm_time = db.Column(db.DateTime, default=datetime.datetime.now(), comment='报警时间')
    #confirm_time = db.Column(db.DateTime, comment='确认时间')
    is_timeout = db.Column(db.Boolean, default=False, comment='是否超时')
   # user_id = db.Column(db.String(24), db.ForeignKey('user.id'), comment='确认人id')
   # user = db.relationship('User')
    is_confirm = db.Column(db.Boolean, default=False, comment='是否确认')


class User(db.Model):

    __tablename__ = 'user'
    id = db.Column(db.String(24), default=objectid, primary_key=True)
    disabled = db.Column(db.Boolean, nullable=False, default=False, comment='是否停用   (1、禁用 0、正常)')
    contract_tel = db.Column(db.String(20), comment='用户电话')
    username = db.Column(db.String(20), index=True, comment='用户名)')
    password = db.Column(db.String(32), comment='密码')
    email = db.Column(db.String(60), comment='email')
    #salt = db.Column(db.String(50), comment='加密盐')
    createTime = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')
    #lastTime = db.Column(db.DateTime, comment='最后登陆时间')
    user_role = db.relationship('UserRole', foreign_keys=[UserRole.user_id], backref=db.backref('f_user_role', lazy='joined'), lazy='dynamic')
    #real_name = db.Column(db.String(50), comment='姓名')
    sensor_visable=db.Column(db.Boolean, default=True, comment='传感器是否可见')
    ins = db.relationship('Ins', secondary=t_user_ins, backref=db.backref('f_ins', lazy='dynamic'), lazy='dynamic')


class UserAlarmRecord(db.Model):
    __tablename__ = 'user_alarm_record'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    type = db.Column(db.Integer, default=0, comment='参考创建信息类型 (0,119 1,疏散,2,传感器，3,求救)')
    content = db.Column(db.String(255), comment='报警内容')
    if_confirm = db.Column(db.Boolean, default=False, comment='是否关闭')
    home_id = db.Column(db.String(24), db.ForeignKey('home.id'), comment='报警关联家庭id')
    home = db.relationship('Home')
    ins_id = db.Column(db.String(24), db.ForeignKey('ins.id'), comment='机构id')
    reference_alarm_id = db.Column(db.String(24), comment='参考创建信息id')
    user_id = db.Column(db.String(24), db.ForeignKey('user.id'), comment='发布人id')
    user = db.relationship('User')
    note = db.Column(db.String(255), comment='备注')
    origin = db.Column(db.String(255), comment='创建来源')
    mark = db.Column(db.String(255), comment='来源备注')
    time = db.Column(db.DateTime, default=datetime.datetime.now(), comment='创建时间')


class AlarmHandle(db.Model):
    __tablename__ = 'alarmhandle'
    id = db.Column(db.String(24), default=objectid, primary_key=True)
    type = db.Column(db.Integer, comment='信息类型(0,传感器报警 1，用户报警)')
    handle_type = db.Column(db.Integer, comment='操作类型(100,系统新创建 101,系统参考传感器报警创建 102,系统参考用户报警创建 '
        '103,系统修改 104,系统超时关闭 200,用户新创建 201,用户参考传感器报警创建 202,用户参考用户报警创建 203,用户修改 204,用户超时关闭 205，用户关闭)')
    reference_message_id = db.Column(db.String(24), comment='参考信息id')
    user_id = db.Column(db.String(24), comment='处理人员id')#  不关联用户，可以写入系统操作
    handle_time = db.Column(db.DateTime, default=datetime.datetime.now(), comment='操作时间')
    note = db.Column(db.String(255), comment='操作备注')







