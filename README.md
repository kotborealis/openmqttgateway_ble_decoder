# OpenMqttGateway BLE decoder

This is a really quick and REALLY DIRTY implementation
of custom decoder for OpenMqttGateway, specifically for 
Xiaomi BLE devices with encrypted packets.

This was hacked together from a couple of different scripts
found on github.

It expects OpenMqttGateway device to run [my modified firmware](https://github.com/1technophile/OpenMQTTGateway/commit/49d81e9f5ce21cf5c3aa922a8b713a9affa5d199).

Publishes decoded packets into `home/mqttgateway_ble_decoder/{{MAC_WITHOUT_:}}` topic.

## Configuration

Configured by env vars:

* `OMG_BD_KEYS`: pairs of mac adresses and decryption keys in format `MAC=key;MAC2=key2;`.
* `OMG_BD_MQTT_IP`: ip of mqtt server.
* `OMG_BD_MQTT_PORT`: port of mqtt server.
