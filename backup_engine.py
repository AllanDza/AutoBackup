
import os, time, tarfile
from datetime import datetime, timedelta
from multiprocessing import Pool
import logging

def get_modified_files(base_dir, days=2):
    cutoff = time.time() - days * 86400
    files_to_backup = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            full_path = os.path.join(root, file)
            if os.path.getmtime(full_path) > cutoff:
                files_to_backup.append(full_path)
    return files_to_backup

def create_backup(files, backup_dir='backups'):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = os.path.join(backup_dir, f"{timestamp}_backup.tar.gz")
    os.makedirs(backup_dir, exist_ok=True)
    with tarfile.open(backup_path, "w:gz") as tar:
        for file in files:
            tar.add(file, arcname=os.path.relpath(file, '/'))
    return backup_path
