from dataclasses import dataclass, field
from typing import Literal
from python_swos_lite.endpoint import SwOSLiteEndpoint, endpoint

# Address aquistion options matching the API’s integer order
AddressAquistion = Literal["DHCP_FALLBACK", "STATIC", "DHCP"]

@endpoint("sys.b")
@dataclass
class SystemEndpoint(SwOSLiteEndpoint):
    """Represents the endpoint with system information."""

    # General
    addressAquistion: AddressAquistion = field(metadata={"name": "i0a", "type": "option", "options": AddressAquistion})
    staticIP: str = field(metadata={"name": "i09", "type": "ip"})
    ip: str = field(metadata={"name": "i02", "type": "ip"})
    identity: str = field(metadata={"name": "i05", "type": "str"})
    serial: str = field(metadata={"name": "i04", "type": "str"})
    mac: str = field(metadata={"name": "i03", "type": "mac"})
    model: str = field(metadata={"name": "i07", "type": "str"})
    version: str = field(metadata={"name": "i06", "type": "str"})
    uptime: int = field(metadata={"name": "i01", "type": "int"})

    # Health
    cpuTemp: int = field(metadata={"name": "i22", "type": "int"})
    psu1Current: int = field(metadata={"name": "i16", "type": "int"})
    psu1Voltage: int = field(metadata={"name": "i15", "type": "int", "scale": 100})
    psu2Current: int = field(metadata={"name": "i1f", "type": "int"})
    psu2Voltage: int = field(metadata={"name": "i1e", "type": "int", "scale": 100})
    power_consumption: int = field(metadata={"name": "i26", "type": "int", "scale": 10})
