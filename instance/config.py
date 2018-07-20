import os
import platform

DEBUG = False

# System
VERSION = '0.0.5'
OS = platform.system()
DIR = os.getcwd()

##APP
# SESSION_COOKIE_SECURE=True
SECRET_KEY = 'mY@Ccrzx4v&f4yPGv2pXTWDKsskvTE5Z'

##CSRF
WTF_CSRF_ENABLED = False

## 使用docker创建一个本地调测使用的mysql

# sudo docker run --name yiyiwei-db -d --env MYSQL_ROOT_PASSWORD=yangjiawei --env MYSQL_DATABASE=yiyiwei --env MYSQL_USER=yiyiwei --env MYSQL_PASSWORD=yiyiwei -p 3306:3306  mysql:5.5

##Sqlalchemy
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:yangjiawei@47.91.222.196:3306/firefighting'
#SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:root@127.0.0.1:3306/firefighting1'
SQLALCHEMY_TRACK_MODIFICATIONS = True

##Cache
CACHE_TYPE = 'simple'


# Restplus
RESTPLUS_MASK_SWAGGER = False
SWAGGER_UI_JSONEDITOR = True
SWAGGER_UI_LANGUAGES = ['zh-cn']

# UPLOADS
UPLOADED_IMAGES_DEST = DIR + '/app/static/upload/'
UPLOAD_FOLDER = DIR + '/app/static/upload/'
UPLOADED_URL = '/static/upload/'
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4']
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024

## Babel
BABEL_DEFAULT_LOCALE = 'zh_CN'

## JWT
JWT_PK = DIR + '/instance/jwt_rsa_private_key.pem'
JWT_PUK = DIR + '/instance/jwt_rsa_public_key.pem'
JWT_EXP=60*60*24*30
JWT_NBF=60

CORS_RESOURCES = {r"/api/*": {"origins": "*"}}

## JPUSH

JPUSH_APP_KEY = 'f49b24f54dfff2cc6454f6ef'
JPUSH_MASTER_SECRET = 'ba478d742873ce02a89d88d7'

#getui
# APP_KEY = 'FUvUQj6C2J69HKCGDKDrc2'
# APP_ID = '1GIGIfZvFyA6iMf5kq3rV3'
# MASTER_SECRET = '7MmIrGUUL16f8RF2OTwFE4'
# APP_SCRET = 'dQ25Qzxkrb8avPi3GyeNLA'
APP_ID = '2B923TWif8AUAITFKi8DK1'
APP_SECRET = 'HnDWnPyb3u9AerwLqzEpQ9'
APP_KEY = 'Q44tX55Jbv8AKOYJOJyrF'
MASTER_SECRET= 'KyHs20ukV5AnGIve7nbIC8'
##mqtt
MQTT_BROKER_URL = '47.91.222.196'
#MQTT_BROKER_URL = '127.0.0.1'
MQTT_BROKER_PORT = 1883
MQTT_USERNAME = 'admin'
#MQTT_PASSWORD = 'public'
MQTT_PASSWORD = 'xiaofang@HT'
MQTT_KEEPALIVE = 5
MQTT_TLS_ENABLED = False
MQTT_LAST_WILL_QOS = 2
###append
PRE_FIX='http://47.91.222.196'

