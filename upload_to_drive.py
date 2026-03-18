"""
Upload caption videos to a shared Google Drive folder using a service account.

Usage:
    python upload_to_drive.py                          # upload today's captions
    python upload_to_drive.py --folder-id XXXXX        # override target folder
    python upload_to_drive.py --service-account key.json

Environment variables (used by GitHub Actions):
    GDRIVE_FOLDER_ID       — ID of the shared Google Drive folder
    GDRIVE_SERVICE_ACCOUNT — path to service account JSON key file (or inline JSON)
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

PROJECT_ROOT = Path(__file__).resolve().parent
CAPTION_VIDEOS_DIR = PROJECT_ROOT / "output" / "caption" / "videos"

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_credentials(sa_path_or_json: str):
    """Load service account credentials from a file path or inline JSON string."""
    if os.path.isfile(sa_path_or_json):
        return service_account.Credentials.from_service_account_file(sa_path_or_json, scopes=SCOPES)
    try:
        info = json.loads(sa_path_or_json)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    except (json.JSONDecodeError, ValueError):
        pass
    raise ValueError(f"Cannot load service account from: {sa_path_or_json[:80]}...")


def find_or_create_subfolder(service, parent_id: str, name: str) -> str:
    """Find or create a subfolder inside parent_id. Returns the folder ID."""
    query = (
        f"'{parent_id}' in parents and name = '{name}' "
        f"and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def upload_file(service, folder_id: str, file_path: Path) -> str:
    """Upload a single file to the given Drive folder. Returns the file ID."""
    metadata = {"name": file_path.name, "parents": [folder_id]}
    media = MediaFileUpload(str(file_path), resumable=True)
    uploaded = service.files().create(body=metadata, media_body=media, fields="id, name").execute()
    return uploaded["id"]


def upload_captions(folder_id: str, sa_path_or_json: str) -> int:
    """Upload all caption .mp4 files to Drive/folder_id/YYYY-MM-DD/. Returns count."""
    creds = get_credentials(sa_path_or_json)
    service = build("drive", "v3", credentials=creds)

    today = datetime.now().strftime("%Y-%m-%d")
    day_folder_id = find_or_create_subfolder(service, folder_id, today)

    videos = sorted(CAPTION_VIDEOS_DIR.glob("caption_*.mp4"))
    if not videos:
        print("No caption videos found to upload.")
        return 0

    uploaded = 0
    for v in videos:
        try:
            fid = upload_file(service, day_folder_id, v)
            print(f"  Uploaded {v.name} -> Drive (id={fid})")
            uploaded += 1
        except Exception as e:
            print(f"  Failed to upload {v.name}: {e}")

    return uploaded


def main():
    parser = argparse.ArgumentParser(description="Upload caption videos to Google Drive")
    parser.add_argument("--folder-id", default=os.environ.get("GDRIVE_FOLDER_ID", ""), help="Google Drive folder ID")
    parser.add_argument(
        "--service-account",
        default=os.environ.get("GDRIVE_SERVICE_ACCOUNT", "service_account.json"),
        help="Path to service account JSON or inline JSON",
    )
    args = parser.parse_args()

    if not args.folder_id:
        print("ERROR: No Drive folder ID. Set GDRIVE_FOLDER_ID env var or pass --folder-id.")
        sys.exit(1)

    print(f"Uploading captions to Drive folder {args.folder_id}...")
    count = upload_captions(args.folder_id, args.service_account)
    print(f"Done. Uploaded {count} files.")


if __name__ == "__main__":
    main()
