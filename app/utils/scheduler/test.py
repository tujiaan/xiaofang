import datetime
from operator import or_, and_

import math
from flask import app, json
from flask_restplus import abort

from app.ext import db, getui, mqtt
from app.models import Sensor, SensorAlarm, MessageSend, Home, HomeUser, User, Ins, UserAlarmRecord, Role, UserRole, \
    SensorTime


def BuiltSensorSendMessage(app):
    with app.app_context():
        sensoralarm = SensorAlarm.query.all()
        for i in sensoralarm:
            messagesend = MessageSend.query.filter(MessageSend.message_id == i.id).all()
            if len(messagesend) < 1:
                    home = Home.query.filter(Home.gateway_id == i.gateway_id).filter(Home.disabled == False).first()
                    if home:
                        h = []
                        _ = Home.query.filter(Home.disabled == False).all()
                        for j in _:
                            if getDistance(home.latitude, home.longitude, j.latitude,
                                           j.longitude) <= home.community.save_distance and j!=home:
                               h.append(j)
                        homeuser = HomeUser.query.filter(HomeUser.home_id.in_(i.id for i in list(set(h+[home])))).all()
                        user = User.query.filter(User.id.in_(i.user_id for i in homeuser)).filter(User.disabled == False).all()
                        for j in user:
                            messagesend = MessageSend(message_id=i.id, message_type='传感器报警', user_id=j.id, role_id='1')
                            ms = MessageSend.query.filter(and_(MessageSend.message_id == i.id, MessageSend.user_id == j.id)).first()
                            if ms is None:
                                db.session.add(messagesend)
                                db.session.commit()#生成传感器报警推送给家庭成员的记录
                            else:pass
                        if not i.is_confirm and not SensorAlarm.query.filter(SensorAlarm.sensor_id==i.id).filter(SensorAlarm.alarm_time==(i.alarm_time - datetime.timedelta(minutes=15))).first():
                            community = home.community
                            ins = community.ins.all()
                            if len(ins) > 0:
                                for j in ins:
                                    for k in j.user:
                                        if j.type=='物业':
                                            messagesend = MessageSend(message_id=i.id, message_type='传感器报警', user_id=k.id, role_id='2')
                                        else: messagesend = MessageSend(message_id=i.id, message_type='传感器报警', user_id=k.id, role_id='3')
                                        ms = MessageSend.query.filter(
                                            and_(MessageSend.message_id == i.id, MessageSend.user_id == j.id)).first()
                                        if ms is None:
                                            db.session.add(messagesend)
                                            db.session.commit()#生成推送给传感器报警的家庭上级的机构的记录
                                        else:
                                            pass
                            else: pass#abort(404, message='机构不存在')
                    else: pass#abort(404, message='家庭不存在')
            else:pass
    return None, 200


