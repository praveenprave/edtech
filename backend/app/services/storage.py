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
        Robustly handles Cloud Run environment (where local private key is missing)
        by auto-detecting Service Account email to trigger IAM Signing.
        """
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(f"textbooks/{filename}")

        try:
            # 1. Try standard signing (works locally)
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(minutes=15),
                method="PUT",
                content_type=content_type,
            )
        except Exception:
            # 2. Fallback: Explicitly use Service Account Email (triggers IAM Signing)
            print("⚠️ Local signing failed (No Private Key). Attempting IAM Signing via Service Account...")
            import google.auth
            credentials, _ = google.auth.default()
            
            # Auto-detect SA email if available, else construct assumption
            sa_email = getattr(credentials, "service_account_email", None)
            if not sa_email or sa_email == "default":
                 # Fallback for Cloud Run if auth lib doesn't populate it or returns 'default'
                 sa_email = f"sa-prod-rag@{self.project_id}.iam.gserviceaccount.com"
            
            print(f"🔑 Using Service Account: {sa_email}")
            
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(minutes=15),
                method="PUT",
                content_type=content_type,
                service_account_email=sa_email,
                access_token=credentials.token # Pass token to be safe
            )

        return {
            "upload_url": url,
            "gcs_uri": f"gs://{self.bucket_name}/textbooks/{filename}",
            "filename": filename
        }
