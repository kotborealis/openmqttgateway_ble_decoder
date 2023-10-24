"""Parser for passive BLE advertisements."""
import logging
from typing import Optional

from openmqttgateway_ble_decoder.helpers import to_mac, to_unformatted_mac
from openmqttgateway_ble_decoder.xiaomi import parse_xiaomi

_LOGGER = logging.getLogger(__name__)


class BleParser:
    """Parser for BLE advertisements"""

    def __init__(
        self,
        report_unknown=False,
        discovery=True,
        filter_duplicates=False,
        sensor_whitelist=None,
        tracker_whitelist=None,
        report_unknown_whitelist=None,
        aeskeys=None,
    ):
        self.report_unknown = report_unknown
        self.discovery = discovery
        self.filter_duplicates = filter_duplicates
        if sensor_whitelist is None:
            self.sensor_whitelist = []
        else:
            self.sensor_whitelist = sensor_whitelist
        if tracker_whitelist is None:
            self.tracker_whitelist = []
        else:
            self.tracker_whitelist = tracker_whitelist
        if report_unknown_whitelist is None:
            self.report_unknown_whitelist = []
        else:
            self.report_unknown_whitelist = report_unknown_whitelist
        if aeskeys is None:
            self.aeskeys = {}
        else:
            self.aeskeys = aeskeys

        self.lpacket_ids = {}
        self.movements_list = {}
        self.adv_priority = {}
        self.no_key_message = []

    def parse_advertisement(
        self,
        mac: bytes,
        rssi: int,
        service_class_uuid16: Optional[int] = None,
        service_class_uuid128: Optional[bytes] = None,
        local_name: Optional[str] = "",
        service_data_list: Optional[list] = None,
        man_spec_data_list: Optional[list] = None,
    ):
        """parse BLE advertisement"""
        sensor_data = None
        tracker_data: Optional[dict] = None
        unknown_sensor = False
        if service_data_list is None:
            service_data_list = []
        if man_spec_data_list is None:
            man_spec_data_list = []

        while not sensor_data:
            if service_data_list:
                for service_data in service_data_list:
                    # parse data for sensors with service data
                    uuid16 = service_class_uuid16
                    if uuid16 == 0xFE95:
                        # UUID16 = Xiaomi
                        sensor_data = parse_xiaomi(self, service_data, mac, rssi)
                        break
                    else:
                        unknown_sensor = True
            else:
                unknown_sensor = True
            if unknown_sensor and self.report_unknown == "Other":
                _LOGGER.info(
                    "Unknown advertisement received for mac: %s"
                    "service data: %s"
                    "manufacturer specific data: %s"
                    "local name: %s"
                    "UUID16: %s,"
                    "UUID128: %s",
                    to_mac(mac),
                    service_data_list,
                    man_spec_data_list,
                    local_name,
                    service_class_uuid16,
                    service_class_uuid128,
                )
            break

        # check for monitored device trackers
        tracker_id = (
            tracker_data["tracker_id"]
            if tracker_data and "tracker_id" in tracker_data
            else mac
        )
        if tracker_id in self.tracker_whitelist:
            if tracker_data is not None:
                tracker_data.update({"is connected": True})
            else:
                tracker_data = {
                    "is connected": True,
                    "mac": to_unformatted_mac(mac),
                    "rssi": rssi,
                }
        else:
            tracker_data = None

        if self.report_unknown_whitelist:
            if tracker_id in self.report_unknown_whitelist:
                _LOGGER.info(
                    "BLE advertisement received from MAC/UUID %s: "
                    "service data: %s"
                    "manufacturer specific data: %s"
                    "local name: %s"
                    "UUID16: %s,"
                    "UUID128: %s",
                    tracker_id.hex(),
                    service_data_list,
                    man_spec_data_list,
                    local_name,
                    service_class_uuid16,
                    service_class_uuid128,
                )

        return sensor_data, tracker_data
