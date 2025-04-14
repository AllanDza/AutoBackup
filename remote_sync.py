import subprocess, json, os
from config import BUCKET 
import logging
from google.cloud import storage
import os


def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)

def sync_file_to_gcs(file_path, bucket_name):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    if not file_path.endswith(".enc"):
        print(f"⚠️ Not an encrypted file (.enc): {file_path}")
        return

    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set. Please export your service account key path.")
        return

    try:
        print(f"🚀 Uploading {os.path.basename(file_path)} to Google Cloud Storage bucket '{bucket_name}'...")
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(os.path.basename(file_path))
        blob.upload_from_filename(file_path)
        print("✅ Upload successful.")
        logging.info(f"Uploaded {file_path} to {bucket_name}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        logging.error(f"Upload failed: {e}")



def download_from_gcs(blob_name, destination_path, bucket_name):
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        blob.download_to_filename(destination_path)

        print(f"📥 Downloaded '{blob_name}' to '{destination_path}'")
        return True
    except Exception as e:
        print(f"❌ Failed to download '{blob_name}' from GCS: {e}")
        return False
