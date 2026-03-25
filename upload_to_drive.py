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
import random
import re
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

PROJECT_ROOT = Path(__file__).resolve().parent
CAPTION_VIDEOS_DIR = PROJECT_ROOT / "output" / "caption" / "videos"

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
TOKEN_URI = "https://oauth2.googleapis.com/token"

# Titres affichés comme nom de fichier sur Google Drive (un tirage au sort par vidéo)
DRIVE_CTA_TITLES = [
    'Follow & comment "W" to receive the full guide',
    'Follow + comment "AI" to unlock the full guide',
    'Follow and drop "W" for the full guide',
    'Follow & type "AI" to get access to the full guide',
    'Follow and comment "W" to unlock everything',
    'Follow + comment "AI" for instant access to the guide',
    'Follow and reply "W" to get the full guide',
    'Follow & comment "AI" to receive the guide',
    'Follow and drop "AI" below to unlock the full guide',
    'Follow & comment "W" to access the full guide',
    'Follow and type "AI" to get everything',
    'Follow + comment "W" for the complete guide',
    'Follow and comment "AI" to unlock the full guide',
    'Follow & drop "W" to get full access to the guide',
    'Follow and comment "AI" to receive the full guide-access',
    'Follow + comment "W" to get the full breakdown',
    'Follow and type "AI" below for the full guide',
    'Follow & comment "W" to unlock the method',
    'Follow and drop "AI" for full access',
    'Follow + comment "W" to get everything unlocked',
]


def sanitize_drive_filename(cta: str, max_len: int = 180) -> str:
    """Transforme une phrase CTA en nom de fichier .mp4 valide pour Drive (espaces conservés)."""
    s = cta.strip()
    s = s.replace('"', "")  # guillemets retirés pour le nom de fichier
    for ch in r'\/:*?<>|':
        s = s.replace(ch, "")
    s = s.replace("&", " and ")
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > max_len:
        s = s[:max_len].rstrip()
    if not s.lower().endswith(".mp4"):
        s = f"{s}.mp4"
    return s


def pick_drive_filenames(n: int) -> list[str]:
    """Choisit n titres distincts (tirage aléatoire) et les convertit en noms .mp4 uniques."""
    if n <= 0:
        return []
    pool = list(DRIVE_CTA_TITLES)
    if n <= len(pool):
        chosen = random.sample(pool, n)
    else:
        chosen = random.choices(pool, k=n)
    names: list[str] = []
    used_lower: set[str] = set()
    for cta in chosen:
        base = sanitize_drive_filename(cta)
        name = base
        i = 2
        while name.lower() in used_lower:
            stem = base[:-4] if base.lower().endswith(".mp4") else base
            name = f"{stem} ({i}).mp4"
            i += 1
        used_lower.add(name.lower())
        names.append(name)
    return names


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


def upload_file(service, folder_id: str, file_path: Path, drive_filename: str | None = None) -> str:
    """Upload a single file to the given Drive folder. Returns the file ID."""
    name = drive_filename if drive_filename else file_path.name
    metadata = {"name": name, "parents": [folder_id]}
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

    drive_names = pick_drive_filenames(len(videos))
    uploaded = 0
    for v, drive_name in zip(videos, drive_names):
        try:
            fid = upload_file(service, folder_id, v, drive_filename=drive_name)
            print(f"  Uploaded {v.name} -> Drive as {drive_name!r} (id={fid})")
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
