from dataclasses import dataclass
from typing import Any

from pyeqx.core.common import from_dict, from_str
from pyeqx.core.models.storage.properties.data_properties import DataProperties


@dataclass
class KafkaDataProperties(DataProperties):
    topic: str
    bootstrap_servers: str
    sasl_user: str
    sasl_password: str
    sasl_mechanism: str
    security_protocol: str
    extras: dict[str, Any]

    def __init__(
        self,
        topic,
        bootstrap_servers,
        sasl_user,
        sasl_password,
        sasl_mechanism,
        security_protocol,
        extras,
    ):
        parsed_obj = {
            "topic": topic,
            "bootstrap_servers": bootstrap_servers,
            "sasl_user": sasl_user,
            "sasl_password": sasl_password,
            "sasl_mechanism": sasl_mechanism,
            "security_protocol": security_protocol,
            "extras": extras,
        }
        super().__init__(parsed_obj)

    @staticmethod
    def from_dict(obj: Any) -> "KafkaDataProperties":
        assert isinstance(obj, dict)

        topic = from_str(obj.get("topic"))
        bootstrap_servers = from_str(obj.get("bootstrapServers"))
        sasl_user = from_str(obj.get("saslUser"))
        sasl_password = from_str(obj.get("saslPassword"))
        sasl_mechanism = from_str(obj.get("saslMechanism"))
        security_protocol = from_str(obj.get("securityProtocol"))
        extras = from_dict(obj.get("extras")) if "extras" in obj else {}

        return KafkaDataProperties(
            topic=topic,
            bootstrap_servers=bootstrap_servers,
            sasl_user=sasl_user,
            sasl_password=sasl_password,
            sasl_mechanism=sasl_mechanism,
            security_protocol=security_protocol,
            extras=extras,
        )

    def to_dict(self) -> dict:
        result: dict = {}
        result["topic"] = from_str(self.topic)
        result["bootstrapServers"] = from_str(self.bootstrap_servers)
        result["saslUser"] = from_str(self.sasl_user)
        result["saslPassword"] = from_str(self.sasl_password)
        result["saslMechanism"] = from_str(self.sasl_mechanism)
        result["securityProtocol"] = from_str(self.security_protocol)
        result["extras"] = from_dict(self.extras)
        return result

    def from_properties(self) -> "KafkaDataProperties":
        return KafkaDataProperties(
            topic=self.topic,
            bootstrap_servers=self.bootstrap_servers,
            sasl_user=self.sasl_user,
            sasl_password=self.sasl_password,
            sasl_mechanism=self.sasl_mechanism,
            security_protocol=self.security_protocol,
            extras=self.extras,
        )