def BuiltUserSendMessage(app):
    with app.app_context():
        useralarmrecord = UserAlarmRecord.query.all()
        for i in useralarmrecord:
            sendmessage= MessageSend.query.filter(MessageSend.message_id == i.id).all()
            if len(sendmessage) < 1:
                if i.home_id:
                    home = Home.query.filter(Home.id == i.home_id).filter(Home.disabled==False).first()
                    if home:
                        homeuser = HomeUser.query.filter(HomeUser.home_id == i.home_id).all()
                        user1 = User.query.filter(User.id.in_(i.user_id for i in homeuser)).all()
                        ins = home.community.ins.all()
                    else:pass#abort(404)
                else:
                    ins = Ins.query.filter(Ins.id == i.ins_id).filter(Ins.disabled == False).all()
                list1 = []
                for _ in ins:
                    list1.append(_.user.all())
                    if _.type =='物业':
                        if i.type == 0 or i.type == 1:
                            userrole = UserRole.query.filter(or_(UserRole.role_id == '4', UserRole.role_id == '5')).union(
                                UserRole.query.filter((UserRole.role_id == '6'))).all()
                            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1)).filter(User.disabled == False)
                            query2 = User.query.with_entities(User.id).filter(User.id.in_(i[0].id for i in list1)).filter(User.disabled == False)
                            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole)).filter(User.disabled == False)
                            list2 = query1.union(query2).union(query3).all()
                            for j in list2:
                                if j in query1.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='1')
                                elif j in query2.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='2')
                                else:
                                    user_role = UserRole.query.filter(UserRole.user_id == j.id).all()
                                    roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
                                    if '4'in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='4')
                                    elif '5'in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='5')
                                    else:messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='6')

                                db.session.add(messagesend)###119 admin superadmin 不会出现在同一人
                                db.session.commit()
                        elif i.type == 2:
                            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1)).filter(User.disabled == False)
                            query2 = User.query.with_entities(User.id).filter(User.id.in_(i[0].id for i in list1)).filter(User.disabled == False)
                            userrole = UserRole.query.filter(or_(UserRole.role_id == '5', UserRole.role_id == '6')).all()
                            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole)).filter(User.disabled == False)
                            list2 = query1.union(query2).union(query3).all()
                            for j in list2:
                                if j in query1.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='1')
                                elif j in query2.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='2')
                                else:
                                    user_role = UserRole.query.filter(UserRole.user_id == j.id).all()
                                    roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
                                    if '5' in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                          role_id='5')
                                    else:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='6')
                                db.session.add(messagesend)  ###119 admin superadmin 不会出现在同一人
                                db.session.commit()
                        else:
                            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1)).filter(User.disabled==False)
                            query2 = User.query.with_entities(User.id).filter(User.id.in_(i[0].id for i in list1)).filter(User.disabled==False)
                            userrole = UserRole.query.filter(or_(UserRole.role_id == '4',UserRole.role_id == '5')).union(UserRole.query.filter((UserRole.role_id=='6'))).all()
                            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole)).filter(User.disabled==False)
                            list2 = query1.union(query2).union(query3).all()
                            for j in list2:
                                if j in query1.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='1')
                                elif j in query2.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='2')
                                else:
                                    user_role = UserRole.query.filter(UserRole.user_id == j.id).all()
                                    roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
                                    if '4' in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='4')
                                    elif '5' in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='5')
                                    else:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='6')
                                db.session.add(messagesend)  ###119 admin superadmin 不会出现在同一人
                                db.session.commit()
                    else:
                        if i.type == 0 or i.type == 1:
                            userrole = UserRole.query.filter(or_(UserRole.role_id == '4', UserRole.role_id == '5')).union(
                                UserRole.query.filter((UserRole.role_id == '6'))).all()
                            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1)).filter(User.disabled==False)
                            query2 = User.query.with_entities(User.id).filter(User.id.in_(i[0].id for i in list1)).filter(User.disabled==False)
                            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole)).filter(User.disabled==False)
                            list2 = query1.union(query2).union(query3).all()
                            for j in list2:
                                if j in query1.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,role_id='1')
                                elif j in query2.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='3')
                                else:
                                    user_role = UserRole.query.filter(UserRole.user_id == j.id).all()
                                    roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
                                    if '4'in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='4')
                                    elif '5'in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='5')
                                    else:messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='6')
                                db.session.add(messagesend)###119 admin superadmin 不会出现在同一人
                                db.session.commit()
                        elif i.type == 2:
                            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1)).filter(User.disabled==False)
                            query2 = User.query.with_entities(User.id).filter(User.id.in_(i[0].id for i in list1)).filter(User.disabled==False)
                            userrole = UserRole.query.filter(or_(UserRole.role_id == '5', UserRole.role_id == '6')).all()
                            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole)).filter(User.disabled==False)
                            list2 = query1.union(query2).union(query3).all()
                            for j in list2:
                                if j in query1.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='1')
                                elif j in query2.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='3')
                                else:
                                    user_role = UserRole.query.filter(UserRole.user_id == j.id).all()
                                    roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
                                    if '5' in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                          role_id='5')
                                    else:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='6')
                                db.session.add(messagesend)  ###119 admin superadmin 不会出现在同一人
                                db.session.commit()
                        else:
                            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1)).filter(User.disabled==False)
                            query2 = User.query.with_entities(User.id).filter(User.id.in_(i[0].id for i in list1)).filter(User.disabled==False)
                            userrole = UserRole.query.filter(or_(UserRole.role_id=='4',UserRole.role_id=='5')).union(UserRole.query.filter((UserRole.role_id=='6'))).all()
                            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole)).filter(User.disabled==False)
                        list2 = query1.union(query2).union(query3).all()
                        for j in list2:
                            if j in query1.all():
                                messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='1')
                            elif j in query2.all():
                                messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='3')
                            else:
                                user_role = UserRole.query.filter(UserRole.user_id == j.id).all()
                                roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
                                if '4' in [i.id for i in roles]:
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                              role_id='4')
                                elif '5' in [i.id for i in roles]:
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                              role_id='5')
                                else:
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                              role_id='6')
                            db.session.add(messagesend)  ###119 admin superadmin 不会出现在同一人
                            db.session.commit()
            else: pass
        return None, 200


