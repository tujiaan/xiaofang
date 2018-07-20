from .apscheduler import scheduler
from .cache import cache
from .cors import cors
from .csrf import csrf
from .db import db
from .jpush import Jpush
from .logger import logger
from .getui import getui
from .mqtt import mqtt

_ = {}
def ext_init(app):
    db.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    logger.init_app(app)
    cors.init_app(app)
    Jpush.init_app(app)
    scheduler.init_app(app)
    getui.init_app(app)
    mqtt.init_app(app)

