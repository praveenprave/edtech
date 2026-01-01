import os
import sys
from google.cloud import storage

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "poc-project-477509")
BUCKET_NAME = f"{PROJECT_ID}-assets"

def upload_to_gcs(source_file_path, destination_blob_name):
    """Uploads a file to the bucket."""
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)

        print(f"Uploading {source_file_path} to gs://{BUCKET_NAME}/{destination_blob_name}...")
        blob.upload_from_filename(source_file_path)

        print(f"✅ Upload Comlete! URI: gs://{BUCKET_NAME}/{destination_blob_name}")
        print("ℹ️  Note: Vertex AI Search will automatically index this if the Data Store is connected.")
        
    except Exception as e:
        print(f"❌ Error uploading to GCS: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_textbooks.py <path_to_pdf>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
        
    filename = os.path.basename(file_path)
    # Organize by 'textbooks/' prefix
    destination = f"textbooks/{filename}"
    
    upload_to_gcs(file_path, destination)
