# AutoBackup

A Python-based secure automated backup system with encryption, integrity validation, logging, remote syncing (Google Cloud Storage), and restoration functionality.

---

## 📦 Features

-  **Incremental Backups** — Backs up only recently modified files (within last 2 days).
-  **Encryption** — Uses AES (Fernet) to encrypt backup archives.
- **Hash Manifest** — SHA256-based hash manifest for file integrity validation.
- **Push to Google Cloud Storage** — Encrypted backups can be synced to a GCS bucket.
- **Restore** — Restore backups locally or download and decrypt from GCS.
- **Validate Integrity** — Check if any files have changed since backup using hash manifests.
- **Logging** — All operations are logged into `backup.log` for tracking and debugging.
- **Cron Integration** — Easily schedule backup and push jobs using `cron`.

---

## Quick Start

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/autobackup.git
cd autobackup
```

#### 2. Create and Activate a Virtual Environment (Optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Requirements
```bash
pip install -r requirements.txt
```
---
## ⚙️ Configuration
🔑 Set Google Cloud Credentials

##### 1. Enable GCS on Google Cloud
1. Go to Google Cloud Console

2. Create a project (if not already)

3. Enable Google Cloud Storage JSON API

##### 2. Create a Storage Bucket
1. Navigate to Storage > Browser

2. Click Create Bucket

3. Give a globally unique name (e.g., autobackup-user123)

4. Choose default settings

##### 3. Create a Service Account Key
1. Navigate to IAM & Admin > Service Accounts

2. Click Create Service Account

3. Assign Storage Admin role

4. Generate a JSON key and download it



🔑 Set Google Cloud Credentials
In config.py, specify the path to your GCP service account key:



#### config.py:

```
JSON_PATH = "/absolute/path/to/autobackup-agent-key.json"
BUCKET= "gcs_bucket_name"
```
Then in your code (typically at the start of main.py or remote_sync.py):

```
import os
from config import JSON_PATH
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = JSON_PATH
```
This ensures Google Cloud SDK uses the correct service account credentials for authentication.

Run the main command-line interface:

```
python3 main.py [command] [options]
```

## Commands:

|  Command	 |  Description |
| ------------ | ------------ |
|  backup | Start a new backup  |
| push  |  Push latest encrypted backup to GCS |
| restore  | Restore from a backup file(local)  |
| restore-remote |  remote Restore from a backup file in remote(GCS) |
| history  | View backup history (local)  |
| validate  | Validate integrity of files from hash manifest  |


Example Usages:
Backup:

```bash
python3 main.py backup --dir /path/to/your/files
```

Push to GCS:

```bash
python3 main.py push
```
Restore:

```bash
python3 main.py restore --file backups/filename.tar.gz.enc --dest ./restored
```
Validate:

```bash
python3 main.py validate --manifest backups/manifest_filename.json
```

## 🧠 How It Works
1. Modified files are packed into a .tar.gz archive.

2. Archive is encrypted using a secret.key.

3. A hash manifest (*_hash_manifest.json) is created for all files.

4. Logs are written to backup.log for every operation.

5. Encrypted backup files are optionally uploaded to a GCS bucket.

6. Can be restored locally or downloaded+decrypted from cloud.

## 🧾 Requirements
- Python 3.7+

Packages:

- cryptography

- google-cloud-storage

- argparse

- tarfile, hashlib, os, json, etc.

Install using:

```bash
pip install -r requirements.txt
```
## ⏱️ Cron Setup
Schedule Automatic Backups (every 12 hours)
```bash
0 */12 * * * /usr/bin/python3 /path/to/main.py backup --dir /your/target/dir >> /path/to/log.txt 2>&1
```
Schedule Cloud Push (once per day)
```bash
0 1 * * * /usr/bin/python3 /path/to/main.py push >> /path/to/log.txt 2>&1
```
## 📄 Log File
All operations are logged in backup.log (created automatically).

View logs using:

```bash
tail -f backup.log
```
## 📂 Directory Structure
```
AutoBackup/
├── main.py
├── backup_engine.py
├── secure_utils.py
├── remote_sync.py
├── backups/
│   ├── [encrypted .tar.gz files]
│   └── [hash_manifest.json files]
├── secret.key
├── backup.log
└── requirements.txt
```
## ✅ Todo / Improvements
- Add email notification on backup success/failure

- Add S3 or Dropbox integration

- Add GUI version

## 📬 Author
Developed by Allan Dsouza
GitHub: github.com/AllanDza
