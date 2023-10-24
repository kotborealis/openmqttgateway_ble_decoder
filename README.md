# OpenMqttGateway BLE decoder

This is a really quick and REALLY DIRTY implementation
of custom decoder for OpenMqttGateway, specifically for 
Xiaomi BLE devices with encrypted packets.

This was hacked together from a couple of different scripts
found on github.

It expects OpenMqttGateway device to run [my modified firmware](https://github.com/1technophile/OpenMQTTGateway/commit/49d81e9f5ce21cf5c3aa922a8b713a9affa5d199).

Publishes decoded packets into `home/mqttgateway_ble_decoder/{{MAC_WITHOUT_:}}` topic.

## Usage

```
Usage: openmqttgateway_ble_decoder [OPTIONS]

Options:
  --mqtt TEXT               MQTT server ip  [required]
  --mqtt-port INTEGER       MQTT server port
  --mqtt-keepalive INTEGER  MQTT connection keepalive param
  --mqtt-username TEXT      MQTT username
  --mqtt-password TEXT      MQTT password
  --device <TEXT TEXT>...   Macs and decryption keys  [required]
  --help                    Show this message and exit.
```