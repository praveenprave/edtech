#!/bin/bash
set -e

# Configuration (Passed from Cloud Build Envs)
PROJECT_ID=${PROJECT_ID}
REGION=${REGION:-us-central1}
DB_INSTANCE_NAME=${DB_INSTANCE_NAME:-"textbook-rag-db"}
BUCKET_NAME="${PROJECT_ID}-assets"

# Extract SA Name from email if full email provided, otherwise default
if [[ "$_SERVICE_ACCOUNT" == *"@"* ]]; then
    # if it's an email sa-name@project..., extract 'sa-name'
    SERVICE_ACCOUNT_NAME=$(echo $_SERVICE_ACCOUNT | cut -d@ -f1)
    SERVICE_ACCOUNT_EMAIL=$_SERVICE_ACCOUNT
else
    # Default fallback
    SERVICE_ACCOUNT_NAME="sa-textbook-rag"
    SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
fi

echo "🚀 Starting Infrastructure Setup for ${PROJECT_ID}..."
echo "📍 Region: ${REGION}"
echo "👤 Service Account: ${SERVICE_ACCOUNT_EMAIL}"

# 1. Enable APIs
echo "Enable APIs..."
gcloud services enable \
    aiplatform.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    storage.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com \
    --project ${PROJECT_ID}

# 2. Infrastructure: Storage
echo "Checking GCS Bucket..."
if ! gsutil ls -b gs://${BUCKET_NAME} > /dev/null 2>&1; then
    gsutil mb -l ${REGION} gs://${BUCKET_NAME}
    echo "✅ Bucket created: ${BUCKET_NAME}"
else
    echo "✅ Bucket exists: ${BUCKET_NAME}"
fi

# 3. Infrastructure: Cloud SQL (PostgreSQL)
# Note: Creating SQL instances takes time (5-10 mins). We check if exists first.
echo "Checking Cloud SQL Instance..."
if ! gcloud sql instances describe ${DB_INSTANCE_NAME} --project ${PROJECT_ID} > /dev/null 2>&1; then
    echo "⚠️ Database instance not found. Creating (this usually takes 5-10 mins)..."
    gcloud sql instances create ${DB_INSTANCE_NAME} \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=${REGION} \
        --root-password=supersecretDBpassword123 \
        --project ${PROJECT_ID}
    
    # Create DB and User
    gcloud sql databases create rag_platform --instance=${DB_INSTANCE_NAME}
else
    echo "✅ Database instance exists: ${DB_INSTANCE_NAME}"
fi

# 4. Infrastructure: IAM
echo "Checking Service Account..."
if ! gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} --project ${PROJECT_ID} > /dev/null 2>&1; then
    gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
        --display-name="Textbook RAG Service Account" \
        --project ${PROJECT_ID}
    
    # Grant Roles
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/aiplatform.user" \
        --condition=None
    
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/storage.objectViewer" \
        --condition=None
        
     gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/cloudsql.client" \
        --condition=None
        
    echo "✅ Service Account created and roles assigned."
    echo "✅ Service Account exists: ${SERVICE_ACCOUNT_EMAIL}"
fi

# 5. Database Schema (Automated Migration)
echo "Checking Database Schema..."
if [ -f "database/schema.sql" ]; then
    echo "Uploading schema.sql to GCS..."
    gsutil cp database/schema.sql gs://${BUCKET_NAME}/schema.sql
    
    # --- Fix: Grant Cloud SQL Permission to Read from Bucket ---
    echo "Granting Cloud SQL Service Account permissions to read from bucket..."
    SQL_SA=$(gcloud sql instances describe ${DB_INSTANCE_NAME} --project ${PROJECT_ID} --format="value(serviceAccountEmailAddress)")
    echo "Found Cloud SQL SA: ${SQL_SA}"
    
    # We use 'gsutil iam ch' for easy bucket-level permission update
    gsutil iam ch serviceAccount:${SQL_SA}:objectViewer gs://${BUCKET_NAME}
    # -----------------------------------------------------------
    
    echo "Importing Schema into Cloud SQL (Safe to run multiple times)..."
    gcloud sql import sql ${DB_INSTANCE_NAME} gs://${BUCKET_NAME}/schema.sql \
        --database=rag_platform \
        --project=${PROJECT_ID} \
        --quiet
    
    echo "✅ Schema Import Triggered."
else
    echo "⚠️ database/schema.sql not found locally. Skipping schema import."
fi

echo "🎉 Infrastructure Setup Complete!"
