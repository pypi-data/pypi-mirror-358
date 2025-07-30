from enum import Enum


class DataType(Enum):
    Default = ""
    LocalPath = "local-path"
    Nfs = "nfs"
    S3 = "s3"
    Sftp = "sftp"
    Impala = "impala"
    Api = "api"
    MongoDB = "mongodb"
    AzureBlobStorage = "azure-blob-storage"
    AzureAdlsGen2Storage = "azure-adls-gen2-storage"
    MSSql = "mssql"
    PostgreSql = "postgresql"
    Cassandra = "cassandra"
    Kafka = "kafka"
