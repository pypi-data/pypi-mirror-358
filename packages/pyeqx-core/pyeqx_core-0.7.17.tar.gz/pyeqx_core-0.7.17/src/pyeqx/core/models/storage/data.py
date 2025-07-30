from dataclasses import dataclass
from typing import Optional, Type, TypeVar, cast

from pyeqx.core.common import to_dict
from pyeqx.core.enums import DataType
from pyeqx.core.models.storage.properties import (
    DataProperties,
    LocalPathDataProperties,
    NfsDataProperties,
    S3DataProperties,
    SftpDataProperties,
    ImpalaDataProperties,
    ApiDataProperties,
    AzureBlobStorageDataProperties,
    AzureAdlsGen2StorageDataProperties,
    MongoDataProperties,
    MSSqlDataProperties,
    PostgreSqlDataProperties,
    CassandraDataProperties,
    KafkaDataProperties,
)


T = TypeVar("T", bound=DataProperties)


@dataclass
class Data:
    type: DataType
    properties: DataProperties

    def get_properties(self, cls: Optional[Type[T]] = None) -> T:
        props = self.properties

        if cls is None:
            return props

        if self.type == DataType.LocalPath:
            props = LocalPathDataProperties.from_properties(self.properties)
        elif self.type == DataType.S3:
            props = S3DataProperties.from_properties(self.properties)
        elif self.type == DataType.Nfs:
            props = NfsDataProperties.from_properties(self.properties)
        elif self.type == DataType.Sftp:
            props = SftpDataProperties.from_properties(self.properties)
        elif self.type == DataType.Impala:
            props = ImpalaDataProperties.from_properties(self.properties)
        elif self.type == DataType.Api:
            props = ApiDataProperties.from_properties(self.properties)
        elif self.type == DataType.MongoDB:
            props = MongoDataProperties.from_properties(self.properties)
        elif self.type == DataType.AzureBlobStorage:
            props = AzureBlobStorageDataProperties.from_properties(self.properties)
        elif self.type == DataType.AzureAdlsGen2Storage:
            props = AzureAdlsGen2StorageDataProperties.from_properties(self.properties)
        elif self.type == DataType.MSSql:
            props = MSSqlDataProperties.from_properties(self.properties)
        elif self.type == DataType.PostgreSql:
            props = PostgreSqlDataProperties.from_properties(self.properties)
        elif self.type == DataType.Cassandra:
            props = CassandraDataProperties.from_properties(self.properties)
        elif self.type == DataType.Kafka:
            props = KafkaDataProperties.from_properties(self.properties)

        if isinstance(props, cls):
            return cast(cls, props)

        return props

    @staticmethod
    def from_dict(obj: any) -> "Data":
        assert isinstance(obj, dict)
        parse_type = DataType(obj.get("type"))

        if parse_type == DataType.LocalPath:
            parse_properties = LocalPathDataProperties.from_dict(obj.get("properties"))
        elif parse_type == DataType.S3:
            parse_properties = S3DataProperties.from_dict(obj.get("properties"))
        elif parse_type == DataType.Nfs:
            parse_properties = NfsDataProperties.from_dict(obj.get("properties"))
        elif parse_type == DataType.Sftp:
            parse_properties = SftpDataProperties.from_dict(obj.get("properties"))
        elif parse_type == DataType.Impala:
            parse_properties = ImpalaDataProperties.from_dict(obj.get("properties"))
        elif parse_type == DataType.Api:
            parse_properties = ApiDataProperties.from_dict(obj.get("properties"))
        elif parse_type == DataType.MongoDB:
            parse_properties = MongoDataProperties.from_dict(obj.get("properties"))
        elif parse_type == DataType.AzureBlobStorage:
            parse_properties = AzureBlobStorageDataProperties.from_dict(
                obj.get("properties")
            )
        elif parse_type == DataType.AzureAdlsGen2Storage:
            parse_properties = AzureAdlsGen2StorageDataProperties.from_dict(
                obj.get("properties")
            )
        elif parse_type == DataType.MSSql:
            parse_properties = MSSqlDataProperties.from_dict(obj.get("properties"))
        elif parse_type == DataType.PostgreSql:
            parse_properties = PostgreSqlDataProperties.from_dict(obj.get("properties"))
        elif parse_type == DataType.Cassandra:
            parse_properties = CassandraDataProperties.from_dict(obj.get("properties"))
        elif parse_type == DataType.Kafka:
            parse_properties = KafkaDataProperties.from_dict(obj.get("properties"))
        else:
            parse_properties = obj.get("properties")

        return Data(parse_type, parse_properties)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = to_dict(DataType, self.type)
        result["properties"] = to_dict(DataProperties, self.properties)
