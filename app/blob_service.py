import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def upload_log_to_blob(file_path, file_name):
    try:
        connection_string = os.getenv("BLOB_CONNECTION_STRING")
        container_name = os.getenv("BLOB_CONTAINER_NAME")

        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=file_name
        )

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        print(f"Uploaded {file_name} to Azure Blob Storage")
        return True

    except Exception as e:
        print(f"Blob upload error: {e}")
        return False
