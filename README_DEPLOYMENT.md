# BTS SMARTCAMPUS - Deploiement

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

Les mots de passe des comptes crees dans l'application sont stockes avec un hash PBKDF2.
L'interface admin n'affiche plus les mots de passe reels.

## Supabase

Pour garder les donnees en ligne sur Streamlit Cloud, creez un projet Supabase puis executez ce SQL dans Supabase SQL Editor:

```sql
create table if not exists app_state (
  id text primary key,
  payload jsonb not null,
  updated_at text not null
);
```

Ajoutez ensuite ces secrets dans Streamlit Cloud:

```text
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
```

L'application utilisera Supabase automatiquement si ces variables existent. Sinon elle garde SQLite en local.

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
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
```

Optionnellement, ajouter les variables professeurs depuis `.env.example`.

## Donnees

Si Supabase est configure, les donnees sont sauvegardees dans Supabase.

Sinon, les donnees sont sauvegardees dans une base SQLite locale:

```text
btsmtacademy.db
```

Une copie lisible est aussi gardee dans:

```text
btsmtacademy_data.json
```

Important: sur Streamlit Community Cloud, les fichiers locaux peuvent etre recrees lors d'un redemarrage. Pour une plateforme publique durable, il faudra connecter Supabase ou une autre base externe.

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

- connecter Supabase ou PostgreSQL externe
- stocker les fichiers dans Google Drive, Supabase Storage ou S3
- hasher les mots de passe
- ajouter sauvegarde externe automatique
