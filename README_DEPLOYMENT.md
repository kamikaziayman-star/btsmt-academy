# BTSMT Academy - Deploiement

Ce projet est une plateforme Streamlit pour un centre de formation BTS Management Touristique.

## Lancer en local

```powershell
python -m pip install -r requirements.txt
python -m streamlit run btsmtacademy.py
```

URL locale:

```text
http://localhost:8501
```

## Comptes importants

Les mots de passe peuvent etre configures avec des variables d'environnement.
Voir `.env.example`.

Comptes par defaut en developpement:

```text
Etudiant: btsmteljadidaacademy@.com / btsmt123
Invite test: invite@btsmtacademy.com / invite123
Admin: admin@btsmtacademy.com / admin123
Direction: direction@btsmtacademy.com / direction123
```

Les etudiants peuvent aussi creer leur propre compte depuis la page de connexion.
Le compte reste en attente jusqu'a validation dans:

```text
Espace direction > Comptes etudiants
```

## Deployer sur Render

1. Creer un compte sur Render.
2. Creer un nouveau Web Service.
3. Connecter le repository GitHub du projet.
4. Render detectera `render.yaml`.
5. Ajouter les variables d'environnement:

```text
BTSMT_ADMIN_PASSWORD
BTSMT_DIRECTION_PASSWORD
BTSMT_STUDENT_EMAIL
BTSMT_STUDENT_PASSWORD
BTSMT_GUEST_EMAIL
BTSMT_GUEST_PASSWORD
```

Optionnellement, ajouter les variables professeurs depuis `.env.example`.

## Donnees

Les donnees sont dans:

```text
btsmtacademy_data.json
```

Les fichiers envoyes sont dans:

```text
btsmtacademy_uploads/
```

Les sauvegardes automatiques sont dans:

```text
btsmtacademy_backups/
```

## Important pour usage reel

Pour un vrai usage public avec beaucoup d'utilisateurs, la prochaine evolution conseillee est:

- remplacer JSON par SQLite ou PostgreSQL
- stocker les fichiers dans Google Drive, Supabase Storage ou S3
- hasher les mots de passe
- ajouter sauvegarde externe automatique
