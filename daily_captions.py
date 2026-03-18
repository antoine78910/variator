"""
Daily caption generator: generates 3 caption videos and uploads to Google Drive.

Local:   python daily_captions.py                  (copies to Google Drive Desktop folder)
Server:  python daily_captions.py --server          (uploads via Google Drive API)
         Requires GDRIVE_FOLDER_ID, GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET, GDRIVE_REFRESH_TOKEN env vars.

Configuration (edit below):
  DAILY_COUNT — number of captions per day (default 3)
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DAILY_COUNT = 3

DRIVE_CANDIDATES = [
    Path("G:/My Drive/Variator/captions"),
    Path("G:/Mon Drive/Variator/captions"),
    Path(r"C:\Users\antod\Google Drive\Variator\captions"),
    Path(r"C:\Users\antod\Mon Drive\Variator\captions"),
]


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def find_drive_folder() -> Path | None:
    for p in DRIVE_CANDIDATES:
        if p.parent.exists():
            p.mkdir(parents=True, exist_ok=True)
            return p
    g_drive = Path("G:/")
    if g_drive.exists():
        for d in g_drive.iterdir():
            if d.is_dir() and ("drive" in d.name.lower() or "mon" in d.name.lower() or "my" in d.name.lower()):
                dest = d / "Variator" / "captions"
                dest.mkdir(parents=True, exist_ok=True)
                return dest
    return None


def copy_to_drive_local(drive_folder: Path) -> int:
    caption_videos = PROJECT_ROOT / "output" / "caption" / "videos"
    if not caption_videos.exists():
        log("No caption videos directory found.")
        return 0
    today = datetime.now().strftime("%Y-%m-%d")
    dest = drive_folder / today
    dest.mkdir(parents=True, exist_ok=True)
    videos = sorted(caption_videos.glob("caption_*.mp4"))
    if not videos:
        log("No caption .mp4 files found to copy.")
        return 0
    copied = 0
    for v in videos:
        target = dest / v.name
        try:
            shutil.copy2(v, target)
            log(f"  Copied {v.name} -> {target}")
            copied += 1
        except Exception as e:
            log(f"  Failed to copy {v.name}: {e}")
    return copied


def upload_to_drive_api() -> int:
    """Upload via Google Drive API (for server / GitHub Actions)."""
    import os
    folder_id = os.environ.get("GDRIVE_FOLDER_ID", "")
    client_id = os.environ.get("GDRIVE_CLIENT_ID", "")
    client_secret = os.environ.get("GDRIVE_CLIENT_SECRET", "")
    refresh_token = os.environ.get("GDRIVE_REFRESH_TOKEN", "")
    if not folder_id or not client_id or not client_secret or not refresh_token:
        log("Missing GDRIVE_FOLDER_ID / GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN. Skipping Drive upload.")
        return 0
    try:
        from upload_to_drive import upload_captions
        count = upload_captions(folder_id, client_id, client_secret, refresh_token)
        return count
    except Exception as e:
        log(f"Drive API upload failed: {e}")
        return 0


def run_pipeline():
    generate_py = PROJECT_ROOT / "generate.py"
    if not generate_py.exists():
        log(f"FATAL: generate.py not found at {generate_py}")
        sys.exit(1)

    sys.path.insert(0, str(PROJECT_ROOT))
    import generate

    generate.MAX_VARIATIONS = DAILY_COUNT
    generate.CAPTION_MAX_COUNT = DAILY_COUNT
    generate.load_layout_file()

    class Args:
        images_only = False
        videos_only = False
        preview_position = False
        preview_live = False
        captions = False

    args = Args()
    log(f"Running full pipeline for {DAILY_COUNT} variations...")
    try:
        generate.main(args)
        log("Generation complete.")
    except Exception as e:
        log(f"Error during generation: {e}")
        import traceback
        log(traceback.format_exc())
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Daily caption generator")
    parser.add_argument("--server", action="store_true", help="Server mode: upload via Google Drive API instead of local copy")
    cli_args = parser.parse_args()

    log("=" * 60)
    log("Daily caption generation started")

    run_pipeline()

    if cli_args.server:
        log("Server mode: uploading via Google Drive API...")
        count = upload_to_drive_api()
        log(f"Uploaded {count} caption videos to Google Drive.")
    else:
        drive_folder = find_drive_folder()
        if drive_folder:
            log(f"Google Drive folder: {drive_folder}")
            copied = copy_to_drive_local(drive_folder)
            log(f"Copied {copied} caption videos to Google Drive.")
        else:
            log("Google Drive folder not found. Videos in output/caption/videos/.")

    log("Daily caption generation finished.")
    log("=" * 60)


if __name__ == "__main__":
    main()
