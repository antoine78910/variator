"""
One-time script to get a Google Drive OAuth2 refresh token.

Run once locally:
    pip install google-auth-oauthlib
    python auth_drive.py --client-id YOUR_ID --client-secret YOUR_SECRET

It will open a browser window to authorize your Google account.
Then it prints the refresh token — copy it into GitHub Secrets as GDRIVE_REFRESH_TOKEN.
"""

import argparse
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def main():
    parser = argparse.ArgumentParser(description="Get Google Drive OAuth2 refresh token")
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--client-secret", required=True)
    args = parser.parse_args()

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
