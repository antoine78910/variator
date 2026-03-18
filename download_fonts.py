"""
Télécharge les 3 polices titres (Rubik-Bold, Montserrat-Bold, Poppins-Bold)
dans le dossier fonts/ pour que generate.py puisse les utiliser.
Lance une fois : python download_fonts.py
"""

import urllib.request
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
FONTS_DIR = PROJECT_ROOT / "fonts"

# URLs des polices (sources officielles / licence OFL)
FONTS_TO_DOWNLOAD = [
    (
        "Rubik-Bold.ttf",
        "https://raw.githubusercontent.com/google/fonts/main/ofl/rubik/Rubik%5Bwght%5D.ttf",
        # Google Fonts n'a plus que la variable ; on la sauve en Rubik-Bold (PIL utilise le poids par défaut)
    ),
    (
        "Montserrat-Bold.ttf",
        "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Bold.ttf",
    ),
    (
        "Poppins-Bold.ttf",
        "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-Bold.ttf",
    ),
]

# Rubik : la variable font peut ne pas rendre "Bold" sous PIL ; alternative static
RUBIK_BOLD_STATIC = (
    "Rubik-Bold.ttf",
    "https://www.cs.cmu.edu/~rraghuna/static/fonts/Rubik/Rubik-Bold.ttf",
)


def download_file(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            dest.write_bytes(resp.read())
        return True
    except Exception as e:
        print(f"  Erreur: {e}")
        return False


def main():
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    print("Téléchargement des polices dans fonts/\n")

    # Essayer d'abord Rubik-Bold en static (CMU), sinon variable
    rubik_dest = FONTS_DIR / "Rubik-Bold.ttf"
    if not rubik_dest.exists():
        print("Rubik-Bold.ttf ...")
        if download_file(RUBIK_BOLD_STATIC[1], rubik_dest):
            print("  OK (source: CMU)")
        else:
            print("  Essai variable font Google ...")
            if download_file(FONTS_TO_DOWNLOAD[0][1], rubik_dest):
                print("  OK (variable font ; rendu peut être Regular)")
            else:
                print("  Échec. Télécharge manuellement depuis https://fonts.google.com/specimen/Rubik")
    else:
        print("Rubik-Bold.ttf déjà présent.")

    for name, url in FONTS_TO_DOWNLOAD[1:]:  # Montserrat, Poppins
        dest = FONTS_DIR / name
        if dest.exists():
            print(f"{name} déjà présent.")
            continue
        print(f"{name} ...")
        if download_file(url, dest):
            print("  OK")
        else:
            print(f"  Échec. Télécharge depuis https://fonts.google.com et place le fichier dans fonts/")

    print("\nTerminé. Tu peux lancer: python generate.py")


if __name__ == "__main__":
    main()
