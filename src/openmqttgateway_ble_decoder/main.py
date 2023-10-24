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

import json
import logging
import os

import click
import paho.mqtt.client as mqttlib

from openmqttgateway_ble_decoder.ble_parser import BleParser
from openmqttgateway_ble_decoder.helpers import to_mac

_LOGGER = logging.getLogger(__name__)


def parse(keys, mac, data, uuid):
    mac = bytes.fromhex(mac.replace(":", ""))
    data = bytes.fromhex(uuid[2:] + "0000" + data)

    ble = BleParser(aeskeys=keys)
    return ble.parse_advertisement(
        mac=mac,
        rssi=-67,
        service_class_uuid16=int(uuid[2:], 16),
        service_class_uuid128=None,
        local_name="",
        service_data_list=[data],
    )


def on_connect(keys):
    def handler(client, userdata, flags, rc):
        for mac in keys:
            _LOGGER.info("Listening for device %s", to_mac(mac))
            client.subscribe(f"home/OMG_ESP32_BLE/BTtoMQTT/undecoded/{to_mac(mac)}")

    return handler


def on_message(keys):
    def handler(client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        mac = data["id"]

        if not data.get("servicedata") or not data.get("servicedatauuid"):
            return

        res = parse(keys, mac, data["servicedata"], data["servicedatauuid"])
        if not res or not res[0]:
            return

        _LOGGER.info("Parsed payload: %s", res)

        client.publish(
            f"home/mqttgateway_ble_decoder/{mac.replace(':', '')}",
            payload=json.dumps(res[0]),
            qos=0,
            retain=False,
        )

    def handler_with_errors(*args, **kwargs):
        try:
            handler(*args, **kwargs)
        except Exception:
            _LOGGER.exception("Failed to handle message")

    return handler_with_errors


@click.command()
@click.option(
    "--mqtt",
    required=True,
    type=str,
    help="MQTT server ip",
)
@click.option(
    "--mqtt-port",
    required=False,
    type=int,
    default=1883,
    help="MQTT server port",
)
@click.option(
    "--mqtt-keepalive",
    required=False,
    type=int,
    default=60,
    help="MQTT connection keepalive param",
)
@click.option(
    "--mqtt-username",
    required=False,
    type=str,
    default=lambda: os.environ.get("OMG_BD_MQTT_USERNAME", None),
    help="MQTT username",
)
@click.option(
    "--mqtt-password",
    required=False,
    type=str,
    default=lambda: os.environ.get("OMG_BD_MQTT_PASSWORD", None),
    help="MQTT password",
)
@click.option(
    "--device",
    required=True,
    type=(str, str),
    multiple=True,
    help="Macs and decryption keys",
)
def main(mqtt, mqtt_port, mqtt_keepalive, mqtt_username, mqtt_password, device):
    keys = {}
    for mac, key in device:
        keys[bytes.fromhex(mac.replace(":", ""))] = bytes.fromhex(key)

    client = mqttlib.Client()

    if mqtt_username and mqtt_password:
        client.username_pw_set(mqtt_username, mqtt_password)

    client.on_connect = on_connect(keys)
    client.on_message = on_message(keys)

    _LOGGER.info("Connecting to %s:%s", mqtt, mqtt_port)
    client.connect(mqtt, mqtt_port, mqtt_keepalive)

    client.loop_forever()


if __name__ == "__main__":
    main()
