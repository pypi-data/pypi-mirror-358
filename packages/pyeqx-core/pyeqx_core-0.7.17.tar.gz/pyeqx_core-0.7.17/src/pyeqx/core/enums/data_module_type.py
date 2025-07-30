from enum import Enum


class DataModuleType(Enum):
    Default = ""
    File = "file"
    Database = "database"
    Api = "api"
    Stream = "stream"
