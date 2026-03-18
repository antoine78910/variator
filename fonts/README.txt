========================================
Comment télécharger les 3 polices titres
========================================

0. Téléchargement automatique (recommandé)
   ---------------------------------------
   À la racine du projet, lance une fois :
     python download_fonts.py
   Les 3 fichiers .ttf seront téléchargés dans CE dossier (fonts/).

1. Où les télécharger à la main (gratuit)
   ----------------------------
   • Google Fonts : https://fonts.google.com

   Rubik (Bold) :
     → https://fonts.google.com/specimen/Rubik
     → Cliquer sur "Download family" (en haut à droite)
     → Dézipper le fichier. Le fichier à garder est dans le dossier "static" : Rubik-Bold.ttf

   Montserrat (Bold) :
     → https://fonts.google.com/specimen/Montserrat
     → Download family → dézipper
     → Dans le dossier "static" : Montserrat-Bold.ttf

   Poppins (Bold) :
     → https://fonts.google.com/specimen/Poppins
     → Download family → dézipper
     → Dans le dossier "static" : Poppins-Bold.ttf


2. Où les mettre
   -------------
   Copie les 3 fichiers .ttf dans CE dossier (Variator/fonts/) :
     • Rubik-Bold.ttf
     • Montserrat-Bold.ttf
     • Poppins-Bold.ttf

   Ou installe-les pour Windows : double-clic sur chaque .ttf → "Installer".
   Le script les trouvera dans C:\Windows\Fonts\.


3. Vérifier les noms
   -----------------
   Les noms doivent être EXACTEMENT (sensible à la casse) :
     Rubik-Bold.ttf
     Montserrat-Bold.ttf
     Poppins-Bold.ttf

   Si ton ZIP contient "Rubik-Bold.ttf" dans "static/", copie ce fichier
   (pas le dossier) dans fonts/. Si le nom est différent (ex. Rubik_Bold.ttf),
   renomme-le en Rubik-Bold.ttf ou modifie TITLE_FONTS dans generate.py.


4. Changer les polices
   --------------------
   Dans generate.py, cherche TITLE_FONTS et modifie la liste avec
   les noms de tes fichiers .ttf.
