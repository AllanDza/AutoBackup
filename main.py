import argparse
import os
import json
import tarfile
from backup_engine import get_modified_files, create_backup
from secure_utils import save_hash_manifest, encrypt_file, verify_file_hashes
from remote_sync import sync_file_to_gcs ,download_from_gcs # updated import
from config import BUCKET ,JSON_PATH

import logging
import os


os.makedirs("logs", exist_ok=True)


LOG_FILE = "logs/autobackup.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,  # You can use DEBUG for more details
    format="%(asctime)s - %(levelname)s - %(message)s"
)


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = JSON_PATH
BACKUP_DIR = "backups"
HASH_FILE = "backups/hash_manifest.json"

def start_backup(target_dir):
    logging.info(f"Starting backup for {target_dir} ...")
    if not os.path.exists(target_dir):
        print(f"Directory not found: {target_dir}")
        logging.error(f"Directory not found: {target_dir}")
        return

    files = get_modified_files(target_dir, days=2)
    if not files:
        print(" No recently modified files to back up.")
        return

    timestamp = os.path.basename(os.path.normpath(target_dir)) + "_" + os.path.splitext(os.path.basename(__file__))[0]
    backup_path = create_backup(files)
    
    
    # Save hash manifest next to the backup
    manifest_path = backup_path.replace(".tar.gz", "_hash_manifest.json")
    save_hash_manifest(files, output=manifest_path)

    encrypted = encrypt_file(backup_path)
    print(f"✅ Backup complete: {encrypted}")
    logging.info(f"Backup completed: {encrypted}")

def push_remote(bucket_name=BUCKET):
    # Get the most recently modified encrypted backup
    logging.info("Push remote...")
    encrypted_files = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.endswith(".enc")],
        key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x))
    )
    if not encrypted_files:
        print("No encrypted backup files found to push.")
        logging.error("No encrypted backup files found to push.")
        return

    latest = encrypted_files[-1]
    full_path = os.path.join(BACKUP_DIR, latest)

    print(f"☁️ Pushing {latest} to Google Cloud Storage...")
    logging.info(f"Pushing {latest} to Google Cloud Storage...")
    sync_file_to_gcs(full_path, bucket_name=bucket_name)


def restore_backup(backup_file, destination):
    logging.info(f"Restoring backup from {backup_file} to {destination} ...")
    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        logging.error(f"Backup file not found: {backup_file}")
        return

    print(f"🔄 Restoring backup from {backup_file} to {destination} ...")
    os.makedirs(destination, exist_ok=True)
    with tarfile.open(backup_file, 'r:gz') as tar:
        tar.extractall(path=destination)
    print("✅ Restore complete.")
    logging.info(f"Restore completed from {backup_file} to {destination}")

from secure_utils import decrypt_file

def restore_remote_backup(blob_name, destination,bucket_name=BUCKET):
    logging.info(f"Restoring remote backup {blob_name} to {destination} ...")
    os.makedirs("backups", exist_ok=True)
    encrypted_path = os.path.join("backups", blob_name)

    # Download encrypted file
    downloaded = download_from_gcs(blob_name, encrypted_path, bucket_name)
    if downloaded:
        try:
            print("🔐 Decrypting the file...")
            decrypted_tar = decrypt_file(encrypted_path)
            print(f"✅ Decrypted: {decrypted_tar}")
            restore_backup(decrypted_tar, destination)
        except Exception as e:
            print(f"❌ Decryption failed: {e}")


def view_backup_history():
    if not os.path.exists(BACKUP_DIR):
        print("No backups found.")
        return
    print("📁 Backup history:")
    for file in sorted(os.listdir(BACKUP_DIR)):
        print("  -", file)

def validate_integrity(manifest_path):
    if not os.path.exists(manifest_path):
        print("Hash manifest not found.")
        return
    print("🔍 Validating file integrity...")
    modified = verify_file_hashes(manifest_path)
    if modified:
        print("Modified files detected:")
        for f in modified:
            print("  -", f)
    else:
        print("All files match original hash.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🖥️ AutoBackup Control Panel")
    parser.add_argument("command", choices=["backup", "push", "restore", "history", "validate","restore-remote"], help="Action to perform")
    parser.add_argument("--file", help="Backup file path (for restore)")
    parser.add_argument("--dest", default="./restored", help="Restore destination (default: ./restored)")
    parser.add_argument("--dir", help="Target directory to back up (for backup)")
    parser.add_argument("--manifest", help="mainifest path(for validity)")
    parser.add_argument("--bucket", help="GCS bucket name for push")
    parser.add_argument("--blob", help="Blob name in GCS (for remote restore)")


    args = parser.parse_args()

    if args.command == "backup":
        if not args.dir:
            print("Please specify --dir to back up.")
        else:
            start_backup(args.dir)

    elif args.command == "push":
        push_remote(args.bucket)
        
    elif args.command == "restore":
        if not args.file:
            print("Please specify --file --dest for restore.")
        else:
            restore_backup(args.file, args.dest)
    elif args.command == "history":
        view_backup_history()
    elif args.command == "validate":
        if not args.manifest:
            print("Please specify --manifest /path/to/manifest.")
        else:
            validate_integrity(args.manifest)

    elif args.command == "restore-remote":
        if not args.blob :
            print("Please specify --blob ")
        else:
            restore_remote_backup(args.blob,args.dest)    
