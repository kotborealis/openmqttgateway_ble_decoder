"""
This is a really quick and REALLY DIRTY implementation
of custom decoder for OpenMqttGateway, specifically for 
Xiaomi BLE devices with encrypted packets.

This was hacked together from a couple of different scripts
found on github.

It expects OpenMqttGateway device to run my modified firmware
https://github.com/1technophile/OpenMQTTGateway/commit/49d81e9f5ce21cf5c3aa922a8b713a9affa5d199

Publishes decoded packets into `home/mqttgateway_ble_decoder/{{MAC_WITHOUT_:}}` topic
"""

"""
Configuration section.
"""
import os

# Read macs and keys from OMG_BD_KEYS env variable,
# expects the following format: "MAC=key;MAC2=key2;"
keys_raw = [pair.split('=') for pair in os.environ["OMG_BD_KEYS"].split(';') if pair]

# Parse into bytes, collect into a dict
HEX_KEYS = {}
MACS = []
for mac, key in keys_raw:
    HEX_KEYS[bytes.fromhex(mac.replace(':', ''))] = bytes.fromhex(key)

# Address of local mqtt server
MQTT_IP = os.environ["OMG_BD_MQTT_IP"]
MQTT_PORT = os.environ.get("OMG_BD_MQTT_PORT", 1883)

from openmqttgateway_ble_decoder.helpers import to_mac
from openmqttgateway_ble_decoder.ble_parser import BleParser


def parse(mac, data, uuid):
    mac = bytes.fromhex(mac.replace(':', ''))
    data = bytes.fromhex(uuid[2:] + "0000" + data)

    ble = BleParser(aeskeys=HEX_KEYS)
    return ble.parse_advertisement(
                mac=mac,
                rssi=-67,
                service_class_uuid16=int(uuid[2:],16),
                service_class_uuid128=None,
                local_name="",
                service_data_list=[data]
                )

import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    for mac in HEX_KEYS:
        print(f"{to_mac(mac)}")
        client.subscribe(f"home/OMG_ESP32_BLE/BTtoMQTT/undecoded/{to_mac(mac)}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(payload)
    data = json.loads(payload)
    mac = data["id"]

    if not data.get("servicedata") or not data.get("servicedatauuid"):
        return

    res = parse(mac, data["servicedata"], data["servicedatauuid"])
    print(res)
    if not res or not res[0]:
        return

    client.publish(f"home/mqttgateway_ble_decoder/{mac.replace(':', '')}", payload=json.dumps(res[0]), qos=0, retain=False)

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_IP, MQTT_PORT, 60)

    client.loop_forever()

if __name__ == "__main__":
    main()