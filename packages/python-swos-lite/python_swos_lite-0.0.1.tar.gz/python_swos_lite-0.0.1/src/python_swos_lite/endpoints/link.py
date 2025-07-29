from dataclasses import dataclass, field
from typing import List, Literal
from python_swos_lite.endpoint import SwOSLiteEndpoint, endpoint

# Speed options matching the API’s integer order
Speed = Literal["10M", "100M", "1G", "10G", "200M", "2.5G", "5G", None]

@endpoint("link.b")
@dataclass
class LinkEndpoint(SwOSLiteEndpoint):
    """Represents the endpoint providing basic information for each individual port."""
    enabled: List[bool] = field(metadata={"name": "i01", "type": "bool"})
    name: List[str] = field(metadata={"name": "i0a", "type": "str"})
    linkState: List[bool] = field(metadata={"name": "i06", "type": "bool"})
    autoNegotiation: List[bool] = field(metadata={"name": "i02", "type": "bool"})
    speed: List[Speed] = field(metadata={"name": "i08", "type": "option", "options": Speed})
    manSpeed: List[Speed] = field(metadata={"name": "i05", "type": "option", "options": Speed})
    fullDuplex: List[bool] = field(metadata={"name": "i07", "type": "bool"})
    manFullDuplex: List[bool] = field(metadata={"name": "i03", "type": "bool"})
    flowControlRx: List[bool] = field(metadata={"name": "i12", "type": "bool"})
    flowControlTx: List[bool] = field(metadata={"name": "i16", "type": "bool"})
