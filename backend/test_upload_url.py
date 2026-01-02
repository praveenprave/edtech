import sys
import os
from dotenv import load_dotenv

# Ensure backend directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

try:
    from app.services.storage import StorageService
    
    print("🧪 initializing StorageService...")
    storage = StorageService()
    
    print(f"✅ Project ID: {storage.project_id}")
    print(f"✅ Bucket Name: {storage.bucket_name}")
    
    # Test SA Email resolution logic
    if os.getenv("SERVICE_ACCOUNT_EMAIL"):
        print(f"✅ SERVICE_ACCOUNT_EMAIL found in env: {os.getenv('SERVICE_ACCOUNT_EMAIL')}")
    else:
        print("⚠️ SERVICE_ACCOUNT_EMAIL not in env (OK for initial test, but required for proper fix)")

    if storage.bucket_name == "None-assets":
        print("❌ Error: Bucket name is invalid (None-assets)")
        sys.exit(1)
        
    print("🧪 Generating Upload URL...")
    result = storage.generate_upload_url("test_file.pdf")
    
    print(f"✅ Generated URL: {result['upload_url'][:50]}...")
    print(f"✅ GCS URI: {result['gcs_uri']}")
    
    if "poc-project-477509-assets" not in result['gcs_uri']:
         print(f"❌ Error: GCS URI does not contain correct bucket name. Got: {result['gcs_uri']}")
         sys.exit(1)
         
    print("\n🎉 Test Passed!")
    
except Exception as e:
    print(f"\n❌ Test Failed: {e}")
    sys.exit(1)