def SendMessage(app):
    with app.app_context():
        sendmessage = MessageSend.query.filter(MessageSend.if_send == False).order_by(MessageSend.message_id).all()
        for i in sendmessage:
            if i.message_type == '传感器报警':
                sensoralarm = SensorAlarm.query.filter_by(id=i.message_id).first()
                home = Home.query.filter(Home.gateway_id==sensoralarm.gateway_id).filter(Home.disabled==False).first()
                if sensoralarm and home:
                    if sensoralarm.sensor_type == '0':
                        content =home.community+home.detail_address+'烟雾传感器'+sensoralarm.sensor_id+'在'+sensoralarm.alarm_time.strftime("%Y-%m-%d %H:%M:%S")+'异常'
                        data = {'d': {
                            sensoralarm.sensor_id: [0]
                        },
                            'time': datetime.datetime.now()
                        }
                        theme = str(sensoralarm.sensor.gateway_id) + '/cmd'
                        mqtt.publish(theme, json.dumps(data))
                    elif sensoralarm.sensor_type == '1':
                        content =home.community.name+home.detail_address+'温度传感器' + sensoralarm.sensor_id +'在'+sensoralarm.alarm_time.strftime("%Y-%m-%d %H:%M:%S")+ '异常'
                    elif sensoralarm.sensor_type == '2':
                         content =home.community.name+home.detail_address+'燃气阀' + sensoralarm.sensor_id +'在'+sensoralarm.alarm_time.strftime("%Y-%m-%d %H:%M:%S")+ '异常'
                    elif sensoralarm.sensor_type == '3':
                        content =home.community.name+home.detail_address+'智能插座' + sensoralarm.sensor_id +'在'+sensoralarm.alarm_time.strftime("%Y-%m-%d %H:%M:%S")+ '异常'
                    else: content =home.community.name+home.detail_address+'电磁阀'+sensoralarm.sensor_id+'在'+sensoralarm.alarm_time.strftime("%Y-%m-%d %H:%M:%S")+'异常'
                    lst=[]
                    for i in sendmessage:
                        lst.append(i.user_id)
                        taskid = getui.getTaskId(i.message_id, content)
                        rs = getui.sendList(lst, taskid)
                        i.if_send = True
                        db.session.commit()
                else:pass
            else:
                user_alarm =UserAlarmRecord.query.filter(UserAlarmRecord.id==i.message_id).first()
                lst=[]
                for i in sendmessage:
                    lst.append(i.user_id)
                    if user_alarm.home_id:
                        home=Home.query.filter_by(id=user_alarm.home_id).filter(Home.disabled==False).first()
                        if home:
                            taskid = getui.getTaskId(i.message_id, home.name+'在'+user_alarm.time.strftime("%Y-%m-%d %H:%M:%S")+'发布了一条'+i.message_type)
                            rs = getui.sendList(lst, taskid)
                        else:pass
                    else:
                        ins=Ins.query.filter_by(id=user_alarm.ins_id).filter(Ins.disabled==False).first()
                        if ins:
                            taskid = getui.getTaskId(i.message_id, ins.name+'在'+user_alarm.time.strftime("%Y-%m-%d %H:%M:%S")+'发布了一条'+i.message_type)
                            rs = getui.sendList(lst, taskid)
                        else:pass

                    i.if_send = True
                    db.session.commit()


def OpenSensor(app):
    with app.app_context():
        sensortimes = SensorTime.query.all()
        for sensortime in sensortimes:
            sensor = Sensor.query.filter(Sensor.id==sensortime.sensor_id).filter(Sensor.online==True).first()
            if sensor:
                if sensortime.start_time >= datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S') and sensortime.\
                        switch_on == True:

                    data = {'d': {
                        sensortime.sensor_id: [1]
                    },
                        'time': datetime.datetime.now()
                    }
                    theme = str(sensor.gateway_id) + '/cmd'
                    mqtt.publish(theme, json.dumps(data))
                else:
                    pass
                if sensortime.end_time >= datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S') and sensortime.\
                        switch_on == True:
                    data = {'d': {
                        sensortime.sensor_id: [0]
                    },
                        'time': datetime.datetime.now()
                    }
                    theme = str(sensor.gateway_id) + '/cmd'
                    mqtt.publish(theme, json.dumps(data))
                else:pass
            else:pass


