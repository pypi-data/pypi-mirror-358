import os
import re
from typing import Optional
from urllib.parse import urlparse

from adlfs import AzureBlobFileSystem
from azure.core.credentials import AzureNamedKeyCredential
from azure.storage.blob import BlobServiceClient

from pyeqx.common.result import FunctionExecuteResult
from pyeqx.core import Operation
from pyeqx.core.models.module.properties import FileDataModuleProperties
from pyeqx.core.models.storage.properties import AzureAdlsGen2StorageDataProperties
from pyeqx.core.utils import build_path

from pyeqx.azure.constants import (
    AZURE_SPARK_OPTION_PATTERN,
    AZURE_STORAGE_CONTAINER_PATTERN,
    AZURE_STORAGE_EXCEPTION_ACCOUNT_KEY_OR_NAME_NOT_FOUND,
    AZURE_STORAGE_EXCEPTION_CONTAINER_NOT_FOUND,
    AZURE_STORAGE_INFO_ACCOUNT_KEY,
    AZURE_STORAGE_INFO_ACCOUNT_NAME,
    AZURE_STORAGE_INFO_CONTAINER_NAME,
)
from pyeqx.azure.errors import AzureStorageException


class AzureStorageHelper:
    @staticmethod
    def is_folder_exists(
        operation: Operation,
        data_props: FileDataModuleProperties,
        path: str,
    ):
        """
        Check if folder exists in ADLS Gen2 (Blob compatible)

        Args:
            data_props (FileDataModuleProperties): file data module properties
            path (str): folder path
        """
        storage = operation.get_storage(data_props.storage)
        storage_props = storage.get_properties(AzureAdlsGen2StorageDataProperties)

        azure_storage_info_map = AzureStorageHelper.get_storage_info_from_endpoint(
            operation=operation, endpoint=storage_props.endpoint
        )

        if (
            azure_storage_info_map.get(AZURE_STORAGE_INFO_ACCOUNT_KEY) is None
            and azure_storage_info_map.get(AZURE_STORAGE_INFO_ACCOUNT_NAME) is None
        ):
            raise AzureStorageException(
                AZURE_STORAGE_EXCEPTION_ACCOUNT_KEY_OR_NAME_NOT_FOUND
            )

        if azure_storage_info_map.get(AZURE_STORAGE_INFO_CONTAINER_NAME) is None:
            raise AzureStorageException(AZURE_STORAGE_EXCEPTION_CONTAINER_NOT_FOUND)

        paths = []
        if storage_props.path:
            paths.append(storage_props.path)

        if data_props.path:
            paths.append(data_props.path)

        if path:
            paths.append(f"{path}")

        actual_path = build_path(
            base_path=azure_storage_info_map.get(AZURE_STORAGE_INFO_CONTAINER_NAME),
            paths=paths,
        )

        fs = AzureBlobFileSystem(
            account_name=azure_storage_info_map.get(AZURE_STORAGE_INFO_ACCOUNT_NAME),
            account_key=azure_storage_info_map.get(AZURE_STORAGE_INFO_ACCOUNT_KEY),
        )

        operation.get_logger().debug(f"checking folder exists: {actual_path}")

        return fs.exists(path=actual_path)

    @staticmethod
    def list_files(
        operation: Operation,
        data_props: FileDataModuleProperties,
        path: str,
    ):
        """
        List files from ADLS Gen2 (Blob compatible)

        Args:
            data_props (FileDataModuleProperties): file data module properties
            path (str): file/folder path
        """
        storage = operation.get_storage(data_props.storage)
        storage_props = storage.get_properties(AzureAdlsGen2StorageDataProperties)

        azure_storage_info_map = AzureStorageHelper.get_storage_info_from_endpoint(
            operation=operation, endpoint=storage_props.endpoint
        )

        if (
            azure_storage_info_map.get(AZURE_STORAGE_INFO_ACCOUNT_KEY) is None
            and azure_storage_info_map.get(AZURE_STORAGE_INFO_ACCOUNT_NAME) is None
        ):
            raise AzureStorageException(
                AZURE_STORAGE_EXCEPTION_ACCOUNT_KEY_OR_NAME_NOT_FOUND
            )

        if azure_storage_info_map.get(AZURE_STORAGE_INFO_CONTAINER_NAME) is None:
            raise AzureStorageException(AZURE_STORAGE_EXCEPTION_CONTAINER_NOT_FOUND)

        paths = []
        if storage_props.path:
            paths.append(storage_props.path)

        if data_props.path:
            paths.append(data_props.path)

        if path:
            paths.append(path)

        paths.append("*.*")

        actual_path = build_path(
            base_path=azure_storage_info_map.get(AZURE_STORAGE_INFO_CONTAINER_NAME),
            paths=paths,
        )

        operation.get_logger().info(f"listing files from: {actual_path}")

        fs = AzureBlobFileSystem(
            account_name=azure_storage_info_map.get(AZURE_STORAGE_INFO_ACCOUNT_NAME),
            account_key=azure_storage_info_map.get(AZURE_STORAGE_INFO_ACCOUNT_KEY),
        )
        remote_files = fs.glob(path=actual_path)

        file_names = []

        for file in remote_files:
            file_names.append(os.path.basename(file))

        return file_names

    @staticmethod
    def get_storage_info_from_endpoint(
        operation: Operation, endpoint: str
    ) -> dict[str, Optional[str]]:
        spark_options = operation.get_config().engine.spark_options

        azure_storage_match = re.match(AZURE_STORAGE_CONTAINER_PATTERN, endpoint)

        container_name = None
        account_name = None
        account_key = None

        if azure_storage_match:
            container_name = azure_storage_match.group(1)
            account_name = azure_storage_match.group(2)

        if account_name:
            for key, value in spark_options.items():
                match = re.match(AZURE_SPARK_OPTION_PATTERN, key)
                if match and match.group(1) == account_name:
                    account_name = match.group(1)
                    account_key = value
                    break

        return {
            AZURE_STORAGE_INFO_CONTAINER_NAME: container_name,
            AZURE_STORAGE_INFO_ACCOUNT_NAME: account_name,
            AZURE_STORAGE_INFO_ACCOUNT_KEY: account_key,
        }

    @staticmethod
    def move_file(
        operation: Operation,
        src: str,
        dest: str,
        storage_props: AzureAdlsGen2StorageDataProperties,
    ):
        """
        Move file from source to destination

        Args:
            src (str): source path
            dest (str): destination path
            storage_props (AzureAdlsGen2StorageDataProperties): storage properties
        """
        azure_storage_info_map = AzureStorageHelper.get_storage_info_from_endpoint(
            operation=operation, endpoint=storage_props.endpoint
        )

        if (
            azure_storage_info_map.get(AZURE_STORAGE_INFO_ACCOUNT_KEY) is None
            and azure_storage_info_map.get(AZURE_STORAGE_INFO_ACCOUNT_NAME) is None
        ):
            raise AzureStorageException(
                AZURE_STORAGE_EXCEPTION_ACCOUNT_KEY_OR_NAME_NOT_FOUND
            )

        if azure_storage_info_map.get(AZURE_STORAGE_INFO_CONTAINER_NAME) is None:
            raise AzureStorageException(AZURE_STORAGE_EXCEPTION_CONTAINER_NOT_FOUND)

        account_name = azure_storage_info_map.get(AZURE_STORAGE_INFO_ACCOUNT_NAME)
        container_name = azure_storage_info_map.get(AZURE_STORAGE_INFO_CONTAINER_NAME)

        creds = AzureNamedKeyCredential(
            account_name,
            azure_storage_info_map.get(AZURE_STORAGE_INFO_ACCOUNT_KEY),
        )
        account_url = f"https://{account_name}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(
            account_url=account_url, credential=creds
        )

        source_blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=urlparse(url=src).path
        )

        destination_blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=urlparse(url=dest).path
        )

        exists = source_blob_client.exists()

        if exists is False:
            operation.get_logger().info(f"src: {src}, file does not exist.")
            return FunctionExecuteResult(data=False)

        copy_props = destination_blob_client.start_copy_from_url(source_blob_client.url)

        properties = destination_blob_client.get_blob_properties()
        if properties.copy.status == "success":
            source_blob_client.delete_blob()
            operation.get_logger().info(f"moving src: {src}, dest: {dest}")
            return FunctionExecuteResult(data=True)
        else:
            operation.get_logger().info(
                f"move operation failed: {copy_props['copy_status']}"
            )
            return FunctionExecuteResult(data=False)
