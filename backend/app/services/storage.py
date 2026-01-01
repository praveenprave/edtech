from google.cloud import storage
import datetime
import os

class StorageService:
    def __init__(self):
        # We assume the environment has GOOGLE_APPLICATION_CREDENTIALS or is running in Cloud Run (Metadata Server)
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.bucket_name = f"{self.project_id}-assets"
        self._client = None

    @property
    def client(self):
        if not self._client:
            self._client = storage.Client(project=self.project_id)
        return self._client

    def generate_upload_url(self, filename: str, content_type: str = "application/pdf") -> dict:
        """
        Generates a V4 Signed URL for uploading a file directly to GCS.
        """
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(f"textbooks/{filename}")

        # Usage: PUT request with the signed URL
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=15), # 15 min window
            method="PUT",
            content_type=content_type,
        )

        return {
            "upload_url": url,
            "gcs_uri": f"gs://{self.bucket_name}/textbooks/{filename}",
            "filename": filename
        }
