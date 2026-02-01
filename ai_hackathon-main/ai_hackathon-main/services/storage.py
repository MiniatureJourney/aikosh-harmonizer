import os
import shutil
from abc import ABC, abstractmethod
import boto3
from botocore.exceptions import NoCredentialsError

class StorageService(ABC):
    @abstractmethod
    def save(self, file_content: bytes, filename: str) -> str:
        """Saves content and returns the file path/URL."""
        pass

    @abstractmethod
    def get(self, filename: str) -> bytes:
        """Retrieves content as bytes."""
        pass

    @abstractmethod
    def delete(self, filename: str):
        """Deletes the file."""
        pass

    @abstractmethod
    def list(self, prefix: str) -> list[str]:
        """Lists files with prefix."""
        pass

class LocalStorage(StorageService):
    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save(self, file_content: bytes, filename: str) -> str:
        path = os.path.join(self.base_dir, filename)
        with open(path, "wb") as f:
            f.write(file_content)
        return path

    def get(self, filename: str) -> bytes:
        path = os.path.join(self.base_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {filename} not found")
        with open(path, "rb") as f:
            return f.read()

    def delete(self, filename: str):
        path = os.path.join(self.base_dir, filename)
        if os.path.exists(path):
            os.remove(path)

    def list(self, prefix: str) -> list[str]:
        # Simple implementation for local
        if not os.path.exists(self.base_dir):
            return []
        return [f for f in os.listdir(self.base_dir) if f.startswith(prefix)]

class S3Storage(StorageService):
    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET_NAME")
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )

    def save(self, file_content: bytes, filename: str) -> str:
        try:
            self.s3.put_object(Bucket=self.bucket, Key=filename, Body=file_content)
            return f"s3://{self.bucket}/{filename}"
        except NoCredentialsError:
            raise Exception("AWS Credentials not available")

    def get(self, filename: str) -> bytes:
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=filename)
            return response['Body'].read()
        except Exception as e:
            raise FileNotFoundError(f"S3 File {filename} not found: {e}")

    def delete(self, filename: str):
        self.s3.delete_object(Bucket=self.bucket, Key=filename)

    def list(self, prefix: str) -> list[str]:
        response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        return []

def get_storage_service() -> StorageService:
    """Factory to get the correct storage service based on Env."""
    if os.getenv("USE_S3", "false").lower() == "true":
        print("Using S3 Storage")
        return S3Storage()
    print("Using Local Storage")
    return LocalStorage()
