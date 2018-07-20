import json
from datetime import datetime, timedelta
import dateutil
from flask import json
from app.ext import mqtt, db
from app.models import Gateway, Sensor, SensorHistory, SensorAlarm, AlarmHandle
from app.ext import _


def gateway_info(client, userdata ,message):
    p = json.loads(message.payload)
    gateway_id = p.get('gateway_id')
    sensors = p.get('sensors')
    #####
    with client.app.app_context():
        g = Gateway.query.filter(Gateway.id==gateway_id).first()
        try:
            t = _.get(gateway_id)-timedelta(seconds=30)
            v = []
            for j in _.values():
                if j<t:
                    v.append(j)#####获取时间超过30s的时间
                else:pass
            __ = dict([val, key] for key, val in _.items())#字典交换建和值
            for i in _:
                g1 = Gateway.query.filter_by(id=__.get(i)).first()#获取时间超过的网关
                g1.usable=False
                db.session.commit()
        except Exception as e:
            print(e)
        if g is None:
            g = Gateway(id=gateway_id)
            db.session.add(g)
            db.session.commit()
        elif not g.usable:
            g.usable=True
            db.session.commit()
        sensors_db_all =set([i[0] for i in (Sensor.query.filter(Sensor.gateway_id==gateway_id).filter(Sensor.online==True).with_entities(Sensor.id).all())])
        lst=[]
        for i in sensors:
            lst.append(i.get('id'))
        sensors_mq_all = set(lst)
        sensors_to_db = list(sensors_mq_all^(sensors_db_all&sensors_mq_all))
        sensors_back_to_db = list(sensors_db_all^(sensors_db_all&sensors_mq_all))
        if sensors_to_db:
            for sensors_id in sensors_to_db:
                s = Sensor.query.filter(Sensor.id==sensors_id).first()
                if not s:
                    sensor = Sensor(id=sensors_id, online=True, gateway_id=gateway_id, sensor_place='暂无')
                    if sensors_id in ['S0001','S0999']:
                        sensor.sensor_type = 0
                    elif sensors_id in ['S1001','S1999']:
                        sensor.sensor_type = 1
                        sensor.max_value = 1
                        sensor.set_type =0
                    elif sensors_id in ['S2001', 'S2999']:
                        sensor.sensor_type = 2
                    elif sensors_id in ['S3001', 'S3999']:
                        sensor.sensor_type = 3
                        sensor.max_value = 10
                        sensor.set_type = 0
                    else: sensor.sensor_type = 4
                    db.session.add(sensor)
                    db.session.commit()
                else: s.online = True
                db.session.commit()
            else:pass
        else:pass
        if sensors_back_to_db:
            for sensor_id in sensors_back_to_db:
                sensor = Sensor.query.filter(Sensor.id == sensor_id).filter(Sensor.online==True).first()
                if sensor:
                    sensor.online = False
                    db.session.commit()
                else:pass
        else:pass
    _[gateway_id] = p.get('time')
    mqtt.subscribe(f'{gateway_id}/data')
    mqtt.client.message_callback_add(f'{gateway_id}/data', gateway_data)


