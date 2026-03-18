# Automatisation serveur — Variator Daily Captions

## Comment ça marche

Chaque jour à 9h (heure de Paris), **GitHub Actions** :
1. Lance `generate.py` → génère 3 variations + 3 captions
2. Uploade les 3 vidéos captions sur ton Google Drive dans `Variator/captions/YYYY-MM-DD/`

Ton PC n'a pas besoin d'être allumé.

---

## Configuration en 4 étapes

### Étape 1 : Créer un repo GitHub

1. Va sur https://github.com/new
2. Nom : `variator` (privé recommandé)
3. Ne coche rien (pas de README, pas de .gitignore)
4. Clique "Create repository"

Puis dans ton terminal PowerShell :

```powershell
cd "C:\Users\antod\OneDrive\Bureau\Variator"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TON_USERNAME/variator.git
git push -u origin main
```

### Étape 2 : Créer un service account Google

1. Va sur https://console.cloud.google.com/
2. Crée un nouveau projet (ex: "Variator")
3. Active l'API Google Drive :
   - Menu → APIs & Services → Library
   - Cherche "Google Drive API" → Enable
4. Crée un service account :
   - Menu → APIs & Services → Credentials
   - "Create Credentials" → "Service Account"
   - Nom : "variator-uploader"
   - Rôle : pas besoin (on partage le dossier directement)
   - Clique "Done"
5. Crée une clé JSON :
   - Clique sur le service account créé
   - Onglet "Keys" → "Add Key" → "Create new key" → JSON
   - Un fichier `.json` se télécharge → garde-le précieusement

### Étape 3 : Partager un dossier Drive avec le service account

1. Va sur https://drive.google.com
2. Crée un dossier "Variator" (ou utilise un existant)
3. Clic droit → Partager
4. Colle l'email du service account (ça ressemble à `variator-uploader@variator-XXXX.iam.gserviceaccount.com`)
5. Donne le rôle "Éditeur"
6. Copie l'**ID du dossier** : c'est la partie après `/folders/` dans l'URL
   - Ex: `https://drive.google.com/drive/folders/1aBcDeFgHiJkLmNoPqRsTuVwXyZ` → ID = `1aBcDeFgHiJkLmNoPqRsTuVwXyZ`

### Étape 4 : Ajouter les secrets GitHub

1. Va sur ton repo GitHub → Settings → Secrets and variables → Actions
2. Ajoute 2 secrets :

   | Nom du secret | Valeur |
   |---|---|
   | `GDRIVE_SERVICE_ACCOUNT_JSON` | Le contenu complet du fichier JSON téléchargé à l'étape 2 |
   | `GDRIVE_FOLDER_ID` | L'ID du dossier Drive de l'étape 3 |

---

## C'est prêt !

- Le workflow tourne chaque jour à 9h (Paris)
- Tu peux aussi le lancer manuellement : repo GitHub → Actions → "Daily Captions" → "Run workflow"
- Les vidéos apparaissent dans ton Google Drive dans `Variator/YYYY-MM-DD/`

## Tester en local

```powershell
# Mode local (copie vers Google Drive Desktop)
python daily_captions.py

# Mode serveur (upload via API, nécessite les env vars)
$env:GDRIVE_FOLDER_ID = "ton_folder_id"
$env:GDRIVE_SERVICE_ACCOUNT = "chemin/vers/service_account.json"
python daily_captions.py --server
```
