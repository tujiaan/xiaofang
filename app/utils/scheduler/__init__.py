from app.ext import scheduler
from .test import BuiltSensorSendMessage, BuiltUserSendMessage, SendMessage, OpenSensor, builtusersendmessage


def scheduler_init_job(app):
     scheduler.add_job('test_scheduler', BuiltSensorSendMessage,max_instances=10, trigger='interval', seconds=10, args=[app])
     scheduler.add_job('test_scheduler1', builtusersendmessage,max_instances=10, trigger='interval', seconds=15, args=[app])
     #scheduler.add_job('test_scheduler2', BuiltUserSendMessage, trigger='interval', seconds=12, args=[app])
     scheduler.add_job('test_scheduler3', SendMessage, max_instances=10,trigger='interval', seconds=16, args=[app])
     scheduler.add_job('test_schedule4', OpenSensor, max_instances=10,trigger='interval', minutes=13, args=[app])
     scheduler.start()