def builtusersendmessage(app):
    with app.app_context():
        useralarmrecords = UserAlarmRecord.query.all()
        for useralarmrecord in useralarmrecords:
            messsgesends = MessageSend.query.filter(MessageSend.message_id == useralarmrecord.id,).all()
            if useralarmrecord.type == 0:
                if useralarmrecord.home_id:
                    home = Home.query.filter(Home.disabled == False).filter(Home.id == useralarmrecord.home_id).first()
                    if home:
                        homeusers1 = HomeUser.query.filter(HomeUser.home_id == home.id).all()
                        user1 = User.query.filter(User.disabled == False).filter(User.id.in_(i.user_id for i in homeusers1)).all()#####报警家庭成员
                        user2 = []###报警家庭上级机构
                        community = home.community
                        inses = community.ins.all()
                        for ins in inses:
                            user2.extend(ins.user.all())
                        userroles4 = UserRole.query.filter(UserRole.role_id == '4').filter(UserRole.if_usable=='1').all()
                        user3 = User.query.filter(User.disabled == False).filter(User.id.in_(i.user_id for i in userroles4)).all()###119用户
                        userroles5 = UserRole.query.filter(UserRole.role_id == '5').filter(UserRole.if_usable=='1').all()
                        user4 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles5)).all()##平台管理员
                        userroles6 = UserRole.query.filter(UserRole.role_id == '6').filter(UserRole.if_usable=='1').all()
                        user5 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles6)).all()###超级管理员
                        lst=list(set(user1+user2+user3+user4+user5))
                        for i in lst:
                            if i in user1:
                                messsgesend = MessageSend(user_id=i.id, role_id='1', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            elif i in user2:
                                messsgesend = MessageSend(user_id=i.id, role_id='2', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            elif i in user3:
                                messsgesend = MessageSend(user_id=i.id, role_id='4', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            elif i in user4:
                                messsgesend = MessageSend(user_id=i.id, role_id='5', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            else:
                                messsgesend = MessageSend(user_id=i.id, role_id='6', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            db.session.add(messsgesend)
                            if len(messsgesends) < 1:
                                db.session.commit()
                            else:
                                for i in messsgesends:
                                    if i.message_id != messsgesend.message_id and i.message_type != messsgesend.message_type and \
                                            i.user_id != messsgesend.user_id and i.role_id != messsgesend.role_id:
                                        db.session.commit()
                                    else:pass
                    else:pass
                else:
                        ins = Ins.query.filter(Ins.disabled == False).filter(Ins.id == useralarmrecord.ins_id).first()
                        if ins:
                            user1 = ins.user.all()##报警机构的用户
                            communitys = ins.community.all()
                            homes = []
                            for community in communitys:
                                homes.extend(community.homes.first())
                            homeuser = HomeUser.query.filter(HomeUser.home_id.in_(i.id for i in homes)).all()
                            user2 = User.query.filter(User.disabled==False).filter(User.id.in_(i.user_id for i in homeuser)).all()#####报警机构管辖下的家庭用户
                            userroles4 = UserRole.query.filter(UserRole.role_id == '4').filter(UserRole.if_usable=='1').all()
                            user3 = User.query.filter(User.disabled == False).filter(
                                User.id.in_(i.user_id for i in userroles4)).all()  ###119用户
                            userroles5 = UserRole.query.filter(UserRole.role_id == '5').filter(UserRole.if_usable=='1').all()
                            user4 = User.query.filter(User.disabled == False).filter(
                                User.id.in_(i.user_id for i in userroles5)).all()  ##平台管理员
                            userroles6 = UserRole.query.filter(UserRole.role_id == '6').filter(UserRole.if_usable=='1').all()
                            user5 = User.query.filter(User.disabled == False).filter(
                                User.id.in_(i.user_id for i in userroles6)).all()  ###超级管理员
                            lst = list(set(user1 + user2 + user3 + user4 + user5))
                            for i in lst:
                                if i in user1:
                                    if ins.type == '物业':
                                        messsgesend = MessageSend(user_id=i.id, role_id='2', message_id=useralarmrecord.id,
                                                         message_type='119报警', if_read=False, if_send=False)
                                    else:  messsgesend = MessageSend(user_id=i.id, role_id='3', message_id=useralarmrecord.id,
                                                              message_type='119报警', if_read=False, if_send=False)
                                elif i in user2:
                                    messsgesend = MessageSend(user_id=i.id, role_id='4', message_id=useralarmrecord.id,
                                                              message_type='119报警', if_read=False, if_send=False)
                                elif i in user3:
                                    messsgesend = MessageSend(user_id=i.id, role_id='5', message_id=useralarmrecord.id,
                                                              message_type='119报警', if_read=False, if_send=False)
                                else:  messsgesend = MessageSend(user_id=i.id, role_id='6', message_id=useralarmrecord.id,
                                                              message_type='119报警', if_read=False, if_send=False)
                                db.session.add(messsgesend)
                                if len(messsgesends) < 1:
                                    db.session.commit()
                                else:
                                    for i in messsgesends:
                                        if i.message_id != messsgesend.message_id and i.message_type != messsgesend.message_type and \
                                                i.user_id != messsgesend.user_id and i.role_id != messsgesend.role_id:
                                            db.session.commit()
                                        else:
                                            pass
            elif useralarmrecord.type == 1:
                if useralarmrecord.home_id:
                    home = Home.query.filter(Home.disabled==False).filter(Home.id==useralarmrecord.home_id).first()
                    if home:
                        if home:
                            h = []
                            _ = Home.query.filter(Home.disabled == False).all()
                            for j in _:
                                if getDistance(home.latitude, home.longitude, j.latitude,
                                               j.longitude) <= home.community.save_distance:
                                    h.append(j)
                            if len(h)>1:
                                h_u=HomeUser.query.filter(HomeUser.home_id.in_(i.id for i in h)).all()
                                if len(h_u)>1:
                                    user0=User.query.filter(User.id.in_(i.user_id for i in h_u)).filter(User.disabled==False).all()#报警的邻居
                                else:pass
                        else:pass
                        homeusers1 = HomeUser.query.filter(HomeUser.home_id == home.id).all()
                        user1 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in homeusers1)).all()  #####发送疏散家庭成员
                        user2 = []  ###发送疏散家庭上级机构
                        community = home.community
                        inses = community.ins.all()
                        for ins in inses:
                            user2.extend(ins.user.all())
                        userroles4 = UserRole.query.filter(UserRole.role_id == '4').all()
                        user3 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles4)).all()  ###119用户
                        userroles5 = UserRole.query.filter(UserRole.role_id == '5').all()
                        user4 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles5)).all()  ##平台管理员
                        userroles6 = UserRole.query.filter(UserRole.role_id == '6').all()
                        user5 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles6)).all()  ###超级管理员
                        lst=list(set(user0+user1+user2+user3+user4+user5))
                        for i in lst:
                            if i in [user1,user0]:
                                messsgesend = MessageSend(user_id=i.id, role_id='1', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            elif i in user2:
                                messsgesend = MessageSend(user_id=i.id, role_id='2', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            elif i in user3:
                                messsgesend = MessageSend(user_id=i.id, role_id='4', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            elif i in user4:
                                messsgesend = MessageSend(user_id=i.id, role_id='5', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            else:
                                messsgesend = MessageSend(user_id=i.id, role_id='6', message_id=useralarmrecord.id,

                                                           message_type='疏散消息', if_read=False, if_send=False)
                            db.session.add(messsgesend)
                            if len(messsgesends) < 1:
                                db.session.commit()
                            else:
                                for i in messsgesends:
                                    if i.message_id != messsgesend.message_id and i.message_type != messsgesend.message_type and \
                                            i.user_id != messsgesend.user_id and i.role_id != messsgesend.role_id:
                                        db.session.commit()
                                    else:
                                        pass
                    else:pass
                else:
                    ins = Ins.query.filter(Ins.disabled == False).filter(Ins.id == useralarmrecord.ins_id).first()
                    if ins:
                        user1 = ins.user.all()  ##报警机构的用户
                        communitys = ins.community.all()
                        homes = []
                        for community in communitys:
                            homes.extend(community.homes.first())
                        homeuser = HomeUser.query.filter(HomeUser.home_id.in_(i.id for i in homes)).all()
                        user2 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in homeuser)).all()  #####报警机构管辖下的家庭用户
                        userroles4 = UserRole.query.filter(UserRole.role_id == '4').all()
                        user3 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles4)).all()  ###119用户
                        userroles5 = UserRole.query.filter(UserRole.role_id == '5').all()
                        user4 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles5)).all()  ##平台管理员
                        userroles6 = UserRole.query.filter(UserRole.role_id == '6').all()
                        user5 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles6)).all()  ###超级管理员
                        lst=list(set(user1+user2+user3+user4+user5))
                        for i in lst:
                            if i in user1:
                                if ins.type == '物业':
                                    messsgesend = MessageSend(user_id=i.id, role_id='2', message_id=useralarmrecord.id,
                                                              message_type='疏散消息', if_read=False, if_send=False)
                                else:
                                    messsgesend = MessageSend(user_id=i.id, role_id='3', message_id=useralarmrecord.id,
                                                              message_type='疏散消息', if_read=False, if_send=False)
                            elif i in user2:
                                messsgesend = MessageSend(user_id=i.id, role_id='4', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            elif i in user3:
                                messsgesend = MessageSend(user_id=i.id, role_id='5', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            else:
                                messsgesend = MessageSend(user_id=i.id, role_id='6', message_id=useralarmrecord.id,
                                                      message_type='疏散消息', if_read=False, if_send=False)
                            db.session.add(messsgesend)
                            if len(messsgesends) < 1:
                                db.session.commit()
                            else:
                                for i in messsgesends:
                                    if i.message_id != messsgesend.message_id and i.message_type != messsgesend.message_type and \
                                            i.user_id != messsgesend.user_id and i.role_id != messsgesend.role_id:
                                        db.session.commit()
                                    else:
                                        pass
            elif useralarmrecord.type == 3:
                if useralarmrecord.home_id:
                    home = Home.query.filter(Home.disabled == False).filter(Home.id == useralarmrecord.home_id).first()
                    if home:
                        h=[]
                        _ = Home.query.filter(Home.disabled == False).all()
                        for k in _:
                            if getDistance(home.latitude, home.longitude, k.latitude,k.longitude) <= home.community.save_distance:
                                h.append(k)
                        if len(h) > 1:
                            h_u = HomeUser.query.filter(HomeUser.home_id.in_(i.id for i in h)).all()
                            if len(h_u) > 1:
                                user0 = User.query.filter(User.id.in_(i.user_id for i in h_u)).filter(
                                    User.disabled == False).all()  # 报警的邻居
                            else:
                                pass
                        else:
                            pass
                        homeusers1 = HomeUser.query.filter(HomeUser.home_id == home.id).all()
                        user1 = User.query.filter(User.disabled == False).filter(User.id.in_(i.user_id for i in homeusers1)).all()#####报警家庭成员
                        user2 = []###求救家庭上级机构
                        community = home.community
                        inses = community.ins.all()
                        for ins in inses:
                            user2.extend(ins.user.all())
                        userroles4 = UserRole.query.filter(UserRole.role_id == '4').all()
                        user3 = User.query.filter(User.disabled == False).filter(User.id.in_(i.user_id for i in userroles4)).all()###119用户
                        userroles5 = UserRole.query.filter(UserRole.role_id == '5').all()
                        user4 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles5)).all()##平台管理员
                        userroles6 = UserRole.query.filter(UserRole.role_id == '6').all()
                        user5 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles6)).all()###超级管理员
                        lst = list(set(user0+user1 + user2 + user3 + user4 + user5))
                        for i in lst:
                            if i in [user1,user0]:
                                messsgesend = MessageSend(user_id=i.id, role_id='1', message_id=useralarmrecord.id,
                                                          message_type='求救消息', if_read=False, if_send=False)
                            elif i in user2:
                                messsgesend = MessageSend(user_id=i.id, role_id='2', message_id=useralarmrecord.id,
                                                          message_type='求救消息', if_read=False, if_send=False)
                            elif i in user3:
                                messsgesend = MessageSend(user_id=i.id, role_id='4', message_id=useralarmrecord.id,
                                                          message_type='求救消息', if_read=False, if_send=False)
                            elif i in user4:
                                messsgesend = MessageSend(user_id=i.id, role_id='5', message_id=useralarmrecord.id,
                                                          message_type='求救消息', if_read=False, if_send=False)
                            else:
                                messsgesend = MessageSend(user_id=i.id, role_id='6', message_id=useralarmrecord.id,
                                                                  message_type='求救消息', if_read=False, if_send=False)
                            db.session.add(messsgesend)
                            if len(messsgesends) < 1:
                                db.session.commit()
                            else:
                                for i in messsgesends:
                                    if i.message_id != messsgesend.message_id and i.message_type != messsgesend.message_type and \
                                            i.user_id != messsgesend.user_id and i.role_id != messsgesend.role_id:
                                        db.session.commit()
                                    else:
                                        pass
                    else:pass
                else:
                    pass
            else:pass


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

