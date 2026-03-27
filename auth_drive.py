"""
One-time script to get a Google Drive OAuth2 refresh token.

Run once locally:
    pip install google-auth-oauthlib
    python auth_drive.py --client-id YOUR_ID --client-secret YOUR_SECRET

Or set env vars (avoids secrets on the command line):
    set GDRIVE_CLIENT_ID=...
    set GDRIVE_CLIENT_SECRET=...
    python auth_drive.py

It will open a browser window to authorize your Google account.
Then it prints the refresh token — copy it into GitHub Secrets as GDRIVE_REFRESH_TOKEN.
"""

import argparse
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def main():
    parser = argparse.ArgumentParser(description="Get Google Drive OAuth2 refresh token")
    parser.add_argument(
        "--client-id",
        default=os.environ.get("GDRIVE_CLIENT_ID", ""),
        help="OAuth client ID (or env GDRIVE_CLIENT_ID)",
    )
    parser.add_argument(
        "--client-secret",
        default=os.environ.get("GDRIVE_CLIENT_SECRET", ""),
        help="OAuth client secret (or env GDRIVE_CLIENT_SECRET)",
    )
    args = parser.parse_args()
    if not args.client_id or not args.client_secret:
        raise SystemExit(
            "Missing client id/secret: pass --client-id and --client-secret, "
            "or set GDRIVE_CLIENT_ID and GDRIVE_CLIENT_SECRET."
        )

    client_config = {
        "installed": {
            "client_id": args.client_id,
            "client_secret": args.client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    print("Ouverture du navigateur pour autoriser l'acces Google Drive...")
    print()

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=9090, prompt="consent", access_type="offline")

    print()
    print("=" * 60)
    print("Authentification reussie!")
    print()
    print("Copie cette valeur dans GitHub Secrets comme GDRIVE_REFRESH_TOKEN:")
    print()
    print(f"  {creds.refresh_token}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
