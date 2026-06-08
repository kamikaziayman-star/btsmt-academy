# BTS SMARTCAMPUS - D?ploiement

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

Les mots de passe peuvent ?tre configur?s avec des variables d'environnement.
Voir `.env.example`.

Comptes par d?faut en d?veloppement:

```text
?tudiant: btsmteljadidaacademy@.com / btsmt123
Invite test: invite@btsmtacademy.com / invite123
Admin: admin@btsmtacademy.com / admin123
Direction: direction@btsmtacademy.com / direction123
```

Les ?tudiants peuvent aussi cr?er leur propre compte depuis la page de connexion.
Le compte reste en attente jusqu'? validation dans:

```text
Espace direction > Comptes ?tudiants
```

Les mots de passe des comptes cr??s dans l'application sont stockes avec un hash PBKDF2.
L'interface admin n'affiche plus les mots de passe r?els.

## Supabase

Pour garder les donn?es en ligne sur Streamlit Cloud, cr?ez un projet Supabase puis ex?cutez ce SQL dans Supabase SQL Editor:

```sql
create table if not exists app_state (
  id text primary key,
  payload jsonb not null,
  updated_at text not null
);
```

Pour une utilisation plus fiable avec plusieurs connexions en m?me temps, ex?cutez aussi le fichier:

```text
supabase_multitable_schema.sql
```

Il cr?e les tables:

```text
student_accounts
prof_accounts
messages
courses
exams
shared_files
planning
view_receipts
support_tickets
```

Quand ces tables existent, l'application les utilise automatiquement. Sinon elle garde l'ancien stockage `app_state` comme fallback.

Ajoutez ensuite ces secrets dans Streamlit Cloud:

```text
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
```

L'application utilisera Supabase automatiquement si ces variables existent. Sinon elle garde SQLite en local.

## D?ployer sur Render

1. Cr?er un compte sur Render.
2. Cr?er un nouveau Web Service.
3. Connecter le repository GitHub du projet.
4. Render d?tectera `render.yaml`.
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

## Donn?es

Si Supabase est configur?, les donn?es sont sauvegard?es dans Supabase.

Sinon, les donn?es sont sauvegard?es dans une base SQLite locale:

```text
btsmtacademy.db
```

Une copie lisible est aussi gard?e dans:

```text
btsmtacademy_data.json
```

Important: sur Streamlit Community Cloud, les fichiers locaux peuvent ?tre recr??s lors d'un red?marrage. Pour une plateforme publique durable, il faudra connecter Supabase ou une autre base externe.

Les fichiers envoy?s sont dans:

```text
btsmtacademy_uploads/
```

Les sauvegardes automatiques sont dans:

```text
btsmtacademy_backups/
```

## Important pour usage r?el

Pour un vrai usage public avec beaucoup d'utilisateurs, la prochaine ?volution conseill?e est:

- connecter Supabase ou PostgreSQL externe
- stocker les fichiers dans Google Drive, Supabase Storage ou S3
- hasher les mots de passe
- ajouter une sauvegarde externe automatique