def gateway_data(client,userdata, message):
    p = json.loads(message.payload)
    lst = p.get("data")
    time = dateutil.parser.parse(p.get("time"))
    with client.app.app_context():
        for i in lst:
            if Sensor.query.filter_by(id=i.get('id')).filter(Sensor.online==True).first().gateway.useable:###网管不可用不再写入历史记录
                sensorhistory = SensorHistory()
                if i['id']>='S0001'and i['id']<='S0999':
                     sensorhistory.sensor_id = i['id']
                     sensorhistory.time = time
                     sensorhistory.sensor_value = i.get('value')
                     if int(sensorhistory.sensor_value) >0:
                        sensorhistory.sensor_state = '异常'
                        sensoralarm = SensorAlarm(sensor_id=i['id'], sensor_type=0, alarm_time=time,alarm_value=i.get('value'), gateway_id=Sensor.query.get(i['id']).gateway_id)
                        s_t=SensorHistory.query.filter(SensorHistory.sensor_id==i.get('id')).filter(SensorHistory.time<sensorhistory.time).filter(SensorHistory.time.desc()).first()
                        if not int(s_t.sensor_vale) or not s_t:
                            db.session.add(sensoralarm)#第一次立刻生成报警供推送
                            db.session.commit()
                        elif sensorhistory.time-timedelta(minutes=5) >= s_t.time:
                            db.session.add(sensoralarm)
                            db.session.commit()#超过五分钟则再次声称报警供推送
                        else:pass
                     else:
                         s=SensorAlarm.query.filter(SensorAlarm.sensor_id==i.get('id')).filter(SensorAlarm.alarm_time<sensorhistory.time).filter(SensorAlarm.alarm_time.desc()).first()
                         if not int(sensorhistory.sensor_value) or s.is_confirm:
                             sensorhistory.sensor_state = '正常'#上来有正常数据，则传感器状态恢复正常
                             db.session.commit()
                         else:pass
                elif i.get('id')>='S1001'and i.get('id')<='S1999':
                    sensorhistory.sensor_id = i['id']
                    sensorhistory.time = time
                    sensorhistory.sensor_value = i.get('value')
                    if int(sensorhistory.sensor_value) > 0:
                        sensorhistory.sensor_state = '异常'
                        sensoralarm = SensorAlarm(sensor_id=i['id'], sensor_type=1, var_type='温度', alarm_value=i.get('value'), unit='℃',alarm_time=time, gateway_id=Sensor.query.get(i['id']).gateway_id )
                        db.session.add(sensoralarm)
                        sm = SensorHistory.query.filter(SensorHistory.sensor_id == i['id']).filter(SensorHistory.time.between(time, time-timedelta(minutes=10)))
                        count = 1
                        for i in sm:
                            if int(i.sensor_value) > 0:
                                count += 1
                        if count > 9:
                            db.session.commit()
                        else:
                            pass
                    else:
                        sensorhistory.sensor_state = '正常'
                elif i['id']>='S2001'and i['id']<='S2999':
                    sensorhistory.sensor_id = i['id']
                    sensorhistory.time = time
                    sensorhistory.sensor_value = i.get('value')
                    if int(sensorhistory.sensor_value) == 1:
                         sensorhistory.sensor_state = '异常'
                         sensoralarm = SensorAlarm(sensor_id=i['id'], sensor_type=2,  alarm_time=time, alarm_value=i.get('value'), gateway_id=Sensor.query.get(i['id']).gateway_id)
                         s_t = SensorHistory.query.filter(SensorHistory.sensor_id == i.get('id')).filter(
                            SensorHistory.time < sensorhistory.time).filter(SensorHistory.time.desc()).first()
                         if not int(s_t.sensor_vale) or not s_t:
                            db.session.add(sensoralarm)
                            db.session.commit()
                         elif sensorhistory.time-timedelta(minutes=5) >= s_t.time:
                            db.session.add(sensoralarm)
                            db.session.commit()
                         else:pass
                    else:
                        s = SensorAlarm.query.filter(SensorAlarm.sensor_id == i.get('id')).filter(
                            SensorAlarm.alarm_time < sensorhistory.time).filter(SensorAlarm.alarm_time.desc()).first()
                        if not int(sensorhistory.sensor_value) or s.is_confirm:
                            sensorhistory.sensor_state = '正常'
                            db.session.commit()
                elif i['id'] >= 'S3001' and i['id']<= 'S3999':
                    sensorhistory.sensor_id = i['id']
                    sensorhistory.time = time
                    sensorhistory.sensor_value = float(i.get('value'))/100
                    if float(sensorhistory.sensor_value) > float(Sensor.query.get(i['id']).max_value):
                      sensorhistory.sensor_state = '异常'
                      sensoralarm = SensorAlarm(sensor_id=i['id'], sensor_type=3, alarm_value=float(i.get('value'))/100, var_type='电流',unit='A', alarm_time=time, gateway_id=Sensor.query.get(i['id']).gateway_id)
                      s_t = SensorHistory.query.filter(SensorHistory.sensor_id == i.get('id')).filter(
                          SensorHistory.time < sensorhistory.time).filter(SensorHistory.time.desc()).first()
                      if not int(s_t.sensor_vale) or not s_t:
                          db.session.add(sensoralarm)  # 第一次立刻生成报警供推送
                          db.session.commit()
                      elif sensorhistory.time - timedelta(minutes=5) >= s_t.time:
                          db.session.add(sensoralarm)
                          db.session.commit()  # 超过五分钟则再次声称报警供推送
                      else:
                          pass
                    else:
                        s = SensorAlarm.query.filter(SensorAlarm.sensor_id == i.get('id')).filter(
                            SensorAlarm.alarm_time < sensorhistory.time).filter(SensorAlarm.alarm_time.desc()).first()
                        if not int(sensorhistory.sensor_value) or s.is_confirm:
                            sensorhistory.sensor_state = '正常'  # 上来有正常数据，则传感器状态恢复正常
                            db.session.commit()
                        else:
                            pass
                    #   if len(SensorHistory.query.filter(SensorHistory.sensor_id==i.get('id')).
                    #                  filter(SensorHistory.sensor_value==str(float(i.get('value'))/100)).
                    #                  filter(time-SensorHistory.time<timedelta(seconds=7)).order_by(SensorHistory.time.desc()).all())>=2#通一个值，并且6秒内有两次数据
                    #       db.session.add(sensoralarm)
                    #       db.session.commit()
                    #   else:
                    #     pass
                    # else: sensorhistory.sensor_state = '正常'
                    # db.session.commit()
                else:
                    sensorhistory.sensor_id = i['id']
                    sensorhistory.time = time
                    sensorhistory.sensor_value = i.get('value')
                    if int(sensorhistory.sensor_value) > 0:
                        sensorhistory.sensor_state = '异常'
                        sensoralarm = SensorAlarm(sensor_id=i['id'], sensor_type=4, alarm_time=time, alarm_value= i.get('value'),gateway_id=Sensor.query.get(i['id']).gateway_id)
                        s_t = SensorHistory.query.filter(SensorHistory.sensor_id == i.get('id')).filter(
                            SensorHistory.time < sensorhistory.time).filter(SensorHistory.time.desc()).first()
                        if not int(s_t.sensor_vale) or not s_t:
                            db.session.add(sensoralarm)  # 第一次立刻生成报警供推送
                            db.session.commit()
                        elif sensorhistory.time - timedelta(minutes=5) >= s_t.time:
                            db.session.add(sensoralarm)
                            db.session.commit()  # 超过五分钟则再次声称报警供推送
                        else:
                            pass
                    else:
                        s = SensorAlarm.query.filter(SensorAlarm.sensor_id == i.get('id')).filter(
                            SensorAlarm.alarm_time < sensorhistory.time).filter(SensorAlarm.alarm_time.desc()).first()
                        if not int(sensorhistory.sensor_value) or s.is_confirm:
                            sensorhistory.sensor_state = '正常'  # 上来有正常数据，则传感器状态恢复正常
                            db.session.commit()
                        else:
                            pass
                # sensoralarm = SensorAlarm.query.filter(SensorAlarm.sensor_id == i['id']).first()
                # if sensoralarm:
                #     alarmhandler = AlarmHandle(type='0', handle_type='100', reference_message_id=sensoralarm.id,
                #                                handle_time=datetime.now())
                #     db.session.add(alarmhandler)
                #     db.session.commit()
            else:pass # else:pass
    return None, 200




