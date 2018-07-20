from app.ext import mqtt
from .handles import gateway_info, gateway_data

app=None


def mqtt_register(b):
    mqtt.client.app = b
    mqtt.subscribe(topic='gatewayinfo')
    # mqtt.subscribe(topic='+/data')
    mqtt.client.message_callback_add('gatewayinfo', gateway_info)
    # mqtt.client.message_callback_add('+/data', gateway_data)

