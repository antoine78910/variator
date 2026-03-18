"""
Upload caption videos to Google Drive using OAuth2 (user credentials).

Usage:
    python upload_to_drive.py                          # upload today's captions
    python upload_to_drive.py --folder-id XXXXX        # override target folder

Environment variables (used by GitHub Actions):
    GDRIVE_FOLDER_ID       — ID of the shared Google Drive folder
    GDRIVE_CLIENT_ID       — OAuth2 client ID
    GDRIVE_CLIENT_SECRET   — OAuth2 client secret
    GDRIVE_REFRESH_TOKEN   — OAuth2 refresh token (obtained via auth_drive.py)
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

PROJECT_ROOT = Path(__file__).resolve().parent
CAPTION_VIDEOS_DIR = PROJECT_ROOT / "output" / "caption" / "videos"

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def get_credentials(client_id: str, client_secret: str, refresh_token: str) -> Credentials:
    """Build OAuth2 credentials from client ID/secret and refresh token."""
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri=TOKEN_URI,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


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


def upload_captions(folder_id: str, client_id: str, client_secret: str, refresh_token: str) -> int:
    """Upload all caption .mp4 files directly to the given Drive folder. Returns count."""
    creds = get_credentials(client_id, client_secret, refresh_token)
    service = build("drive", "v3", credentials=creds)

    videos = sorted(CAPTION_VIDEOS_DIR.glob("caption_*.mp4"))
    if not videos:
        print("No caption videos found to upload.")
        return 0

    uploaded = 0
    for v in videos:
        try:
            fid = upload_file(service, folder_id, v)
            print(f"  Uploaded {v.name} -> Drive (id={fid})")
            uploaded += 1
        except Exception as e:
            print(f"  Failed to upload {v.name}: {e}")

    return uploaded


def main():
    parser = argparse.ArgumentParser(description="Upload caption videos to Google Drive")
    parser.add_argument("--folder-id", default=os.environ.get("GDRIVE_FOLDER_ID", ""), help="Google Drive folder ID")
    parser.add_argument("--client-id", default=os.environ.get("GDRIVE_CLIENT_ID", ""), help="OAuth2 client ID")
    parser.add_argument("--client-secret", default=os.environ.get("GDRIVE_CLIENT_SECRET", ""), help="OAuth2 client secret")
    parser.add_argument("--refresh-token", default=os.environ.get("GDRIVE_REFRESH_TOKEN", ""), help="OAuth2 refresh token")
    args = parser.parse_args()

    if not args.folder_id:
        print("ERROR: No Drive folder ID. Set GDRIVE_FOLDER_ID env var or pass --folder-id.")
        sys.exit(1)
    if not args.client_id or not args.client_secret or not args.refresh_token:
        print("ERROR: Missing OAuth2 credentials. Set GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET, GDRIVE_REFRESH_TOKEN.")
        sys.exit(1)

    print(f"Uploading captions to Drive folder {args.folder_id}...")
    count = upload_captions(args.folder_id, args.client_id, args.client_secret, args.refresh_token)
    print(f"Done. Uploaded {count} files.")


if __name__ == "__main__":
    main()
