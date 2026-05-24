import calendar
import base64
import hashlib
import hmac
import html
import json
import os
import secrets
import shutil
import sqlite3
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st


APP_TITLE = "BTS SMARTCAMPUS"
DATA_FILE = Path("btsmtacademy_data.json")
DATABASE_FILE = Path("btsmtacademy.db")
BACKUP_DIR = Path("btsmtacademy_backups")
UPLOAD_DIR = Path("btsmtacademy_uploads")
LOGO_PATH = Path(r"c:\Users\pc\Downloads\plf logo.png")
RESOURCE_TYPES = ["Cours", "Exercice", "Correction", "Examen", "Fiche resume"]
COURSE_STATUS = ["Disponible", "A reviser", "Corrige ajoute", "Mis a jour"]
ADMIN_EMAIL = "admin@btsmtacademy.com"
ADMIN_PASSWORD = os.getenv("BTSMT_ADMIN_PASSWORD", "admin123")
DIRECTION_EMAIL = "direction@btsmtacademy.com"
DIRECTION_PASSWORD = os.getenv("BTSMT_DIRECTION_PASSWORD", "direction123")
STUDENT_EMAIL = os.getenv("BTSMT_STUDENT_EMAIL", "btsmteljadidaacademy@.com")
STUDENT_PASSWORD = os.getenv("BTSMT_STUDENT_PASSWORD", "btsmt123")
GUEST_EMAIL = os.getenv("BTSMT_GUEST_EMAIL", "invite@btsmtacademy.com")
GUEST_PASSWORD = os.getenv("BTSMT_GUEST_PASSWORD", "invite123")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
PASSWORD_HASH_PREFIX = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 260000


def env_password(name, default):
    return os.getenv(name, default)


def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_HASH_ITERATIONS,
    ).hex()
    return f"{PASSWORD_HASH_PREFIX}${PASSWORD_HASH_ITERATIONS}${salt}${digest}"


def is_password_hash(value):
    return isinstance(value, str) and value.startswith(f"{PASSWORD_HASH_PREFIX}$")


def verify_password(password, stored_password):
    if not stored_password:
        return False
    if not is_password_hash(stored_password):
        return hmac.compare_digest(password, str(stored_password))

    try:
        _prefix, iterations, salt, expected_digest = stored_password.split("$", 3)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        ).hex()
        return hmac.compare_digest(digest, expected_digest)
    except (ValueError, TypeError):
        return False


def protect_password(password):
    return password if is_password_hash(password) else hash_password(str(password))

SUBJECTS = [
    "Controle de gestion",
    "Informatique de gestion",
    "Marketing touristique",
    "Commercialisation des services touristiques",
    "Communication professionnelle",
    "Entrepreneuriat",
    "Anglais",
    "Arabe",
    "Espagnol",
    "Francais",
    "Economie generale et touristique",
    "Management des organisations touristiques",
    "Droit applique au tourisme",
]

SUBJECT_THEMES = {
    "Controle de gestion": {
        "icon": "&#128202;",
        "color": "#4f46e5",
        "soft": "#eef2ff",
        "label": "Analyse et chiffres",
    },
    "Informatique de gestion": {
        "icon": "&#128187;",
        "color": "#7c3aed",
        "soft": "#f3e8ff",
        "label": "Systemes et outils",
    },
    "Marketing touristique": {
        "icon": "&#127965;",
        "color": "#10b981",
        "soft": "#ecfdf5",
        "label": "Clients et marche",
    },
    "Commercialisation des services touristiques": {
        "icon": "&#127970;",
        "color": "#f97316",
        "soft": "#fff7ed",
        "label": "Vente et services",
    },
    "Communication professionnelle": {
        "icon": "&#128172;",
        "color": "#0ea5e9",
        "soft": "#e0f2fe",
        "label": "Ecrits et oral",
    },
    "Entrepreneuriat": {
        "icon": "&#128188;",
        "color": "#f59e0b",
        "soft": "#fffbeb",
        "label": "Projet et creation",
    },
    "Anglais": {
        "icon": "A+",
        "color": "#3b82f6",
        "soft": "#eff6ff",
        "label": "English skills",
    },
    "Arabe": {
        "icon": "&#1593;",
        "color": "#ec4899",
        "soft": "#fdf2f8",
        "label": "Langue arabe",
    },
    "Espagnol": {
        "icon": "ES",
        "color": "#8b5cf6",
        "soft": "#f5f3ff",
        "label": "Idioma espanol",
    },
    "Francais": {
        "icon": "Fr",
        "color": "#059669",
        "soft": "#ecfdf5",
        "label": "Langue francaise",
    },
    "Economie generale et touristique": {
        "icon": "&#127757;",
        "color": "#2563eb",
        "soft": "#eff6ff",
        "label": "Economie et tourisme",
    },
    "Management des organisations touristiques": {
        "icon": "&#128200;",
        "color": "#f97316",
        "soft": "#fff7ed",
        "label": "Strategie et GRH",
    },
    "Droit applique au tourisme": {
        "icon": "&#9878;",
        "color": "#64748b",
        "soft": "#f8fafc",
        "label": "Regles et contrats",
    },
}


def subject_theme(subject):
    return SUBJECT_THEMES.get(
        subject,
        {
            "icon": "&#128214;",
            "color": "#2563eb",
            "soft": "#eff6ff",
            "label": "Ressources",
        },
    )

PROF_ACCOUNTS = {
    ADMIN_EMAIL: {
        "name": "Administration BTS SMARTCAMPUS",
        "subject": "Toutes les matieres",
        "password": ADMIN_PASSWORD,
        "role": "admin",
    },
    "controle@btsmtacademy.com": {
        "name": "Prof Controle de gestion",
        "subject": "Controle de gestion",
        "password": env_password("BTSMT_PROF_CONTROLE_PASSWORD", "controle123"),
        "role": "prof",
    },
    "informatique@btsmtacademy.com": {
        "name": "Prof Informatique de gestion",
        "subject": "Informatique de gestion",
        "password": env_password("BTSMT_PROF_INFORMATIQUE_PASSWORD", "informatique123"),
        "role": "prof",
    },
    "marketing@btsmtacademy.com": {
        "name": "Prof Marketing touristique",
        "subject": "Marketing touristique",
        "password": env_password("BTSMT_PROF_MARKETING_PASSWORD", "marketing123"),
        "role": "prof",
    },
    "commercialisation@btsmtacademy.com": {
        "name": "Prof Commercialisation",
        "subject": "Commercialisation des services touristiques",
        "password": env_password("BTSMT_PROF_COMMERCIALISATION_PASSWORD", "commercialisation123"),
        "role": "prof",
    },
    "communication@btsmtacademy.com": {
        "name": "Prof Communication professionnelle",
        "subject": "Communication professionnelle",
        "password": env_password("BTSMT_PROF_COMMUNICATION_PASSWORD", "communication123"),
        "role": "prof",
    },
    "entrepreneuriat@btsmtacademy.com": {
        "name": "Prof Entrepreneuriat",
        "subject": "Entrepreneuriat",
        "password": env_password("BTSMT_PROF_ENTREPRENEURIAT_PASSWORD", "entrepreneuriat123"),
        "role": "prof",
    },
    "anglais@btsmtacademy.com": {
        "name": "Prof Anglais",
        "subject": "Anglais",
        "password": env_password("BTSMT_PROF_ANGLAIS_PASSWORD", "anglais123"),
        "role": "prof",
    },
    "arabe@btsmtacademy.com": {
        "name": "Prof Arabe",
        "subject": "Arabe",
        "password": env_password("BTSMT_PROF_ARABE_PASSWORD", "arabe123"),
        "role": "prof",
    },
    "espagnol@btsmtacademy.com": {
        "name": "Prof Espagnol",
        "subject": "Espagnol",
        "password": env_password("BTSMT_PROF_ESPAGNOL_PASSWORD", "espagnol123"),
        "role": "prof",
    },
    "francais@btsmtacademy.com": {
        "name": "Prof Francais",
        "subject": "Francais",
        "password": env_password("BTSMT_PROF_FRANCAIS_PASSWORD", "francais123"),
        "role": "prof",
    },
    "economie@btsmtacademy.com": {
        "name": "Prof Economie generale et touristique",
        "subject": "Economie generale et touristique",
        "password": env_password("BTSMT_PROF_ECONOMIE_PASSWORD", "economie123"),
        "role": "prof",
    },
    "management@btsmtacademy.com": {
        "name": "Prof Management",
        "subject": "Management des organisations touristiques",
        "password": env_password("BTSMT_PROF_MANAGEMENT_PASSWORD", "management123"),
        "role": "prof",
    },
    "droit@btsmtacademy.com": {
        "name": "Prof Droit applique au tourisme",
        "subject": "Droit applique au tourisme",
        "password": env_password("BTSMT_PROF_DROIT_PASSWORD", "droit123"),
        "role": "prof",
    },
}

ACCOUNT_PASSWORD_ENV = {
    ADMIN_EMAIL: "BTSMT_ADMIN_PASSWORD",
    "controle@btsmtacademy.com": "BTSMT_PROF_CONTROLE_PASSWORD",
    "informatique@btsmtacademy.com": "BTSMT_PROF_INFORMATIQUE_PASSWORD",
    "marketing@btsmtacademy.com": "BTSMT_PROF_MARKETING_PASSWORD",
    "commercialisation@btsmtacademy.com": "BTSMT_PROF_COMMERCIALISATION_PASSWORD",
    "communication@btsmtacademy.com": "BTSMT_PROF_COMMUNICATION_PASSWORD",
    "entrepreneuriat@btsmtacademy.com": "BTSMT_PROF_ENTREPRENEURIAT_PASSWORD",
    "anglais@btsmtacademy.com": "BTSMT_PROF_ANGLAIS_PASSWORD",
    "arabe@btsmtacademy.com": "BTSMT_PROF_ARABE_PASSWORD",
    "espagnol@btsmtacademy.com": "BTSMT_PROF_ESPAGNOL_PASSWORD",
    "francais@btsmtacademy.com": "BTSMT_PROF_FRANCAIS_PASSWORD",
    "economie@btsmtacademy.com": "BTSMT_PROF_ECONOMIE_PASSWORD",
    "management@btsmtacademy.com": "BTSMT_PROF_MANAGEMENT_PASSWORD",
    "droit@btsmtacademy.com": "BTSMT_PROF_DROIT_PASSWORD",
}


def default_data():
    return {
        "prof_accounts": PROF_ACCOUNTS,
        "student_accounts": {},
        "devoirs": [],
        "shared_files": [],
        "student_contacts": [],
        "support_tickets": [],
        "direct_messages": [],
        "seen_updates": {},
        "messages": [
            {
                "titre": "Bienvenue sur BTS SMARTCAMPUS",
                "matiere": "General",
                "prof": "Administration",
                "date": "2026-05-20 12:00",
                "contenu": (
                    "Les professeurs peuvent publier ici les annonces, les nouveaux "
                    "cours et les dates importantes."
                ),
            }
        ],
        "cours": {
            subject: [
                {
                    "titre": f"Cours de {subject}",
                    "description": "Ajoutez ici le lien Drive du dossier de cours.",
                    "url": "https://drive.google.com/",
                    "type": "Cours",
                    "statut": "Disponible",
                    "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "prof": "Administration",
                }
            ]
            for subject in SUBJECTS
        },
        "examens": [
            {
                "titre": "Examens nationaux precedents",
                "matiere": "Toutes les matieres",
                "annee": "Archive",
                "description": "Ajoutez ici le lien Drive des examens nationaux.",
                "url": "https://drive.google.com/",
                "session": "Archive",
                "corrige_url": "",
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
        ],
    }


def init_database():
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def supabase_is_configured():
    return bool(SUPABASE_URL and SUPABASE_KEY)


def supabase_request(method, path, payload=None, extra_headers=None):
    url = f"{SUPABASE_URL}/rest/v1/{path.lstrip('/')}"
    body = None
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=12) as response:
        content = response.read().decode("utf-8")
    return json.loads(content) if content else None


def load_data_from_supabase():
    if not supabase_is_configured():
        return None
    try:
        rows = supabase_request(
            "GET",
            "app_state?id=eq.main&select=payload",
        )
        if not rows:
            return None
        payload = rows[0].get("payload")
        if isinstance(payload, str):
            return json.loads(payload)
        return payload
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, KeyError):
        return None


def save_data_to_supabase(data):
    if not supabase_is_configured():
        return False
    updated_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    try:
        supabase_request(
            "POST",
            "app_state",
            {
                "id": "main",
                "payload": data,
                "updated_at": updated_at,
            },
            {
                "Prefer": "resolution=merge-duplicates,return=minimal",
            },
        )
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return False


def load_data_from_database():
    supabase_data = load_data_from_supabase()
    if supabase_data is not None:
        return supabase_data

    if not DATABASE_FILE.exists():
        return None

    init_database()
    with sqlite3.connect(DATABASE_FILE) as connection:
        row = connection.execute(
            "SELECT payload FROM app_state WHERE id = ?",
            ("main",),
        ).fetchone()

    if not row:
        return None

    return json.loads(row[0])


def save_data_to_database(data):
    save_data_to_supabase(data)
    init_database()
    payload = json.dumps(data, ensure_ascii=False)
    updated_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            INSERT INTO app_state (id, payload, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                payload = excluded.payload,
                updated_at = excluded.updated_at
            """,
            ("main", payload, updated_at),
        )
        connection.execute(
            "INSERT INTO audit_log (action, created_at) VALUES (?, ?)",
            ("save_data", updated_at),
        )
        connection.commit()


def normalize_brand_text(value):
    if not isinstance(value, str):
        return value
    replacements = {
        "BTSMT Academy": "BTS SMARTCAMPUS",
        "Administration BTSMT": "Administration BTS SMARTCAMPUS",
        "Direction BTSMT": "Direction BTS SMARTCAMPUS",
        "BTSMT": "BTS SMARTCAMPUS",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def load_data():
    data = load_data_from_database()
    if data is None:
        if DATA_FILE.exists():
            with DATA_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = default_data()
        save_data(data, create_backup=False)

    for message in data.get("messages", []):
        message.setdefault("matiere", "General")
        message.setdefault("prof", "Administration")
        message.setdefault("date", "Date non indiquee")
        message.setdefault("important", False)
        for field in ("titre", "prof", "contenu"):
            message[field] = normalize_brand_text(message.get(field, ""))

    for subject in SUBJECTS:
        data.setdefault("cours", {}).setdefault(subject, [])
        for resource in data["cours"][subject]:
            resource.setdefault("type", "Cours")
            resource.setdefault("statut", "Disponible")
            resource.setdefault("date", "Date non indiquee")
            resource.setdefault("prof", "Administration")
            for field in ("titre", "description", "prof"):
                resource[field] = normalize_brand_text(resource.get(field, ""))

    for exam in data.get("examens", []):
        exam.setdefault("session", "Archive")
        exam.setdefault("corrige_url", "")
        exam.setdefault("date", "Date non indiquee")

    data.setdefault("prof_accounts", PROF_ACCOUNTS)
    for email, account in PROF_ACCOUNTS.items():
        data["prof_accounts"].setdefault(email, account)
        data["prof_accounts"][email]["name"] = normalize_brand_text(
            data["prof_accounts"][email].get("name", "")
        )
        env_var = ACCOUNT_PASSWORD_ENV.get(email)
        if env_var and os.getenv(env_var):
            data["prof_accounts"][email]["password"] = hash_password(os.getenv(env_var))
        else:
            data["prof_accounts"][email]["password"] = protect_password(
                data["prof_accounts"][email].get("password", "")
            )

    data.setdefault("student_accounts", {})
    for email, account in data["student_accounts"].items():
        account.setdefault("prenom", "")
        account.setdefault("nom", "")
        account.setdefault("groupe", "")
        account.setdefault("password", "")
        account.setdefault("status", "pending")
        account.setdefault("created_at", "Date non indiquee")
        account.setdefault("validated_at", "")
        account.setdefault("banned", False)
        account.setdefault("admin_messages", [])
        account["password"] = protect_password(account.get("password", ""))
        for admin_message in account["admin_messages"]:
            for field in ("titre", "contenu"):
                admin_message[field] = normalize_brand_text(admin_message.get(field, ""))

    data.setdefault("devoirs", [])
    for devoir in data["devoirs"]:
        devoir.setdefault("matiere", "General")
        devoir.setdefault("titre", "Devoir")
        devoir.setdefault("description", "")
        devoir.setdefault("date_limite", "")
        devoir.setdefault("lien", "")
        devoir.setdefault("prof", "Administration")
        devoir.setdefault("date_publication", "Date non indiquee")
        for field in ("titre", "description", "prof"):
            devoir[field] = normalize_brand_text(devoir.get(field, ""))

    data.setdefault("shared_files", [])
    for shared_file in data["shared_files"]:
        shared_file.setdefault("titre", "Fichier partage")
        shared_file.setdefault("description", "")
        shared_file.setdefault("matiere", "Toutes les matieres")
        shared_file.setdefault("auteur", "Administration")
        shared_file.setdefault("role", "direction")
        shared_file.setdefault("date", "Date non indiquee")
        shared_file.setdefault("filename", "")
        shared_file.setdefault("path", "")
        shared_file.setdefault("mime", "application/octet-stream")
        for field in ("titre", "description", "auteur"):
            shared_file[field] = normalize_brand_text(shared_file.get(field, ""))

    data.setdefault("student_contacts", [])
    for contact in data["student_contacts"]:
        contact.setdefault("matiere", "General")
        contact.setdefault("nom", "")
        contact.setdefault("prenom", "")
        contact.setdefault("message", "")
        contact.setdefault("date", "Date non indiquee")
        contact.setdefault("reponse", "")
        contact.setdefault("date_reponse", "")

    data.setdefault("support_tickets", [])
    for ticket in data["support_tickets"]:
        ticket.setdefault("type", "Reclamation")
        ticket.setdefault("nom", "")
        ticket.setdefault("email", "")
        ticket.setdefault("role", "Utilisateur")
        ticket.setdefault("sujet", "")
        ticket.setdefault("message", "")
        ticket.setdefault("date", "Date non indiquee")
        ticket.setdefault("statut", "Nouveau")
        ticket.setdefault("reponse", "")
        ticket.setdefault("date_reponse", "")
        ticket.setdefault("screenshot_path", "")
        ticket.setdefault("screenshot_name", "")
        ticket.setdefault("screenshot_mime", "")
        for field in ("sujet", "message", "reponse"):
            ticket[field] = normalize_brand_text(ticket.get(field, ""))

    data.setdefault("seen_updates", {})

    data.setdefault("direct_messages", [])
    for message in data["direct_messages"]:
        message.setdefault("from_email", ADMIN_EMAIL)
        message.setdefault("from_name", "Administration BTS SMARTCAMPUS")
        message.setdefault("to_email", "")
        message.setdefault("to_name", "")
        message.setdefault("titre", "Message")
        message.setdefault("contenu", "")
        message.setdefault("date", "Date non indiquee")
        message.setdefault("attachment_path", "")
        message.setdefault("attachment_name", "")
        message.setdefault("attachment_mime", "application/octet-stream")
        message.setdefault("read", False)
        for field in ("from_name", "to_name", "titre", "contenu"):
            message[field] = normalize_brand_text(message.get(field, ""))

    save_data(data, create_backup=False)
    return data


def backup_data_file():
    if not DATA_FILE.exists():
        return

    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{DATA_FILE.stem}_{timestamp}.json"
    shutil.copy2(DATA_FILE, backup_path)

    backups = sorted(BACKUP_DIR.glob(f"{DATA_FILE.stem}_*.json"))
    for old_backup in backups[:-20]:
        old_backup.unlink(missing_ok=True)


def save_data(data, create_backup=True):
    if create_backup:
        backup_data_file()
    save_data_to_database(data)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def logo_data_uri():
    if not LOGO_PATH.exists():
        return ""

    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def clean_filename(filename):
    safe = "".join(
        character if character.isalnum() or character in "._-" else "_"
        for character in filename
    )
    return safe or "fichier"


def save_uploaded_file(uploaded_file, folder="general"):
    UPLOAD_DIR.mkdir(exist_ok=True)
    target_dir = UPLOAD_DIR / clean_filename(folder)
    target_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{clean_filename(uploaded_file.name)}"
    path = target_dir / filename
    path.write_bytes(uploaded_file.getbuffer())
    return path


def render_shared_file(shared_file):
    role_label = "Direction BTS SMARTCAMPUS" if shared_file.get("role") == "direction" else shared_file.get("auteur", "Professeur")
    st.markdown(
        f"""
        <div class="shared-file-card">
            <div class="shared-file-head">
                <div class="shared-file-icon">F</div>
                <div>
                    <h3>{shared_file.get("titre", "Fichier partage")}</h3>
                    <div class="shared-file-meta">
                        <span>Matiere: {shared_file.get("matiere", "Toutes les matieres")}</span>
                        <span>Publie par: {role_label}</span>
                        <span>Date: {shared_file.get("date", "Date non indiquee")}</span>
                    </div>
                </div>
            </div>
            <p>{shared_file.get("description", "")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    path = Path(shared_file.get("path", ""))
    if not path.exists():
        st.warning("Le fichier n'existe plus dans le dossier local.")
        return

    mime = shared_file.get("mime", "application/octet-stream")
    if mime.startswith("image/"):
        st.image(str(path), width="stretch")

    st.download_button(
        "Telecharger le fichier",
        data=path.read_bytes(),
        file_name=shared_file.get("filename") or path.name,
        mime=mime,
        key=f"download_{path.as_posix()}_{shared_file.get('date', '')}",
    )


def render_local_attachment(path_value, file_name="", mime="application/octet-stream", key_prefix="attachment"):
    raw_path = str(path_value or "").strip()
    if not raw_path or raw_path in {".", "./", "/", "\\"}:
        return

    path = Path(raw_path)
    if not path.exists() or not path.is_file():
        st.info("Piece jointe indisponible sur ce serveur.")
        return

    try:
        attachment_bytes = path.read_bytes()
    except (OSError, IsADirectoryError, PermissionError):
        st.info("Piece jointe indisponible sur ce serveur.")
        return

    if (mime or "").startswith("image/"):
        try:
            st.image(str(path), width="stretch")
        except Exception:
            pass

    st.download_button(
        "Telecharger la piece jointe",
        data=attachment_bytes,
        file_name=file_name or path.name,
        mime=mime or "application/octet-stream",
        key=f"{key_prefix}_{abs(hash((path.as_posix(), file_name, mime)))}",
    )


def support_bot_answer(user_message):
    text = user_message.lower()
    password_words = ["mot de passe", "password", "mdp", "nssit", "نسيت", "code", "connexion", "login"]
    course_words = ["cours", "cour", "matiere", "module", "pdf", "drive", "lien", "link", "ma kayt7el", "makaykhdemch"]
    account_words = ["compte", "inscription", "validation", "valider", "banni", "ban", "access", "acces", "دخول"]
    exam_words = ["examen", "exam", "devoir", "calendrier", "planning", "date"]
    bug_words = ["bug", "erreur", "problem", "probleme", "مشكل", "mouchkil", "khata", "error", "ne marche pas"]

    if any(word in text for word in password_words):
        return (
            "Je comprends. Pour un probleme de connexion ou mot de passe, verifiez d'abord que l'email est ecrit sans espace. "
            "Si le probleme continue, envoyez cette conversation a l'admin: il pourra verifier votre compte ou changer le mot de passe."
        )
    if any(word in text for word in course_words):
        return (
            "Pour un cours ou un lien Drive, indiquez la matiere et le nom du cours. "
            "Si le lien ne s'ouvre pas, l'admin/professeur pourra le corriger apres reception de votre reclamation."
        )
    if any(word in text for word in account_words):
        return (
            "Pour un compte ou une validation, votre demande doit etre traitee par l'administration. "
            "Envoyez cette conversation a l'admin avec votre nom, email et groupe."
        )
    if any(word in text for word in exam_words):
        return (
            "Pour les examens ou la planification, verifiez d'abord l'onglet Calendrier et Examens. "
            "Si une date ou un fichier manque, envoyez la conversation a l'admin."
        )
    if any(word in text for word in bug_words):
        return (
            "D'accord. Decrivez ce qui ne marche pas, la page concernee et le moment exact du probleme. "
            "Une capture est utile mais pas obligatoire. Vous pouvez envoyer cette conversation au support."
        )
    return (
        "Merci pour votre message. Je peux vous aider en darija, francais ou anglais. "
        "Expliquez le probleme avec plus de details, puis envoyez la conversation a l'admin si vous voulez une intervention."
    )


def support_bot_transcript(messages):
    lines = []
    for message in messages:
        role = "Utilisateur" if message.get("role") == "user" else "Assistant support"
        lines.append(f"{role}: {message.get('content', '')}")
    return "\n\n".join(lines).strip()


def show_support_assistant(data, user_label, user_email, user_role):
    if "support_bot_open" not in st.session_state:
        st.session_state.support_bot_open = False
    if "support_bot_messages" not in st.session_state:
        st.session_state.support_bot_messages = [
            {
                "role": "assistant",
                "content": "Salam, bonjour. Expliquez votre probleme en darija, francais ou anglais, je vais vous orienter.",
            }
        ]

    col1, col2 = st.columns([1, 3])
    if col1.button("Assistant support", key="open_support_assistant"):
        st.session_state.support_bot_open = not st.session_state.support_bot_open

    if not st.session_state.support_bot_open:
        return

    st.markdown("#### Assistant support")
    for index, message in enumerate(st.session_state.support_bot_messages):
        role_label = "Vous" if message.get("role") == "user" else "Assistant"
        bubble_class = "chat-user" if message.get("role") == "user" else "chat-assistant"
        st.markdown(
            f"""
            <div class="{bubble_class}">
                <strong>{role_label}</strong><br>
                {html.escape(message.get('content', ''))}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.form("support_bot_form", clear_on_submit=True):
        user_message = st.text_area(
            "Votre message",
            placeholder="Exemple: ma kaykhdemch lien dyal cours marketing / je n'arrive pas a ouvrir le PDF...",
            key="support_bot_input",
        )
        send_bot_message = st.form_submit_button("Envoyer a l'assistant")

    if send_bot_message:
        if not user_message.strip():
            st.error("Ecrivez votre message d'abord.")
        else:
            st.session_state.support_bot_messages.append({"role": "user", "content": user_message.strip()})
            st.session_state.support_bot_messages.append(
                {"role": "assistant", "content": support_bot_answer(user_message)}
            )
            st.rerun()

    col_send, col_reset = st.columns(2)
    if col_send.button("Envoyer cette conversation a l'admin", key="send_support_bot_to_admin"):
        transcript = support_bot_transcript(st.session_state.support_bot_messages)
        if not any(message.get("role") == "user" for message in st.session_state.support_bot_messages):
            st.error("Discutez d'abord avec l'assistant avant d'envoyer a l'admin.")
        else:
            data.setdefault("support_tickets", []).insert(
                0,
                {
                    "type": "Assistant support",
                    "nom": user_label or "Utilisateur",
                    "email": user_email,
                    "role": user_role,
                    "sujet": "Conversation envoyee depuis l'assistant support",
                    "message": transcript,
                    "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "statut": "Nouveau",
                    "reponse": "",
                    "date_reponse": "",
                    "screenshot_path": "",
                    "screenshot_name": "",
                    "screenshot_mime": "",
                },
            )
            save_data(data)
            st.success("Conversation envoyee a l'admin.")
            st.session_state.support_bot_messages = [
                {
                    "role": "assistant",
                    "content": "Votre conversation a ete envoyee. Vous pouvez commencer une nouvelle demande si besoin.",
                }
            ]
            st.rerun()

    if col_reset.button("Nouvelle conversation", key="reset_support_bot"):
        st.session_state.support_bot_messages = [
            {
                "role": "assistant",
                "content": "Salam, bonjour. Expliquez votre probleme en darija, francais ou anglais, je vais vous orienter.",
            }
        ]
        st.rerun()


def platform_users_directory(data):
    users = [
        {
            "email": STUDENT_EMAIL,
            "name": "Compte etudiant general",
            "role": "Etudiant general",
        },
        {
            "email": GUEST_EMAIL,
            "name": "Compte invite test",
            "role": "Invite",
        },
        {
            "email": DIRECTION_EMAIL,
            "name": "Direction BTS SMARTCAMPUS",
            "role": "Direction",
        },
    ]

    for email, account in data.get("prof_accounts", {}).items():
        users.append(
            {
                "email": email,
                "name": account.get("name", "Professeur"),
                "role": account.get("role", "prof"),
            }
        )

    for email, account in data.get("student_accounts", {}).items():
        users.append(
            {
                "email": email,
                "name": f"{account.get('prenom', '')} {account.get('nom', '')}".strip() or "Etudiant",
                "role": f"Etudiant - {account.get('groupe', 'Sans groupe')}",
            }
        )

    seen = set()
    unique_users = []
    for user in users:
        if user["email"] and user["email"] not in seen:
            unique_users.append(user)
            seen.add(user["email"])
    return unique_users


def parse_date(value):
    for date_format in ("%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(value, date_format)
        except (TypeError, ValueError):
            continue
    return datetime.min


def is_new(value, days=7):
    parsed = parse_date(value)
    if parsed == datetime.min:
        return False
    return (datetime.now() - parsed).days <= days


def all_course_items(data):
    items = []
    for subject, resources in data.get("cours", {}).items():
        for resource in resources:
            item = resource.copy()
            item["matiere"] = subject
            items.append(item)
    return items


def search_courses(data, query, resource_type="Tous", status="Tous"):
    query = query.strip().lower()
    results = []

    for item in all_course_items(data):
        text = " ".join(
            [
                item.get("titre", ""),
                item.get("description", ""),
                item.get("matiere", ""),
                item.get("type", ""),
                item.get("statut", ""),
            ]
        ).lower()
        type_ok = resource_type == "Tous" or item.get("type") == resource_type
        status_ok = status == "Tous" or item.get("statut") == status
        query_ok = not query or query in text
        if type_ok and status_ok and query_ok:
            results.append(item)

    return sorted(results, key=lambda item: parse_date(item.get("date")), reverse=True)


def latest_updates(data, limit=8):
    items = all_course_items(data)
    return sorted(items, key=lambda item: parse_date(item.get("date")), reverse=True)[:limit]


def update_identity(item):
    parts = [
        item.get("matiere", ""),
        item.get("titre", ""),
        item.get("type", ""),
        item.get("statut", ""),
        item.get("date", ""),
        item.get("url", ""),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def current_user_key():
    email = st.session_state.get("platform_user_email", "").strip().lower()
    role = st.session_state.get("platform_user_role", "student")
    return email or f"session-{role}"


def seen_update_ids(data):
    seen = data.setdefault("seen_updates", {})
    return set(seen.setdefault(current_user_key(), []))


def unread_updates(data, limit=4):
    seen_ids = seen_update_ids(data)
    items = latest_updates(data, limit=50)
    return [item for item in items if update_identity(item) not in seen_ids][:limit]


def mark_updates_seen(data, items):
    if not items:
        return
    seen = data.setdefault("seen_updates", {})
    key = current_user_key()
    current_seen = set(seen.setdefault(key, []))
    before = len(current_seen)
    current_seen.update(update_identity(item) for item in items)
    if len(current_seen) != before:
        seen[key] = sorted(current_seen)
        save_data(data)


def parse_deadline(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError):
        return datetime.max


def is_weekend_date(value):
    parsed = parse_deadline(value)
    if parsed == datetime.max:
        return False
    return parsed.weekday() >= 5


def deadline_label(value):
    deadline = parse_deadline(value)
    if deadline == datetime.max:
        return "Date non indiquee"

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    days_left = (deadline - today).days
    if days_left < 0:
        return f"En retard depuis {abs(days_left)} jour(s)"
    if days_left == 0:
        return "A rendre aujourd'hui"
    if days_left == 1:
        return "A rendre demain"
    return f"Dans {days_left} jour(s)"


def weekday_exam_options(days=180):
    today = datetime.now().date()
    options = []
    for offset in range(days):
        day = today + timedelta(days=offset)
        if day.weekday() < 5:
            label = day.strftime("%d/%m/%Y")
            options.append((label, day.strftime("%Y-%m-%d")))
    return options


def month_options(months=8):
    today = datetime.now().date().replace(day=1)
    options = []
    year = today.year
    month = today.month
    for _ in range(months):
        label = datetime(year, month, 1).strftime("%B %Y")
        options.append((label, year, month))
        month += 1
        if month > 12:
            month = 1
            year += 1
    return options


def format_exam_date(value):
    parsed = parse_deadline(value)
    if parsed == datetime.max:
        return "Aucune date choisie"
    return parsed.strftime("%d/%m/%Y")


def weekday_calendar_picker(key_prefix):
    selected_key = f"{key_prefix}_selected_exam_date"
    month_key = f"{key_prefix}_calendar_month"

    if selected_key not in st.session_state:
        st.session_state[selected_key] = ""

    options = month_options()
    selected_month = st.selectbox(
        "Mois de l'examen",
        options,
        format_func=lambda option: option[0],
        key=month_key,
        help="Choisissez le mois, puis cliquez sur une date disponible.",
    )

    _, year, month = selected_month
    today = datetime.now().date()
    days = [
        day
        for day in calendar.Calendar(firstweekday=0).itermonthdates(year, month)
        if day.month == month and day.weekday() < 5 and day >= today
    ]

    st.markdown("#### Choisir une date")
    st.caption("Les week-ends sont retires du calendrier.")

    header_cols = st.columns(5)
    for col, label in zip(header_cols, ["Lun", "Mar", "Mer", "Jeu", "Ven"]):
        col.markdown(f"**{label}**")

    weeks = []
    week = []
    for day in calendar.Calendar(firstweekday=0).itermonthdates(year, month):
        if day.month != month:
            continue
        if day.weekday() >= 5:
            continue
        week.append(day)
        if len(week) == 5:
            weeks.append(week)
            week = []
    if week:
        weeks.append(week)

    for week_index, week_days in enumerate(weeks):
        cols = st.columns(5)
        for col_index, col in enumerate(cols):
            if col_index >= len(week_days):
                col.write("")
                continue

            day = week_days[col_index]
            if day < today:
                col.button(str(day.day), disabled=True, key=f"{key_prefix}_disabled_{day}")
                continue

            iso_date = day.strftime("%Y-%m-%d")
            is_selected = st.session_state[selected_key] == iso_date
            label = f"> {day.day}" if is_selected else str(day.day)
            if col.button(label, key=f"{key_prefix}_day_{week_index}_{iso_date}"):
                st.session_state[selected_key] = iso_date
                st.rerun()

    selected_date = st.session_state[selected_key]
    st.info(f"Date selectionnee: {format_exam_date(selected_date)}")
    return selected_date


def inject_style():
    st.markdown(
        """
        <style>
        .stApp {
            background: #f6f7fb;
            color: #111827;
        }

        @keyframes fadeSlideIn {
            from {
                opacity: 0;
                transform: translateY(14px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes softZoomIn {
            from {
                opacity: 0;
                transform: scale(0.985);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }

        @keyframes buttonPress {
            0% {
                transform: scale(1);
            }
            50% {
                transform: scale(0.97);
            }
            100% {
                transform: scale(1);
            }
        }

        @keyframes entryReveal {
            0% {
                opacity: 1;
                transform: scale(1);
            }
            65% {
                opacity: 1;
                transform: scale(1.015);
            }
            100% {
                opacity: 0;
                transform: scale(1.035);
                visibility: hidden;
            }
        }

        @keyframes entryText {
            0% {
                opacity: 0;
                transform: translateY(18px);
            }
            30% {
                opacity: 1;
                transform: translateY(0);
            }
            80% {
                opacity: 1;
                transform: translateY(0);
            }
            100% {
                opacity: 0;
                transform: translateY(-10px);
            }
        }

        @keyframes loginGatewayReveal {
            0% {
                opacity: 1;
                clip-path: circle(130% at 50% 50%);
            }
            62% {
                opacity: 1;
                clip-path: circle(130% at 50% 50%);
            }
            100% {
                opacity: 0;
                clip-path: circle(0% at 50% 50%);
                visibility: hidden;
            }
        }

        @keyframes loginGatewayCard {
            0% {
                opacity: 0;
                transform: translateY(28px) scale(0.92) rotateX(8deg);
            }
            22% {
                opacity: 1;
                transform: translateY(0) scale(1) rotateX(0deg);
            }
            62% {
                opacity: 1;
                transform: translateY(0) scale(1.02) rotateX(0deg);
            }
            100% {
                opacity: 0;
                transform: translateY(-34px) scale(1.08) rotateX(-8deg);
            }
        }

        @keyframes loginGatewaySweep {
            0% {
                transform: translateX(-120%) rotate(10deg);
                opacity: 0;
            }
            32% {
                opacity: 0.95;
            }
            76% {
                opacity: 0.55;
            }
            100% {
                transform: translateX(120%) rotate(10deg);
                opacity: 0;
            }
        }

        @keyframes loginGatewayDot {
            0%, 100% {
                transform: translateY(0) scale(1);
                opacity: 0.55;
            }
            50% {
                transform: translateY(-16px) scale(1.15);
                opacity: 1;
            }
        }

        .entry-transition {
            position: fixed;
            inset: 0;
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
            background:
                linear-gradient(135deg, rgba(18, 53, 91, 0.98), rgba(36, 123, 123, 0.96));
            color: #ffffff;
            pointer-events: none;
            animation: entryReveal 1.25s ease forwards;
        }

        .entry-transition-content {
            text-align: center;
            color: #ffffff;
            animation: entryText 1.15s ease forwards;
        }

        .entry-transition-content h2 {
            color: #ffffff;
            font-size: 48px;
            margin: 0 0 10px 0;
            letter-spacing: 0;
            font-weight: 900;
        }

        .entry-transition-content p {
            color: #ffffff;
            font-size: 18px;
            margin: 0;
            font-weight: 700;
        }

        .login-gateway-transition {
            position: fixed;
            inset: 0;
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
            background:
                radial-gradient(circle at 50% 45%, rgba(96, 165, 250, 0.36), transparent 28%),
                radial-gradient(circle at 70% 62%, rgba(139, 92, 246, 0.34), transparent 30%),
                linear-gradient(135deg, #04112f 0%, #10115a 48%, #28105f 100%);
            color: #ffffff;
            pointer-events: none;
            overflow: hidden;
            animation: loginGatewayReveal 2.15s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }

        .login-gateway-transition::before {
            content: "";
            position: absolute;
            width: 46vw;
            height: 160vh;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.24), transparent);
            filter: blur(10px);
            animation: loginGatewaySweep 1.85s ease-in-out forwards;
        }

        .login-gateway-transition::after {
            content: "";
            position: absolute;
            inset: 8%;
            border-radius: 34px;
            border: 1px solid rgba(255,255,255,0.14);
            box-shadow: inset 0 0 80px rgba(96,165,250,0.12);
        }

        .login-gateway-card {
            position: relative;
            z-index: 2;
            width: min(560px, 86vw);
            min-height: 260px;
            border-radius: 28px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.22);
            box-shadow: 0 30px 90px rgba(0, 0, 0, 0.32);
            backdrop-filter: blur(16px);
            animation: loginGatewayCard 2.05s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }

        .login-gateway-mark {
            width: 78px;
            height: 78px;
            border-radius: 22px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 22px;
            background: linear-gradient(135deg, #38bdf8, #7c3aed);
            color: #ffffff !important;
            font-size: 34px;
            font-weight: 950;
            box-shadow: 0 24px 50px rgba(79, 70, 229, 0.34);
        }

        .login-gateway-card h2 {
            color: #ffffff !important;
            font-size: 44px;
            line-height: 1;
            font-weight: 950;
            margin: 0 0 12px 0;
        }

        .login-gateway-card h2 span {
            color: #60a5fa !important;
        }

        .login-gateway-card p {
            color: #dbeafe !important;
            font-size: 17px;
            font-weight: 800;
            margin: 0;
        }

        .login-gateway-dots {
            display: flex;
            gap: 10px;
            margin-top: 24px;
        }

        .login-gateway-dots span {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            background: #93c5fd;
            animation: loginGatewayDot 850ms ease-in-out infinite;
        }

        .login-gateway-dots span:nth-child(2) {
            animation-delay: 120ms;
            background: #a78bfa;
        }

        .login-gateway-dots span:nth-child(3) {
            animation-delay: 240ms;
            background: #22d3ee;
        }

        .main .block-container {
            animation: fadeSlideIn 180ms ease-out;
        }

        .stApp,
        .stApp p,
        .stApp label,
        .stApp span,
        .stApp div {
            color: #111827;
        }

        .welcome-screen,
        .welcome-screen p,
        .welcome-screen div,
        .hero,
        .hero p {
            color: #ffffff !important;
        }

        .main .block-container {
            max-width: 1180px;
            padding-top: 1.6rem;
            padding-bottom: 2rem;
        }

        .hero {
            background: linear-gradient(135deg, #12355b, #247b7b);
            color: white;
            border-radius: 8px;
            padding: 32px;
            margin-bottom: 22px;
            animation: softZoomIn 520ms ease-out;
        }

        .hero h1 {
            margin: 0 0 8px 0;
            font-size: 42px;
            letter-spacing: 0;
        }

        .hero p {
            max-width: 820px;
            margin: 0;
            font-size: 17px;
            line-height: 1.55;
        }

        .welcome-shell {
            min-height: 520px;
            margin: -1.6rem calc(50% - 50vw) 0 calc(50% - 50vw);
            background:
                radial-gradient(circle at 78% 45%, rgba(124, 58, 237, 0.40), transparent 24%),
                radial-gradient(circle at 26% 24%, rgba(14, 165, 233, 0.22), transparent 26%),
                radial-gradient(circle at 60% 85%, rgba(59, 130, 246, 0.22), transparent 28%),
                linear-gradient(135deg, #07142f 0%, #090b2f 48%, #170837 100%);
            background-size: cover;
            background-position: center;
            color: #ffffff;
            animation: fadeSlideIn 220ms ease-out;
            position: relative;
            overflow: hidden;
            border-radius: 0 0 46px 46px;
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
        }

        .welcome-shell::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(rgba(96, 165, 250, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(96, 165, 250, 0.05) 1px, transparent 1px);
            background-size: 36px 36px;
            mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.72), transparent 88%);
            pointer-events: none;
        }

        .welcome-shell::after {
            content: "";
            position: absolute;
            left: -5%;
            right: -5%;
            bottom: -72px;
            height: 148px;
            background: #f6f8fc;
            border-radius: 50% 50% 0 0;
            z-index: 1;
        }

        .welcome-topbar {
            min-height: 70px;
            background: rgba(6, 13, 42, 0.78);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 0 6vw;
            gap: 24px;
            backdrop-filter: blur(14px);
            border-bottom: 1px solid rgba(148, 163, 184, 0.16);
            position: relative;
            z-index: 3;
        }

        .welcome-nav {
            display: flex;
            gap: 30px;
            align-items: center;
            justify-content: center;
            color: rgba(255, 255, 255, 0.82);
            font-size: 14px;
            font-weight: 900;
            text-transform: none;
        }

        .welcome-nav-item {
            color: rgba(255, 255, 255, 0.82) !important;
            position: relative;
        }

        .welcome-nav-item.active {
            color: #ffffff !important;
        }

        .welcome-nav-item.active::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: -18px;
            height: 2px;
            border-radius: 999px;
            background: linear-gradient(90deg, #22d3ee, #7c3aed);
            box-shadow: 0 0 18px rgba(34, 211, 238, 0.55);
        }

        .welcome-tools {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            gap: 12px;
        }

        .welcome-tool {
            width: 46px;
            height: 46px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #ffffff !important;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.10);
            font-size: 22px;
        }

        .welcome-space {
            color: #ffffff !important;
            border-radius: 8px;
            padding: 13px 18px;
            font-weight: 950;
            background: linear-gradient(135deg, #1fb6ff, #7c3aed);
            box-shadow: 0 18px 40px rgba(124, 58, 237, 0.28);
        }

        .welcome-tags,
        .welcome-tags-outside {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            justify-content: center;
            max-width: 860px;
            margin: 14px auto 0 auto;
        }

        .welcome-tag {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 8px 13px;
            font-size: 13px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0;
            border: 1px solid rgba(255, 255, 255, 0.14);
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.22);
        }

        .tag-academy {
            background: rgba(34, 211, 238, 0.13);
            color: #67e8f9 !important;
        }

        .tag-ressources {
            background: rgba(124, 58, 237, 0.16);
            color: #c4b5fd !important;
        }

        .tag-examens {
            background: rgba(59, 130, 246, 0.16);
            color: #93c5fd !important;
        }

        .tag-direction {
            background: rgba(236, 72, 153, 0.14);
            color: #f9a8d4 !important;
        }

        .welcome-brand {
            color: #ffffff;
            font-size: 34px;
            font-weight: 950;
            letter-spacing: 0;
            white-space: nowrap;
            text-shadow: 0 0 28px rgba(34, 211, 238, 0.25);
            display: flex;
            align-items: center;
            gap: 14px;
            line-height: 1;
            text-transform: uppercase;
        }

        .welcome-brand-mark {
            width: 44px;
            height: 44px;
            border-radius: 14px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background:
                linear-gradient(135deg, rgba(34, 211, 238, 0.18), rgba(124, 58, 237, 0.18)),
                rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(125, 211, 252, 0.30);
            box-shadow: 0 18px 38px rgba(14, 165, 233, 0.18);
            position: relative;
            overflow: hidden;
        }

        .welcome-brand-mark::before {
            content: "";
            width: 24px;
            height: 18px;
            border: 3px solid #38bdf8;
            border-top: 0;
            transform: skewX(-12deg) rotate(-8deg);
            box-shadow: inset 0 -8px 0 rgba(124, 58, 237, 0.36);
        }

        .welcome-brand-mark::after {
            content: "";
            position: absolute;
            width: 38px;
            height: 3px;
            background: linear-gradient(90deg, #38bdf8, #8b5cf6);
            top: 17px;
            transform: rotate(-8deg);
            border-radius: 999px;
        }

        .welcome-brand-text {
            display: flex;
            flex-direction: column;
            gap: 7px;
        }

        .welcome-brand-main {
            color: #ffffff !important;
            font-size: 28px;
            font-weight: 950;
        }

        .welcome-brand-main span {
            background: linear-gradient(90deg, #38bdf8, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent !important;
        }

        .welcome-brand-sub {
            color: rgba(255, 255, 255, 0.74) !important;
            font-size: 11px;
            letter-spacing: 7px;
            font-weight: 900;
        }

        .welcome-hero {
            min-height: 360px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 38px;
            padding: 30px 7vw 70px 7vw;
            position: relative;
            z-index: 2;
            perspective: 1100px;
        }

        .welcome-copy {
            max-width: 640px;
            color: #ffffff;
            animation: fadeSlideIn 260ms ease-out;
            position: relative;
            z-index: 2;
            background: transparent;
            border: 0;
            border-radius: 0;
            padding: 0;
            box-shadow: none;
            backdrop-filter: none;
        }

        .welcome-copy h1 {
            color: #ffffff;
            font-size: 44px;
            line-height: 1.08;
            margin: 0 0 14px 0;
            font-weight: 900;
            letter-spacing: 0;
            text-shadow: 0 18px 42px rgba(0, 0, 0, 0.34);
        }

        .welcome-copy h1 span {
            background: linear-gradient(90deg, #38bdf8, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent !important;
        }

        .welcome-copy p {
            color: rgba(226, 232, 240, 0.86);
            max-width: 560px;
            font-size: 16px;
            line-height: 1.42;
            margin: 0;
            font-weight: 700;
        }

        .welcome-copy::before {
            content: "Plateforme de revision intelligente";
            display: inline-block;
            color: #bae6fd;
            background: rgba(14, 165, 233, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.24);
            padding: 8px 13px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 900;
            margin-bottom: 12px;
            text-transform: uppercase;
        }

        .welcome-visual {
            width: min(420px, 38vw);
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 12px;
            position: relative;
            z-index: 2;
            transform-style: preserve-3d;
            animation: welcomeSceneTilt 7s ease-in-out infinite;
        }

        .welcome-visual::before {
            content: "";
            position: absolute;
            inset: 18px -10px -18px 12px;
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(34, 211, 238, 0.10), rgba(124, 58, 237, 0.14));
            border: 1px solid rgba(255, 255, 255, 0.10);
            transform: translateZ(-80px) rotateX(58deg);
            filter: blur(0.2px);
        }

        .welcome-mini-card {
            min-height: 92px;
            border-radius: 8px;
            padding: 14px;
            color: #ffffff;
            box-shadow: 0 26px 60px rgba(0, 0, 0, 0.30);
            border: 1px solid rgba(255, 255, 255, 0.16);
            position: relative;
            overflow: hidden;
            animation: miniCardIn 520ms ease-out both, miniCardFloat 4.8s ease-in-out infinite;
            transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
            backdrop-filter: blur(10px);
            grid-column: span 3;
            transform-style: preserve-3d;
        }

        .welcome-mini-card::after {
            content: "";
            position: absolute;
            width: 92px;
            height: 92px;
            border-radius: 999px;
            right: -30px;
            top: -30px;
            background: rgba(255, 255, 255, 0.16);
        }

        .welcome-mini-card:hover {
            transform: translateY(-10px) translateZ(42px) rotateX(3deg) rotateY(-4deg) scale(1.03);
            box-shadow: 0 30px 68px rgba(59, 130, 246, 0.26);
            filter: saturate(1.08);
        }

        .welcome-mini-card strong {
            display: block;
            color: #ffffff !important;
            font-size: 21px;
            line-height: 1;
            margin-bottom: 8px;
        }

        .welcome-mini-card span {
            color: rgba(255, 255, 255, 0.92) !important;
            font-size: 13px;
            font-weight: 900;
            line-height: 1.25;
        }

        .mini-cours {
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.95), rgba(59, 130, 246, 0.92));
            animation-delay: 40ms, 0ms;
            transform: translateZ(42px) rotateY(-7deg);
        }

        .mini-examens {
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.94), rgba(59, 130, 246, 0.88));
            margin-top: 16px;
            animation-delay: 120ms, 480ms;
            transform: translateZ(74px) rotateY(6deg);
        }

        .mini-drive {
            background: linear-gradient(135deg, rgba(49, 46, 129, 0.94), rgba(14, 165, 233, 0.82));
            animation-delay: 200ms, 240ms;
            transform: translateZ(24px) rotateY(-5deg);
        }

        .mini-profs {
            background: linear-gradient(135deg, rgba(126, 34, 206, 0.94), rgba(236, 72, 153, 0.84));
            margin-top: 16px;
            animation-delay: 280ms, 720ms;
            transform: translateZ(58px) rotateY(7deg);
        }

        .welcome-orbit {
            position: absolute;
            width: 54px;
            height: 54px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff !important;
            font-size: 24px;
            font-weight: 950;
            border: 1px solid rgba(255, 255, 255, 0.20);
            box-shadow: 0 22px 48px rgba(0, 0, 0, 0.24);
            transform-style: preserve-3d;
            animation: orbitFloat 5.4s ease-in-out infinite;
            z-index: 3;
        }

        .orbit-one {
            right: min(37vw, 455px);
            top: 92px;
            background: linear-gradient(135deg, #1fb6ff, #2563eb);
        }

        .orbit-two {
            right: min(8vw, 105px);
            top: 132px;
            background: linear-gradient(135deg, #7c3aed, #ec4899);
            animation-delay: 820ms;
        }

        .orbit-three {
            right: min(25vw, 310px);
            bottom: 84px;
            background: linear-gradient(135deg, #4338ca, #22d3ee);
            animation-delay: 420ms;
        }

        .welcome-feature-row {
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            margin-top: 18px;
        }

        .welcome-feature {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            color: rgba(226, 232, 240, 0.88) !important;
            font-size: 13px;
            font-weight: 900;
        }

        .welcome-feature b {
            color: #38bdf8 !important;
            font-size: 24px;
            line-height: 1;
        }

        @keyframes miniCardIn {
            from {
                opacity: 0;
                transform: translateY(18px) scale(0.96);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        @keyframes miniCardFloat {
            0%, 100% {
                translate: 0 0 0;
            }
            50% {
                translate: 0 -8px 24px;
            }
        }

        @keyframes welcomeSceneTilt {
            0%, 100% {
                transform: rotateX(8deg) rotateY(-10deg);
            }
            50% {
                transform: rotateX(4deg) rotateY(-2deg) translateY(-6px);
            }
        }

        @keyframes orbitFloat {
            0%, 100% {
                transform: translate3d(0, 0, 70px) rotateX(10deg) rotateY(-12deg);
            }
            50% {
                transform: translate3d(0, -16px, 110px) rotateX(-4deg) rotateY(12deg);
            }
        }

        @keyframes iconPulse3d {
            0%, 100% {
                transform: translateY(0) scale(1) rotateZ(0deg);
                filter: saturate(1);
            }
            50% {
                transform: translateY(-5px) scale(1.06) rotateZ(-2deg);
                filter: saturate(1.15);
            }
        }

        @keyframes iconGlowRing {
            0%, 100% {
                box-shadow: 0 16px 34px rgba(79, 70, 229, 0.18);
            }
            50% {
                box-shadow: 0 20px 46px rgba(59, 130, 246, 0.34);
            }
        }

        @keyframes iconPopIn {
            from {
                opacity: 0;
                transform: translateY(10px) scale(0.92);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        @keyframes pageTransitionIn {
            from {
                opacity: 0;
                transform: translateY(22px) scale(0.985);
                filter: blur(8px);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
                filter: blur(0);
            }
        }

        @keyframes contentCascadeIn {
            from {
                opacity: 0;
                transform: translateY(20px) scale(0.99);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        @keyframes softShimmer {
            0% {
                transform: translateX(-140%) rotate(8deg);
                opacity: 0;
            }
            35% {
                opacity: 0.65;
            }
            100% {
                transform: translateX(140%) rotate(8deg);
                opacity: 0;
            }
        }

        @keyframes floatLogo {
            0%, 100% {
                transform: translateY(0) rotate(0deg);
            }
            50% {
                transform: translateY(-14px) rotate(1.5deg);
            }
        }

        @keyframes glowPulse {
            0%, 100% {
                box-shadow: 0 12px 30px rgba(18, 53, 91, 0.10);
            }
            50% {
                box-shadow: 0 18px 40px rgba(36, 123, 123, 0.18);
            }
        }

        .dashboard-stat-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            margin: 12px 0 24px 0;
        }

        .dashboard-stat {
            border-radius: 8px;
            padding: 18px;
            min-height: 118px;
            color: #ffffff;
            position: relative;
            overflow: hidden;
            box-shadow: 0 14px 32px rgba(15, 23, 42, 0.16);
            animation: fadeSlideIn 180ms ease-out;
        }

        .dashboard-stat::after {
            content: "";
            position: absolute;
            width: 110px;
            height: 110px;
            border-radius: 999px;
            right: -28px;
            top: -28px;
            background: rgba(255, 255, 255, 0.16);
        }

        .dashboard-stat .label {
            color: rgba(255, 255, 255, 0.88) !important;
            font-size: 13px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0;
        }

        .dashboard-stat .value {
            color: #ffffff !important;
            font-size: 34px;
            font-weight: 950;
            margin-top: 8px;
        }

        .stat-blue {
            background: linear-gradient(135deg, #12355b, #2563eb);
        }

        .stat-teal {
            background: linear-gradient(135deg, #0f766e, #22c55e);
        }

        .stat-amber {
            background: linear-gradient(135deg, #b45309, #f59e0b);
        }

        .stat-violet {
            background: linear-gradient(135deg, #5b21b6, #0891b2);
        }

        .welcome-actions {
            max-width: 420px;
            margin: -62px auto 0 auto;
            position: relative;
            z-index: 4;
        }

        .welcome-actions div[data-testid="stButton"] > button {
            background: linear-gradient(135deg, #12355b, #0f766e) !important;
            border-color: rgba(255, 255, 255, 0.18) !important;
            color: #ffffff !important;
            min-height: 48px;
            font-size: 17px !important;
            box-shadow: 0 18px 36px rgba(79, 70, 229, 0.32) !important;
        }

        .welcome-actions div[data-testid="stButton"] > button * {
            color: #ffffff !important;
            font-weight: 950 !important;
        }

        .platform-login-shell {
            min-height: 74vh;
            border-radius: 28px;
            padding: 26px;
            background:
                radial-gradient(circle at 80% 18%, rgba(139, 92, 246, 0.22), transparent 30%),
                radial-gradient(circle at 18% 84%, rgba(14, 165, 233, 0.18), transparent 30%),
                linear-gradient(135deg, #06143a 0%, #10115a 48%, #24105e 100%);
            border: 1px solid rgba(255, 255, 255, 0.16);
            box-shadow: 0 30px 90px rgba(15, 23, 42, 0.24);
            overflow: hidden;
            position: relative;
        }

        .platform-login-shell::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(115deg, transparent 0 44%, rgba(255,255,255,0.08) 45% 46%, transparent 47%),
                radial-gradient(circle at 72% 62%, rgba(96, 165, 250, 0.18), transparent 22%);
            pointer-events: none;
        }

        .platform-login-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            z-index: 2;
            margin-bottom: 34px;
        }

        .platform-login-brand {
            color: #ffffff !important;
            font-size: 28px;
            font-weight: 950;
        }

        .platform-login-brand span {
            color: #38bdf8 !important;
        }

        .platform-login-pill {
            color: #dbeafe !important;
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 999px;
            padding: 10px 14px;
            font-size: 13px;
            font-weight: 900;
            background: rgba(255,255,255,0.08);
        }

        .platform-login-hero {
            display: grid;
            grid-template-columns: minmax(0, 1.05fr) minmax(320px, 0.95fr);
            gap: 34px;
            align-items: center;
            position: relative;
            z-index: 2;
        }

        .platform-login-copy h1 {
            color: #ffffff !important;
            font-size: 54px;
            line-height: 1.05;
            margin: 0 0 18px 0;
            font-weight: 950;
        }

        .platform-login-copy h1 span {
            color: #60a5fa !important;
        }

        .platform-login-copy p {
            color: #cbd5e1 !important;
            font-size: 18px;
            line-height: 1.7;
            font-weight: 750;
            max-width: 650px;
            margin: 0;
        }

        .platform-login-card {
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid rgba(255,255,255,0.28);
            box-shadow: 0 26px 70px rgba(0, 0, 0, 0.26);
            padding: 30px;
        }

        .platform-login-card-title {
            color: #0f1f44 !important;
            font-size: 28px;
            font-weight: 950;
            margin: 0 0 8px 0;
        }

        .platform-login-card-subtitle {
            color: #64748b !important;
            font-size: 15px;
            font-weight: 800;
            margin-bottom: 22px;
        }

        .platform-login-note {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-top: 18px;
            color: #64748b !important;
            font-size: 13px;
            font-weight: 800;
        }

        .platform-login-note span:first-child {
            width: 28px;
            height: 28px;
            border-radius: 999px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: #eef2ff;
            color: #4f46e5 !important;
            font-weight: 950;
            flex: 0 0 auto;
        }

        .welcome-tags-outside {
            margin-bottom: 6px;
        }

        @media (max-width: 860px) {
            .welcome-topbar {
                grid-template-columns: 1fr;
                text-align: center;
                padding: 20px;
            }

            .welcome-nav,
            .welcome-nav.right {
                justify-content: center;
                gap: 18px;
                flex-wrap: wrap;
            }

            .welcome-brand {
                font-size: 26px;
            }

            .welcome-hero {
                justify-content: center;
                flex-direction: column;
                padding: 24px 6vw 52px 6vw;
            }

            .welcome-visual {
                width: min(100%, 520px);
            }

            .welcome-copy h1 {
                font-size: 36px;
            }

            .welcome-copy p {
                font-size: 17px;
            }

            .platform-login-shell {
                padding: 18px !important;
                border-radius: 18px !important;
            }

            .platform-login-top {
                align-items: flex-start;
                flex-direction: column;
                gap: 12px;
            }

            .platform-login-hero {
                display: block !important;
            }

            .platform-login-copy h1 {
                font-size: 34px !important;
            }

            .platform-login-copy p {
                font-size: 15px !important;
                margin-bottom: 22px !important;
            }

            .platform-login-card {
                padding: 20px !important;
                border-radius: 14px !important;
            }

        }

        @media (max-width: 900px) {
            .dashboard-stat-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 560px) {
            .dashboard-stat-grid {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 14px;
            box-shadow: 0 8px 22px rgba(18, 53, 91, 0.06);
            color: #111827;
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
            animation: fadeSlideIn 180ms ease-out;
        }

        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 14px 30px rgba(18, 53, 91, 0.12);
            border-color: #b8dfd8;
        }

        .card h3 {
            color: #12355b;
            font-size: 19px;
            margin: 0 0 6px 0;
        }

        .badge {
            display: inline-block;
            background: #e8f5f3;
            color: #145c5c;
            border: 1px solid #b8dfd8;
            border-radius: 999px;
            padding: 4px 9px;
            font-size: 12px;
            font-weight: 800;
            margin-right: 6px;
            margin-bottom: 8px;
        }

        .badge-new {
            background: #fff3cd;
            border-color: #f7d774;
            color: #7a4f01;
        }

        .badge-important {
            background: #fee2e2;
            border-color: #fecaca;
            color: #991b1b;
        }

        .muted {
            color: #5f6c7b;
            font-size: 14px;
            margin-bottom: 10px;
        }

        .message {
            background: #ffffff;
            border-left: 4px solid #247b7b;
            border-radius: 7px;
            padding: 14px 16px;
            margin-bottom: 12px;
            color: #111827;
        }

        .message-important {
            border-left-color: #dc2626;
            background: #fff7f7;
        }

        .message-title {
            color: #111827;
            font-weight: 800;
            font-size: 17px;
        }

        .message-meta {
            color: #374151;
            font-weight: 700;
            font-size: 13px;
            margin-top: 4px;
            margin-bottom: 8px;
        }

        .message-content {
            color: #111827;
            font-weight: 600;
            line-height: 1.5;
        }

        .subject-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
            min-height: 96px;
            margin-bottom: 10px;
            box-shadow: 0 8px 22px rgba(18, 53, 91, 0.05);
            color: #111827;
            transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease;
            animation: fadeSlideIn 160ms ease-out;
        }

        .subject-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 14px 30px rgba(18, 53, 91, 0.12);
            border-color: #b8dfd8;
        }

        .subject-card strong {
            color: #12355b;
            font-size: 17px;
        }

        .subject-action {
            margin-top: 10px;
            color: #0f766e;
            font-weight: 900;
            font-size: 13px;
            text-transform: uppercase;
        }

        .course-row {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            color: #111827;
            transition: transform 120ms ease, box-shadow 120ms ease;
            animation: fadeSlideIn 160ms ease-out;
        }

        .course-row:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(18, 53, 91, 0.10);
        }

        .section-title {
            color: #12355b;
            font-weight: 800;
            margin-top: 18px;
        }

        .homework-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-left: 5px solid #247b7b;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            color: #111827;
            box-shadow: 0 8px 22px rgba(18, 53, 91, 0.06);
            animation: fadeSlideIn 160ms ease-out;
        }

        .homework-card h3 {
            color: #12355b;
            margin: 0 0 8px 0;
        }

        .homework-meta {
            color: #374151;
            font-weight: 800;
            margin-bottom: 8px;
            font-size: 13px;
        }

        div[data-testid="column"] div[data-testid="stButton"] > button {
            min-height: 42px;
        }

        div[data-testid="stButton"] > button,
        div[data-testid="stLinkButton"] > a {
            background: #12355b !important;
            color: #ffffff !important;
            border: 1px solid #12355b !important;
            border-radius: 7px !important;
            font-weight: 800 !important;
            transition: transform 140ms ease, background 180ms ease, box-shadow 180ms ease !important;
            box-shadow: 0 8px 18px rgba(18, 53, 91, 0.16) !important;
        }

        div[data-testid="stButton"] > button:hover,
        div[data-testid="stLinkButton"] > a:hover {
            background: #247b7b !important;
            color: #ffffff !important;
            border-color: #247b7b !important;
            transform: translateY(-1px);
            box-shadow: 0 12px 24px rgba(36, 123, 123, 0.24) !important;
        }

        div[data-testid="stButton"] > button:active,
        div[data-testid="stLinkButton"] > a:active {
            animation: buttonPress 180ms ease;
            transform: scale(0.98);
        }

        div[data-testid="stButton"] > button p,
        div[data-testid="stButton"] > button span,
        div[data-testid="stLinkButton"] > a p,
        div[data-testid="stLinkButton"] > a span {
            color: #ffffff !important;
            font-weight: 800 !important;
        }

        div[data-testid="stButton"] > button[kind="secondary"] {
            background: #374151 !important;
            color: #ffffff !important;
            border-color: #374151 !important;
        }

        div[data-testid="stTabs"] button {
            color: #111827 !important;
            background: #ffffff !important;
            border: 1px solid #d1d5db !important;
            border-radius: 7px 7px 0 0 !important;
            font-weight: 800 !important;
            transition: background 180ms ease, color 180ms ease, transform 180ms ease;
        }

        div[data-testid="stTabs"] button:hover {
            transform: translateY(-1px);
        }

        div[data-testid="stTabs"] button p {
            color: #111827 !important;
            font-weight: 800 !important;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            background: #12355b !important;
            color: #ffffff !important;
            border-color: #12355b !important;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] p {
            color: #ffffff !important;
        }

        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea,
        div[data-baseweb="select"] > div {
            background: #ffffff !important;
            color: #111827 !important;
            border-color: #9ca3af !important;
        }

        div[data-baseweb="input"] input::placeholder,
        div[data-baseweb="textarea"] textarea::placeholder {
            color: #6b7280 !important;
        }

        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div {
            color: #111827 !important;
        }

        div[data-testid="stAlert"] div,
        div[data-testid="stAlert"] p {
            color: #111827 !important;
        }

        section[data-testid="stSidebar"] {
            background: #ffffff !important;
        }

        section[data-testid="stSidebar"] * {
            color: #111827 !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
            justify-content: flex-start !important;
            min-height: 44px;
            margin-bottom: 6px;
            box-shadow: none !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
            background: #12355b !important;
            border-color: #12355b !important;
            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] {
            background: #f3f4f6 !important;
            border-color: #d1d5db !important;
            color: #111827 !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] p,
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] span {
            color: #111827 !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] p,
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] span {
            color: #ffffff !important;
        }

        div[role="radiogroup"] {
            gap: 10px;
        }

        div[role="radiogroup"] label {
            background: #ffffff !important;
            border: 1px solid #d1d5db !important;
            border-radius: 999px !important;
            padding: 8px 14px !important;
            transition: background 180ms ease, transform 180ms ease, border-color 180ms ease;
        }

        div[role="radiogroup"] label:hover {
            transform: translateY(-1px);
            border-color: #247b7b !important;
        }

        div[role="radiogroup"] label:has(input:checked) {
            background: #12355b !important;
            border-color: #12355b !important;
        }

        div[role="radiogroup"] label:has(input:checked) * {
            color: #ffffff !important;
            font-weight: 900 !important;
        }

        button[data-testid="collapsedControl"],
        button[kind="header"],
        header button {
            background: #12355b !important;
            color: #ffffff !important;
            border: 1px solid #12355b !important;
            border-radius: 7px !important;
        }

        button[data-testid="collapsedControl"] svg,
        button[kind="header"] svg,
        header button svg {
            fill: #ffffff !important;
            color: #ffffff !important;
            stroke: #ffffff !important;
        }

        button[data-testid="collapsedControl"]:hover,
        button[kind="header"]:hover,
        header button:hover {
            background: #247b7b !important;
            border-color: #247b7b !important;
        }

        /* Final visual polish */
        html, body, [class*="css"] {
            font-family: "Inter", "Segoe UI", Arial, sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(36, 123, 123, 0.10), transparent 34%),
                linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
        }

        h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #102a43 !important;
            letter-spacing: 0 !important;
        }

        .main .block-container {
            max-width: 1220px;
        }

        .hero {
            background:
                linear-gradient(135deg, rgba(16, 42, 67, 0.95), rgba(36, 123, 123, 0.92)),
                url("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1600&q=80");
            background-size: cover;
            background-position: center;
            min-height: 240px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .hero-logo {
            width: 92px;
            height: 92px;
            object-fit: contain;
            background: rgba(255, 255, 255, 0.92);
            border-radius: 8px;
            padding: 8px;
            margin-bottom: 14px;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);
        }

        .hero h1 {
            font-size: 48px;
            color: #ffffff !important;
        }

        .hero p {
            font-size: 18px;
            color: #eef6f6 !important;
            font-weight: 650;
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 10px 28px rgba(16, 42, 67, 0.08);
        }

        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #102a43 !important;
            font-weight: 900 !important;
        }

        .card,
        .message,
        .homework-card,
        .course-row,
        .subject-card {
            border-radius: 8px;
            border: 1px solid #dde5ee;
            box-shadow: 0 12px 30px rgba(16, 42, 67, 0.08);
        }

        .card {
            border-top: 4px solid #247b7b;
        }

        .subject-card {
            border-top: 4px solid #f59e0b;
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(239, 246, 255, 0.98));
        }

        .course-row {
            border-left: 5px solid #12355b;
        }

        .message {
            border-left-width: 6px;
        }

        .card h3,
        .homework-card h3,
        .course-row h3 {
            font-size: 18px;
            font-weight: 900;
        }

        .badge {
            text-transform: uppercase;
            letter-spacing: 0;
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, #0f172a 0%, #12355b 56%, #174e61 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.12);
        }

        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {
            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.08) !important;
            border-color: rgba(255, 255, 255, 0.16) !important;
            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] p,
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] span {
            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
            background: #f59e0b !important;
            border-color: #f59e0b !important;
            color: #111827 !important;
            box-shadow: 0 10px 22px rgba(245, 158, 11, 0.24) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] p,
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] span {
            color: #111827 !important;
        }

        div[data-testid="stButton"] > button,
        div[data-testid="stLinkButton"] > a,
        div[data-testid="stDownloadButton"] > button {
            min-height: 42px;
            border-radius: 8px !important;
        }

        div[data-testid="stDownloadButton"] > button {
            background: #0f766e !important;
            border-color: #0f766e !important;
            color: #ffffff !important;
            font-weight: 900 !important;
        }

        div[data-testid="stDownloadButton"] > button * {
            color: #ffffff !important;
        }

        .creator-footer {
            margin: 24px 0 0 auto;
            padding: 7px 10px;
            width: fit-content;
            text-align: right;
            color: #64748b;
            font-size: 12px;
            line-height: 1.2;
            font-weight: 750;
            border: 1px solid #e5eaf6;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.72);
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
        }

        .creator-footer strong {
            color: #4f46e5;
            font-weight: 900;
        }

        .welcome-topbar {
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.12);
        }

        .welcome-brand {
            color: #f59e0b !important;
            display: flex;
            align-items: center;
            gap: 12px;
            justify-content: center;
        }

        .welcome-logo {
            width: 58px;
            height: 58px;
            object-fit: contain;
            background: rgba(255, 255, 255, 0.92);
            border-radius: 8px;
            padding: 5px;
        }

        .sidebar-logo {
            width: 96px;
            height: 96px;
            object-fit: contain;
            display: block;
            margin: 4px auto 12px auto;
            background: rgba(255, 255, 255, 0.94);
            border-radius: 8px;
            padding: 8px;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22);
        }

        .welcome-copy h1 {
            text-shadow: 0 8px 28px rgba(0, 0, 0, 0.38);
        }

        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea,
        div[data-baseweb="select"] > div {
            border-radius: 8px !important;
            box-shadow: 0 6px 18px rgba(16, 42, 67, 0.06);
        }

        @media (max-width: 760px) {
            .hero h1 {
                font-size: 34px;
            }

            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }

        /* Dashboard premium style */
        .stApp {
            background: #f5f7ff;
        }

        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 72% 12%, rgba(99, 102, 241, 0.28), transparent 24%),
                linear-gradient(180deg, #07142f 0%, #0b1740 58%, #08122f 100%) !important;
            border-right: 0 !important;
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 18px;
        }

        section[data-testid="stSidebar"] h3 {
            color: #ffffff !important;
            font-size: 24px !important;
            font-weight: 950 !important;
            letter-spacing: 0 !important;
            margin-bottom: 2px !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] p {
            color: rgba(226, 232, 240, 0.74) !important;
            font-weight: 800 !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
            min-height: 52px !important;
            justify-content: flex-start !important;
            border-radius: 8px !important;
            padding: 0 18px !important;
            margin-bottom: 9px !important;
            font-weight: 950 !important;
            letter-spacing: 0 !important;
            transition: transform 140ms ease, box-shadow 140ms ease, background 140ms ease !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
            transform: translateX(4px);
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] {
            background: transparent !important;
            border-color: transparent !important;
            color: rgba(255, 255, 255, 0.88) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.08) !important;
            border-color: rgba(255, 255, 255, 0.10) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
            border-color: rgba(255, 255, 255, 0.14) !important;
            color: #ffffff !important;
            box-shadow: 0 18px 38px rgba(79, 70, 229, 0.34) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] *,
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] * {
            color: inherit !important;
            font-weight: 950 !important;
        }

        .app-topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid #e5e7f2;
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 16px;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
        }

        .app-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #111827 !important;
            font-size: 24px;
            font-weight: 950;
        }

        .app-brand span {
            color: #2563eb !important;
        }

        .app-search {
            flex: 1;
            max-width: 440px;
            background: #f7f8ff;
            border: 1px solid #dde3f3;
            color: #64748b !important;
            border-radius: 8px;
            padding: 13px 16px;
            font-weight: 800;
        }

        .app-notification {
            width: 44px;
            height: 44px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: #f7f8ff;
            border: 1px solid #dde3f3;
            color: #172554 !important;
            font-size: 22px;
            font-weight: 950;
            position: relative;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
        }

        .notification-action {
            max-width: 44px;
            margin: -66px 152px 22px auto;
            position: relative;
            z-index: 5;
        }

        .notification-action div[data-testid="stButton"] > button {
            width: 44px !important;
            min-width: 44px !important;
            height: 44px !important;
            min-height: 44px !important;
            padding: 0 !important;
            border-radius: 8px !important;
            background: #f7f8ff !important;
            border: 1px solid #dde3f3 !important;
            color: #172554 !important;
            font-size: 0 !important;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06) !important;
            position: relative;
            overflow: visible !important;
        }

        .notification-action div[data-testid="stButton"] > button p,
        .notification-action div[data-testid="stButton"] > button span,
        .notification-action div[data-testid="stButton"] > button div {
            font-size: 0 !important;
            line-height: 0 !important;
            color: transparent !important;
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
            overflow: hidden !important;
        }

        .notification-action div[data-testid="stButton"] > button::before {
            content: "";
            position: absolute;
            width: 16px;
            height: 18px;
            left: 13px;
            top: 11px;
            border: 2.5px solid #172554;
            border-bottom-width: 3px;
            border-radius: 12px 12px 7px 7px;
            box-shadow: 0 10px 0 -7px #172554;
        }

        .notification-action.has-updates div[data-testid="stButton"] > button::after {
            content: "";
            position: absolute;
            width: 11px;
            height: 11px;
            border-radius: 999px;
            right: 8px;
            top: 7px;
            background: #ef4444;
            border: 2px solid #ffffff;
            box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.14);
        }

        .notification-action.no-updates div[data-testid="stButton"] > button::after {
            content: none;
        }

        .app-notification::after {
            content: "";
            position: absolute;
            width: 11px;
            height: 11px;
            border-radius: 999px;
            right: 9px;
            top: 8px;
            background: #ef4444;
            border: 2px solid #ffffff;
            box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.14);
        }

        .app-user {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #334155 !important;
            font-weight: 900;
        }

        .app-user-avatar {
            width: 42px;
            height: 42px;
            border-radius: 999px;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            box-shadow: 0 12px 28px rgba(79, 70, 229, 0.24);
        }

        .dashboard-hero {
            min-height: 260px;
            border-radius: 8px;
            padding: 44px 48px;
            margin-bottom: 22px;
            background:
                radial-gradient(circle at 82% 40%, rgba(124, 58, 237, 0.46), transparent 24%),
                radial-gradient(circle at 64% 16%, rgba(59, 130, 246, 0.34), transparent 24%),
                linear-gradient(135deg, #07142f 0%, #111b63 58%, #312e81 100%);
            position: relative;
            overflow: hidden;
            box-shadow: 0 24px 60px rgba(30, 41, 113, 0.22);
        }

        .dashboard-hero::after {
            content: "";
            position: absolute;
            right: 54px;
            top: 38px;
            width: 310px;
            height: 180px;
            border-radius: 8px;
            background:
                linear-gradient(135deg, rgba(96, 165, 250, 0.18), rgba(124, 58, 237, 0.18)),
                rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.16);
            box-shadow: 0 28px 70px rgba(0, 0, 0, 0.22);
            transform: rotate(-3deg);
        }

        .dashboard-hero h1 {
            color: #ffffff !important;
            font-size: 46px;
            line-height: 1.08;
            margin: 0 0 14px 0;
            font-weight: 950;
            position: relative;
            z-index: 2;
        }

        .dashboard-hero h1 span {
            background: linear-gradient(90deg, #38bdf8, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent !important;
        }

        .dashboard-hero p {
            color: rgba(226, 232, 240, 0.88) !important;
            max-width: 620px;
            font-size: 17px;
            line-height: 1.55;
            margin: 0 0 24px 0;
            font-weight: 750;
            position: relative;
            z-index: 2;
        }

        .dashboard-hero-cta {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            color: #ffffff !important;
            background: linear-gradient(135deg, #1fb6ff, #7c3aed);
            border-radius: 8px;
            padding: 14px 24px;
            font-weight: 950;
            position: relative;
            z-index: 2;
            box-shadow: 0 18px 38px rgba(79, 70, 229, 0.34);
        }

        .dashboard-course-action {
            max-width: 245px;
            margin: -128px 0 88px 48px;
            position: relative;
            z-index: 5;
        }

        .dashboard-course-action div[data-testid="stButton"] > button {
            min-height: 52px !important;
            border-radius: 8px !important;
            background: linear-gradient(135deg, #1fb6ff, #7c3aed) !important;
            border-color: rgba(255, 255, 255, 0.18) !important;
            color: #ffffff !important;
            box-shadow: 0 18px 38px rgba(79, 70, 229, 0.34) !important;
            font-weight: 950 !important;
        }

        .dashboard-course-action div[data-testid="stButton"] > button * {
            color: #ffffff !important;
            font-weight: 950 !important;
        }

        .dashboard-stat-grid {
            gap: 18px;
            margin: 4px 0 24px 0;
        }

        .dashboard-stat {
            min-height: 132px;
            padding: 22px 22px 18px 22px;
            border-radius: 8px;
            box-shadow: 0 20px 42px rgba(15, 23, 42, 0.13);
        }

        .dashboard-stat .stat-icon {
            width: 48px;
            height: 48px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.22);
            color: #ffffff !important;
            font-size: 24px;
            font-weight: 950;
            margin-bottom: 10px;
        }

        .dashboard-stat .label {
            font-size: 12px;
        }

        .dashboard-stat .value {
            font-size: 32px;
            margin-top: 5px;
        }

        .dashboard-stat .hint {
            color: rgba(255, 255, 255, 0.88) !important;
            font-size: 13px;
            font-weight: 800;
            margin-top: 2px;
        }

        .stat-blue {
            background: linear-gradient(135deg, #2563eb, #38bdf8);
        }

        .stat-teal {
            background: linear-gradient(135deg, #059669, #5eead4);
        }

        .stat-amber {
            background: linear-gradient(135deg, #f97316, #fbbf24);
        }

        .stat-violet {
            background: linear-gradient(135deg, #5b21b6, #c084fc);
        }

        .homework-card,
        .card,
        .message {
            border-radius: 8px;
            box-shadow: 0 18px 44px rgba(15, 23, 42, 0.08);
            border-color: #e4e8f3;
        }

        .courses-hero {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
            margin: 2px 0 24px 0;
            padding: 22px 0 8px 0;
        }

        .courses-hero h1 {
            color: #0f1f44 !important;
            font-size: 36px;
            font-weight: 950;
            margin: 0 0 8px 0;
        }

        .courses-hero p {
            color: #64748b !important;
            font-size: 16px;
            font-weight: 750;
            margin: 0;
        }

        .courses-hero-art {
            width: 280px;
            height: 130px;
            border-radius: 8px;
            background:
                radial-gradient(circle at 26% 64%, rgba(99, 102, 241, 0.18), transparent 28%),
                radial-gradient(circle at 74% 42%, rgba(59, 130, 246, 0.22), transparent 30%),
                linear-gradient(135deg, #eef2ff, #ffffff);
            position: relative;
            overflow: hidden;
        }

        .courses-hero-art::before {
            content: "";
            position: absolute;
            width: 116px;
            height: 74px;
            right: 72px;
            bottom: 22px;
            border-radius: 8px;
            background: linear-gradient(135deg, #dbeafe, #818cf8);
            box-shadow: 0 16px 34px rgba(37, 99, 235, 0.18);
            transform: rotate(-5deg);
        }

        .courses-hero-art::after {
            content: "BTS";
            position: absolute;
            right: 102px;
            bottom: 44px;
            color: #ffffff;
            font-weight: 950;
            letter-spacing: 1px;
        }

        .subject-card {
            min-height: 188px;
            padding: 22px 20px 18px 20px;
            border-radius: 8px;
            border: 1px solid #e6eaf5;
            border-top: 4px solid var(--subject-color);
            background:
                radial-gradient(circle at 92% 18%, color-mix(in srgb, var(--subject-color) 16%, transparent), transparent 22%),
                #ffffff;
            box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
            display: grid;
            grid-template-columns: 72px 1fr;
            gap: 18px;
            align-items: start;
            margin-bottom: 12px;
        }

        .subject-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 26px 56px rgba(15, 23, 42, 0.13);
            border-color: color-mix(in srgb, var(--subject-color) 42%, #e6eaf5);
        }

        .subject-icon {
            width: 64px;
            height: 64px;
            border-radius: 999px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, var(--subject-color), color-mix(in srgb, var(--subject-color) 58%, #ffffff));
            color: #ffffff !important;
            font-size: 28px;
            font-weight: 950;
            box-shadow: 0 16px 34px color-mix(in srgb, var(--subject-color) 28%, transparent);
        }

        .subject-card strong {
            color: #0f1f44 !important;
            font-size: 18px;
            line-height: 1.22;
            display: block;
            margin-bottom: 8px;
        }

        .subject-count {
            color: var(--subject-color) !important;
            font-size: 14px;
            font-weight: 950;
            margin-bottom: 10px;
        }

        .subject-action {
            margin-top: 6px;
            color: var(--subject-color) !important;
            font-weight: 950;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0;
        }

        .subject-label {
            color: #64748b !important;
            font-size: 13px;
            font-weight: 800;
            margin-top: 6px;
        }

        .subject-card-button-space {
            grid-column: 1 / -1;
            height: 1px;
        }

        .contact-topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid #e5eaf6;
            border-radius: 8px;
            padding: 16px 22px;
            margin-bottom: 30px;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
        }

        .contact-brand {
            color: #0f1f44 !important;
            font-size: 28px;
            font-weight: 950;
        }

        .contact-brand span {
            color: #2563eb !important;
        }

        .contact-user {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #334155 !important;
            font-weight: 900;
        }

        .contact-avatar {
            width: 44px;
            height: 44px;
            border-radius: 999px;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            box-shadow: 0 12px 28px rgba(79, 70, 229, 0.24);
        }

        .contact-hero {
            min-height: 190px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 28px;
            margin-bottom: 18px;
            padding: 8px 0 0 0;
        }

        .contact-title-wrap {
            display: flex;
            align-items: center;
            gap: 22px;
        }

        .contact-icon {
            width: 78px;
            height: 78px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #4f46e5 !important;
            background: linear-gradient(135deg, #eef2ff, #ffffff);
            border: 1px solid #e5eaf6;
            box-shadow: 0 18px 40px rgba(79, 70, 229, 0.10);
            font-size: 34px;
            font-weight: 950;
        }

        .contact-hero h1 {
            color: #0f1f44 !important;
            font-size: 34px;
            font-weight: 950;
            margin: 0 0 10px 0;
        }

        .contact-hero p {
            color: #64748b !important;
            font-size: 16px;
            font-weight: 750;
            margin: 0;
        }

        .contact-art {
            width: min(420px, 38vw);
            height: 160px;
            border-radius: 8px;
            background:
                radial-gradient(circle at 28% 70%, rgba(99, 102, 241, 0.18), transparent 28%),
                radial-gradient(circle at 68% 52%, rgba(124, 58, 237, 0.18), transparent 30%),
                linear-gradient(135deg, #f8fbff, #eef2ff);
            position: relative;
            overflow: hidden;
        }

        .contact-art::before {
            content: "";
            position: absolute;
            right: 92px;
            top: 42px;
            width: 126px;
            height: 76px;
            border-radius: 8px;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            box-shadow: 0 20px 44px rgba(79, 70, 229, 0.22);
        }

        .contact-art::after {
            content: "";
            position: absolute;
            right: 44px;
            bottom: 28px;
            width: 112px;
            height: 56px;
            background: linear-gradient(135deg, #4338ca, #818cf8);
            clip-path: polygon(50% 0, 100% 35%, 50% 70%, 0 35%);
            filter: drop-shadow(0 18px 24px rgba(67, 56, 202, 0.22));
        }

        .contact-form-title {
            background: #ffffff;
            border: 1px solid #e5eaf6;
            border-bottom: 0;
            border-radius: 8px 8px 0 0;
            padding: 18px 22px;
            color: #0f1f44 !important;
            font-weight: 950;
            box-shadow: 0 18px 44px rgba(15, 23, 42, 0.06);
        }

        .contact-help {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-top: 12px;
            padding: 16px 18px;
            border-radius: 8px;
            background: #ffffff;
            border: 1px solid #e5eaf6;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
            color: #334155 !important;
            font-weight: 800;
        }

        .contact-help-icon {
            width: 44px;
            height: 44px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: #eef2ff;
            color: #4f46e5 !important;
            font-weight: 950;
            font-size: 20px;
        }

        .files-hero {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 28px;
            margin-bottom: 24px;
            padding: 12px 0 4px 0;
        }

        .files-title-wrap {
            display: flex;
            align-items: center;
            gap: 22px;
        }

        .files-icon {
            width: 82px;
            height: 82px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #4f46e5 !important;
            background: linear-gradient(135deg, #eef2ff, #ffffff);
            border: 1px solid #e5eaf6;
            box-shadow: 0 18px 40px rgba(79, 70, 229, 0.10);
            font-size: 34px;
            font-weight: 950;
        }

        .files-hero h1 {
            color: #0f1f44 !important;
            font-size: 38px;
            font-weight: 950;
            margin: 0 0 10px 0;
        }

        .files-hero p {
            color: #64748b !important;
            font-size: 16px;
            font-weight: 750;
            margin: 0;
        }

        .files-art {
            width: min(360px, 34vw);
            height: 170px;
            border-radius: 8px;
            background:
                radial-gradient(circle at 38% 36%, rgba(99, 102, 241, 0.18), transparent 30%),
                radial-gradient(circle at 78% 70%, rgba(124, 58, 237, 0.16), transparent 30%),
                linear-gradient(135deg, #f8fbff, #eef2ff);
            position: relative;
            overflow: hidden;
        }

        .files-art::before {
            content: "";
            position: absolute;
            width: 170px;
            height: 96px;
            right: 66px;
            bottom: 26px;
            border-radius: 8px 8px 18px 18px;
            background: linear-gradient(135deg, #7c3aed, #6366f1);
            box-shadow: 0 24px 52px rgba(79, 70, 229, 0.24);
        }

        .files-art::after {
            content: "";
            position: absolute;
            width: 84px;
            height: 84px;
            right: 106px;
            top: 18px;
            border-radius: 999px;
            background:
                linear-gradient(135deg, transparent 42%, #ffffff 43% 58%, transparent 59%),
                linear-gradient(90deg, transparent 42%, #ffffff 43% 58%, transparent 59%),
                #ffffff;
            filter: drop-shadow(0 18px 32px rgba(79, 70, 229, 0.20));
        }

        .shared-file-card {
            background: #ffffff;
            border: 1px solid #e5eaf6;
            border-top: 4px solid #8b5cf6;
            border-radius: 8px;
            padding: 26px 28px;
            margin: 24px 0 14px 0;
            box-shadow: 0 22px 54px rgba(15, 23, 42, 0.09);
        }

        .shared-file-head {
            display: flex;
            gap: 22px;
            align-items: flex-start;
        }

        .shared-file-icon {
            width: 66px;
            height: 66px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #6366f1, #7c3aed);
            color: #ffffff !important;
            font-size: 26px;
            font-weight: 950;
            box-shadow: 0 16px 34px rgba(99, 102, 241, 0.28);
            flex: 0 0 auto;
        }

        .shared-file-card h3 {
            color: #0f1f44 !important;
            font-size: 24px;
            font-weight: 950;
            margin: 2px 0 12px 0;
        }

        .shared-file-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            color: #536179 !important;
            font-size: 14px;
            font-weight: 850;
        }

        .shared-file-meta span {
            color: #536179 !important;
            padding-right: 12px;
            border-right: 1px solid #dbe3f2;
        }

        .shared-file-meta span:last-child {
            border-right: 0;
        }

        .shared-file-card p {
            color: #111827 !important;
            font-size: 16px;
            font-weight: 800;
            margin: 18px 0 0 88px;
        }

        .exam-page-shell {
            background: rgba(255, 255, 255, 0.68);
            border: 1px solid #dbe3f2;
            border-radius: 8px;
            padding: 34px;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.07);
        }

        .exam-hero {
            display: flex;
            align-items: center;
            gap: 28px;
            margin-bottom: 28px;
        }

        .exam-icon-main {
            width: 82px;
            height: 82px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #4f46e5 !important;
            background: linear-gradient(135deg, #eef2ff, #ffffff);
            border: 1px solid #d8ddff;
            box-shadow: 0 18px 40px rgba(79, 70, 229, 0.10);
            font-size: 36px;
            font-weight: 950;
        }

        .exam-hero h1 {
            color: #0f1f44 !important;
            font-size: 38px;
            font-weight: 950;
            margin: 0 0 10px 0;
        }

        .exam-hero p {
            color: #64748b !important;
            font-size: 16px;
            font-weight: 750;
            margin: 0;
        }

        .exam-card {
            min-height: 260px;
            border: 1px solid #c7c5ff;
            border-radius: 8px;
            background:
                radial-gradient(circle at 82% 48%, rgba(124, 58, 237, 0.12), transparent 24%),
                #ffffff;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
            padding: 34px;
            margin: 22px 0 18px 0;
            position: relative;
            overflow: hidden;
        }

        .exam-card::after {
            content: "";
            position: absolute;
            right: 42px;
            bottom: 0;
            width: 290px;
            height: 190px;
            background:
                radial-gradient(circle at 45% 20%, #ffffff 0 42px, transparent 43px),
                linear-gradient(135deg, #8b5cf6, #6366f1);
            opacity: 0.42;
            clip-path: polygon(12% 54%, 42% 54%, 42% 30%, 58% 30%, 58% 54%, 88% 54%, 88% 100%, 12% 100%);
        }

        .exam-card-head {
            display: flex;
            gap: 24px;
            align-items: flex-start;
            position: relative;
            z-index: 2;
        }

        .exam-card-icon {
            width: 72px;
            height: 72px;
            border-radius: 999px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: #eef2ff;
            color: #4f46e5 !important;
            font-size: 30px;
            font-weight: 950;
            box-shadow: inset 0 0 0 1px #dbe4ff;
            flex: 0 0 auto;
        }

        .exam-card h3 {
            color: #0f1f44 !important;
            font-size: 25px;
            font-weight: 950;
            margin: 6px 0 16px 0;
        }

        .exam-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            color: #64748b !important;
            font-size: 15px;
            font-weight: 850;
            margin: 14px 0 20px 0;
        }

        .exam-meta span {
            color: #64748b !important;
            padding-right: 12px;
            border-right: 1px solid #dbe3f2;
        }

        .exam-meta span:last-child {
            border-right: 0;
        }

        .exam-description {
            color: #111827 !important;
            font-size: 17px;
            font-weight: 800;
            position: relative;
            z-index: 2;
        }

        .exam-action-wrap {
            max-width: 240px;
            margin-bottom: 22px;
        }

        .planning-shell {
            background:
                radial-gradient(circle at 94% 18%, rgba(124, 58, 237, 0.08), transparent 24%),
                rgba(255, 255, 255, 0.76);
            border: 1px solid #dbe3f2;
            border-radius: 8px;
            padding: 34px;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.07);
            margin-bottom: 26px;
            overflow: hidden;
            position: relative;
        }

        .planning-hero {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 32px;
            min-height: 250px;
        }

        .planning-title-wrap {
            display: flex;
            align-items: flex-start;
            gap: 26px;
            position: relative;
            z-index: 2;
        }

        .planning-icon-main {
            width: 86px;
            height: 86px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #6d5dfc !important;
            background: linear-gradient(135deg, #f0edff, #ffffff);
            border: 1px solid #ddd7ff;
            box-shadow: 0 18px 40px rgba(109, 93, 252, 0.12);
            font-size: 34px;
            font-weight: 950;
            flex: 0 0 auto;
        }

        .planning-hero h1 {
            color: #0f1f44 !important;
            font-size: 42px;
            line-height: 1.05;
            font-weight: 950;
            margin: 18px 0 18px 0;
        }

        .planning-hero p {
            color: #64748b !important;
            font-size: 18px;
            font-weight: 750;
            margin: 0 0 10px 0;
        }

        .planning-hero strong {
            color: #6d5dfc !important;
            font-size: 18px;
            font-weight: 950;
        }

        .planning-art {
            width: min(420px, 36vw);
            height: 230px;
            position: relative;
            flex: 0 0 auto;
        }

        .planning-art::before {
            content: "";
            position: absolute;
            right: 52px;
            top: 8px;
            width: 220px;
            height: 160px;
            border-radius: 8px 8px 22px 22px;
            background:
                linear-gradient(#6d5dfc 0 38px, transparent 39px),
                repeating-linear-gradient(90deg, transparent 0 30px, rgba(255,255,255,0.56) 31px 46px, transparent 47px 70px),
                linear-gradient(135deg, #ffffff, #eceaff);
            border: 1px solid #d7d0ff;
            box-shadow: 0 28px 50px rgba(109, 93, 252, 0.24);
            transform: rotate(3deg);
        }

        .planning-art::after {
            content: "";
            position: absolute;
            right: 18px;
            bottom: 28px;
            width: 108px;
            height: 108px;
            border-radius: 999px;
            background:
                radial-gradient(circle at 50% 50%, #ffffff 0 6px, transparent 7px),
                conic-gradient(from 30deg, #8b5cf6, #4f46e5, #8b5cf6);
            border: 10px solid #7668ff;
            box-shadow: 0 20px 40px rgba(79, 70, 229, 0.26);
        }

        .planning-card {
            min-height: 148px;
            display: flex;
            align-items: center;
            gap: 26px;
            border: 1px solid #dbe3f2;
            border-left: 7px solid #7c3aed;
            border-radius: 8px;
            background:
                radial-gradient(circle at 96% 18%, rgba(124, 58, 237, 0.06), transparent 28%),
                #ffffff;
            box-shadow: 0 20px 48px rgba(15, 23, 42, 0.08);
            padding: 30px 34px;
            margin: 24px 0;
            transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease;
        }

        .planning-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 26px 60px rgba(15, 23, 42, 0.12);
            border-color: #c7d2fe;
        }

        .planning-card-icon {
            width: 76px;
            height: 76px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #eef2ff, #ffffff);
            color: #6d5dfc !important;
            border: 1px solid #d8ddff;
            box-shadow: inset 0 0 0 1px rgba(109, 93, 252, 0.08);
            font-size: 30px;
            font-weight: 950;
            flex: 0 0 auto;
        }

        .planning-card h3 {
            color: #0f1f44 !important;
            font-size: 27px;
            font-weight: 950;
            margin: 0 0 18px 0;
        }

        .planning-date {
            color: #64748b !important;
            font-size: 17px;
            font-weight: 850;
        }

        .planning-date strong {
            color: #475569 !important;
            font-weight: 950;
        }

        .planning-empty {
            border: 1px dashed #c7d2fe;
            background: #ffffff;
            border-radius: 8px;
            padding: 28px;
            color: #64748b !important;
            font-weight: 850;
            box-shadow: 0 16px 38px rgba(15, 23, 42, 0.06);
        }

        /* Global blue-violet application polish */
        h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #0f1f44 !important;
            font-weight: 950 !important;
            letter-spacing: 0 !important;
        }

        div[data-testid="stExpander"],
        div[data-testid="stForm"],
        div[data-testid="stAlert"] {
            border-radius: 8px !important;
        }

        .card,
        .course-row,
        .homework-card,
        .message {
            background:
                radial-gradient(circle at 96% 6%, rgba(99, 102, 241, 0.08), transparent 20%),
                #ffffff !important;
            border: 1px solid #e5eaf6 !important;
            border-radius: 8px !important;
            box-shadow: 0 18px 44px rgba(15, 23, 42, 0.08) !important;
        }

        .card {
            border-top: 4px solid #6366f1 !important;
        }

        .course-row {
            border-left: 5px solid #2563eb !important;
        }

        .homework-card {
            border-left: 5px solid #7c3aed !important;
        }

        .message {
            border-left: 5px solid #0ea5e9 !important;
        }

        .message-important {
            border-left-color: #ef4444 !important;
            background: linear-gradient(135deg, #fff7f7, #ffffff) !important;
        }

        .badge {
            background: #eef2ff !important;
            color: #3730a3 !important;
            border-color: #c7d2fe !important;
            font-weight: 950 !important;
        }

        .badge-new {
            background: #fffbeb !important;
            color: #b45309 !important;
            border-color: #fde68a !important;
        }

        .badge-important {
            background: #fee2e2 !important;
            color: #991b1b !important;
            border-color: #fecaca !important;
        }

        div[data-testid="stButton"] > button,
        div[data-testid="stLinkButton"] > a,
        div[data-testid="stDownloadButton"] > button {
            border-radius: 8px !important;
            font-weight: 950 !important;
        }

        div[data-testid="stLinkButton"] > a {
            background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
            border-color: transparent !important;
            color: #ffffff !important;
            box-shadow: 0 14px 30px rgba(79, 70, 229, 0.22) !important;
        }

        div[data-testid="stLinkButton"] > a * {
            color: #ffffff !important;
        }

        div[data-baseweb="tab-list"] {
            gap: 8px;
        }

        div[data-baseweb="tab"] {
            border-radius: 8px !important;
            background: #ffffff !important;
            border: 1px solid #e5eaf6 !important;
            color: #172554 !important;
            font-weight: 950 !important;
            padding: 8px 14px !important;
        }

        div[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
            color: #ffffff !important;
        }

        .login-topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid #e5eaf6;
            border-radius: 8px;
            padding: 18px 24px;
            margin-bottom: 46px;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
        }

        .login-brand {
            color: #0f1f44 !important;
            font-size: 28px;
            font-weight: 950;
        }

        .login-brand span {
            color: #2563eb !important;
        }

        .login-user {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #334155 !important;
            font-weight: 900;
        }

        .login-avatar {
            width: 46px;
            height: 46px;
            border-radius: 999px;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            box-shadow: 0 12px 28px rgba(79, 70, 229, 0.24);
        }

        .login-intro {
            background: #ffffff;
            border: 1px solid #e5eaf6;
            border-radius: 8px;
            padding: 34px;
            min-height: 520px;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.10);
        }

        .login-icon {
            width: 74px;
            height: 74px;
            border-radius: 999px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #2563eb !important;
            background: #eef2ff;
            font-size: 34px;
            font-weight: 950;
            margin-bottom: 22px;
            box-shadow: inset 0 0 0 1px #dbe4ff;
        }

        .login-intro h1 {
            color: #0f1f44 !important;
            font-size: 34px;
            font-weight: 950;
            margin: 0 0 8px 0;
        }

        .login-intro p {
            color: #64748b !important;
            font-size: 16px;
            font-weight: 750;
            margin: 0 0 34px 0;
        }

        .login-line {
            width: 56px;
            height: 4px;
            border-radius: 999px;
            background: linear-gradient(90deg, #2563eb, #7c3aed);
            margin-bottom: 28px;
        }

        .login-visual {
            min-height: 520px;
            border-radius: 8px;
            border: 1px solid #e5eaf6;
            background:
                radial-gradient(circle at 38% 28%, rgba(99, 102, 241, 0.18), transparent 24%),
                radial-gradient(circle at 68% 64%, rgba(37, 99, 235, 0.18), transparent 28%),
                linear-gradient(135deg, #f8fbff, #eef2ff);
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
            position: relative;
            overflow: hidden;
        }

        .login-visual::before {
            content: "";
            position: absolute;
            width: 260px;
            height: 170px;
            left: 50%;
            top: 47%;
            transform: translate(-50%, -50%) rotate(4deg);
            border-radius: 8px;
            background: #ffffff;
            border: 12px solid #3346b8;
            box-shadow: 0 28px 70px rgba(37, 99, 235, 0.22);
        }

        .login-visual::after {
            content: "";
            position: absolute;
            width: 120px;
            height: 120px;
            left: 36%;
            top: 55%;
            transform: translate(-50%, -50%);
            border-radius: 30px;
            background:
                radial-gradient(circle at 50% 34%, #ffffff 0 18px, transparent 19px),
                radial-gradient(circle at 50% 82%, #ffffff 0 32px, transparent 33px),
                linear-gradient(135deg, #2563eb, #7c3aed);
            box-shadow: 0 20px 50px rgba(79, 70, 229, 0.26);
        }

        .login-visual-card {
            position: absolute;
            right: 82px;
            top: 142px;
            width: 92px;
            height: 92px;
            border-radius: 8px;
            background: linear-gradient(135deg, #2563eb, #60a5fa);
            box-shadow: 0 18px 44px rgba(37, 99, 235, 0.26);
        }

        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.96) !important;
            border: 1px solid #e5eaf6 !important;
            box-shadow: 0 18px 44px rgba(15, 23, 42, 0.08) !important;
        }

        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
            border-color: transparent !important;
            color: #ffffff !important;
            min-height: 50px !important;
            font-weight: 950 !important;
            box-shadow: 0 18px 36px rgba(79, 70, 229, 0.26) !important;
        }

        div[data-testid="stFormSubmitButton"] button * {
            color: #ffffff !important;
            font-weight: 950 !important;
        }

        /* Final platform polish */
        .main .block-container {
            max-width: 1280px;
        }

        .stApp {
            background:
                radial-gradient(circle at 2% 8%, rgba(99, 102, 241, 0.08), transparent 22%),
                radial-gradient(circle at 96% 4%, rgba(14, 165, 233, 0.08), transparent 22%),
                #f6f8ff !important;
        }

        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3,
        div[data-testid="stHeading"] h1,
        div[data-testid="stHeading"] h2,
        div[data-testid="stHeading"] h3 {
            color: #0b173d !important;
            font-weight: 950 !important;
        }

        .stMarkdown p,
        .stMarkdown li,
        label,
        .muted,
        .message-meta,
        .homework-meta {
            color: #536179 !important;
            font-weight: 750;
        }

        div[data-testid="stForm"] {
            padding: 22px !important;
            border-radius: 8px !important;
            border: 1.5px solid #d5def2 !important;
            background:
                radial-gradient(circle at 96% 0%, rgba(99, 102, 241, 0.06), transparent 24%),
                #ffffff !important;
            box-shadow: 0 16px 38px rgba(15, 23, 42, 0.06) !important;
        }

        div[data-testid="stTextInput"],
        div[data-testid="stTextArea"],
        div[data-testid="stNumberInput"],
        div[data-testid="stDateInput"],
        div[data-testid="stTimeInput"],
        div[data-testid="stSelectbox"],
        div[data-testid="stMultiSelect"] {
            padding: 2px 0 8px 0 !important;
        }

        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea,
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] input {
            background: #fbfcff !important;
            border-color: #b8c4df !important;
            color: #111827 !important;
            font-weight: 800 !important;
        }

        div[data-baseweb="input"],
        div[data-baseweb="textarea"],
        div[data-baseweb="select"] > div {
            border: 1.7px solid #b8c4df !important;
            border-radius: 8px !important;
            background: #fbfcff !important;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.045) !important;
            transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease !important;
        }

        div[data-baseweb="input"]:hover,
        div[data-baseweb="textarea"]:hover,
        div[data-baseweb="select"] > div:hover {
            border-color: #7c8cf8 !important;
            box-shadow: 0 14px 30px rgba(79, 70, 229, 0.10) !important;
        }

        div[data-baseweb="input"]:focus-within input,
        div[data-baseweb="textarea"]:focus-within textarea,
        div[data-baseweb="select"]:focus-within > div {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12) !important;
        }

        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="textarea"]:focus-within,
        div[data-baseweb="select"]:focus-within > div {
            border-color: #4f46e5 !important;
            box-shadow:
                0 0 0 4px rgba(99, 102, 241, 0.14),
                0 16px 34px rgba(79, 70, 229, 0.12) !important;
        }

        div[data-testid="stButton"] > button {
            transition: transform 140ms ease, box-shadow 140ms ease, background 140ms ease !important;
        }

        div[data-testid="stButton"] > button:hover,
        div[data-testid="stLinkButton"] > a:hover,
        div[data-testid="stDownloadButton"] > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 18px 36px rgba(79, 70, 229, 0.20) !important;
        }

        div[data-testid="stAlert"] {
            border: 1px solid #dce3f4 !important;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06) !important;
        }

        div[data-testid="stAlert"] * {
            font-weight: 800 !important;
        }

        .card,
        .message,
        .homework-card,
        .course-row,
        .subject-card,
        .login-intro,
        .login-visual,
        .contact-form-title,
        .contact-help {
            transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease;
        }

        .card:hover,
        .message:hover,
        .homework-card:hover,
        .course-row:hover {
            transform: translateY(-3px);
            box-shadow: 0 24px 56px rgba(15, 23, 42, 0.12) !important;
            border-color: #c7d2fe !important;
        }

        .message-title,
        .card h3,
        .course-row h3,
        .homework-card h3 {
            color: #0f1f44 !important;
            font-weight: 950 !important;
        }

        .message-content,
        .card p,
        .course-row p {
            color: #1f2937 !important;
            font-weight: 700;
        }

        div[data-testid="stFileUploader"] {
            background: #ffffff;
            border: 1.8px dashed #8b95ff !important;
            border-radius: 8px;
            padding: 12px;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05) !important;
        }

        div[data-testid="stFileUploader"] * {
            color: #334155 !important;
            font-weight: 800 !important;
        }

        div[data-testid="stRadio"] label {
            color: #111827 !important;
            font-weight: 900 !important;
        }

        div[role="radiogroup"] label {
            border-radius: 8px !important;
            border: 1px solid #dce3f4 !important;
            background: #ffffff !important;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.05);
        }

        div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            border-color: #6366f1 !important;
        }

        .creator-footer {
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid #e5eaf6;
            border-radius: 8px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
        }

        @media (max-width: 900px) {
            .app-topbar,
            .contact-topbar,
            .login-topbar {
                flex-direction: column;
                align-items: flex-start;
            }

            .dashboard-hero {
                padding: 30px 24px;
            }

            .dashboard-hero::after,
            .contact-art,
            .courses-hero-art {
                display: none;
            }

            .contact-hero,
            .courses-hero {
                align-items: flex-start;
            }
        }

        /* Comfortable reading and spacing pass */
        .main .block-container {
            padding-top: 2rem !important;
            padding-left: 2.4rem !important;
            padding-right: 2.4rem !important;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0.95rem;
        }

        .stMarkdown p,
        .stMarkdown li,
        .message-content,
        .card p,
        .course-row p,
        .contact-help,
        .homework-meta,
        .muted {
            line-height: 1.65 !important;
        }

        .card,
        .course-row,
        .homework-card,
        .message {
            padding: 22px 24px !important;
            margin-bottom: 18px !important;
        }

        .subject-card {
            padding: 24px 22px 20px 22px !important;
            margin-bottom: 18px !important;
        }

        .dashboard-stat-grid {
            margin: 10px 0 32px 0 !important;
        }

        .dashboard-stat {
            min-height: 146px !important;
            padding: 24px !important;
        }

        .dashboard-hero,
        .courses-hero,
        .contact-hero {
            margin-bottom: 30px !important;
        }

        .app-topbar,
        .contact-topbar,
        .login-topbar {
            margin-bottom: 28px !important;
        }

        .login-intro,
        .login-visual {
            min-height: 500px !important;
        }

        div[data-baseweb="input"] input,
        div[data-baseweb="select"] > div {
            min-height: 48px !important;
        }

        div[data-baseweb="textarea"] textarea {
            min-height: 132px !important;
        }

        div[data-testid="stForm"] {
            padding: 28px !important;
        }

        div[data-testid="stButton"] > button,
        div[data-testid="stLinkButton"] > a,
        div[data-testid="stDownloadButton"] > button,
        div[data-testid="stFormSubmitButton"] button {
            min-height: 46px !important;
        }

        hr {
            margin: 1.8rem 0 !important;
            border-color: #e5eaf6 !important;
        }

        div[data-testid="stTabs"] {
            margin-top: 8px;
        }

        div[data-baseweb="tab-list"] {
            margin-bottom: 18px;
        }

        div[data-testid="column"] {
            padding: 0 0.35rem;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
            margin-bottom: 11px !important;
        }

        section[data-testid="stSidebar"] {
            box-shadow: 16px 0 42px rgba(15, 23, 42, 0.10);
        }

        @media (max-width: 760px) {
            .main .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-top: 1rem !important;
            }

            .dashboard-hero h1,
            .welcome-copy h1 {
                font-size: 34px !important;
            }

            .contact-title-wrap {
                align-items: flex-start;
                flex-direction: column;
            }

            .subject-card {
                grid-template-columns: 1fr !important;
            }

            .planning-shell {
                padding: 20px !important;
                margin: 0 0 18px 0 !important;
                overflow: visible !important;
            }

            .planning-hero {
                display: block !important;
                min-height: auto !important;
            }

            .planning-title-wrap {
                display: block !important;
                width: 100% !important;
            }

            .planning-icon-main {
                width: 64px !important;
                height: 64px !important;
                font-size: 26px !important;
                margin-bottom: 16px !important;
            }

            .planning-hero h1 {
                font-size: 30px !important;
                line-height: 1.15 !important;
                margin: 0 0 14px 0 !important;
                word-break: normal !important;
                overflow-wrap: normal !important;
                hyphens: none !important;
            }

            .planning-hero p,
            .planning-hero strong {
                font-size: 15px !important;
                line-height: 1.55 !important;
                word-break: normal !important;
                overflow-wrap: normal !important;
            }

            .planning-art {
                display: none !important;
            }

            .planning-card {
                align-items: flex-start !important;
                gap: 14px !important;
                padding: 20px !important;
                min-height: auto !important;
            }

            .planning-card-icon {
                width: 54px !important;
                height: 54px !important;
                font-size: 22px !important;
            }

            .planning-card h3 {
                font-size: 21px !important;
                line-height: 1.25 !important;
                margin-bottom: 12px !important;
            }

            .planning-date {
                font-size: 15px !important;
                line-height: 1.45 !important;
            }

            div[data-testid="column"] {
                padding: 0 !important;
            }
        }

        .subject-icon,
        .dashboard-stat .stat-icon,
        .contact-icon,
        .login-icon,
        .welcome-brand-mark {
            animation: iconPopIn 420ms ease-out both, iconPulse3d 4.8s ease-in-out infinite;
            transform-origin: center;
        }

        .subject-card:nth-of-type(2n) .subject-icon,
        .dashboard-stat:nth-child(2n) .stat-icon {
            animation-delay: 90ms, 680ms;
        }

        .subject-card:nth-of-type(3n) .subject-icon,
        .dashboard-stat:nth-child(3n) .stat-icon {
            animation-delay: 150ms, 1180ms;
        }

        .subject-icon,
        .dashboard-stat .stat-icon,
        .contact-icon,
        .login-icon {
            animation-name: iconPopIn, iconPulse3d, iconGlowRing;
            animation-duration: 420ms, 4.8s, 4.8s;
            animation-timing-function: ease-out, ease-in-out, ease-in-out;
            animation-iteration-count: 1, infinite, infinite;
        }

        .subject-card:hover .subject-icon,
        .dashboard-stat:hover .stat-icon,
        .contact-title-wrap:hover .contact-icon,
        .login-intro:hover .login-icon {
            transform: translateY(-7px) scale(1.10) rotateZ(-4deg);
        }

        .page-transition {
            animation: pageTransitionIn 520ms cubic-bezier(0.16, 1, 0.3, 1) both;
            transform-origin: top center;
        }

        .page-transition > div,
        .page-transition .stMarkdown,
        .page-transition div[data-testid="stForm"],
        .page-transition div[data-testid="stExpander"],
        .page-transition div[data-testid="stAlert"] {
            animation: contentCascadeIn 440ms cubic-bezier(0.2, 0.8, 0.2, 1) both;
        }

        .page-transition > div:nth-child(2) {
            animation-delay: 45ms;
        }

        .page-transition > div:nth-child(3) {
            animation-delay: 90ms;
        }

        .page-transition > div:nth-child(4) {
            animation-delay: 135ms;
        }

        .dashboard-hero,
        .courses-hero,
        .contact-hero,
        .files-hero,
        .exam-page-shell,
        .planning-shell,
        .platform-login-shell,
        .welcome-shell,
        .app-topbar,
        .login-topbar,
        .contact-topbar {
            position: relative;
            overflow: hidden;
        }

        .dashboard-hero::before,
        .courses-hero::before,
        .contact-hero::before,
        .files-hero::before,
        .exam-page-shell::before,
        .planning-shell::before,
        .app-topbar::before,
        .login-topbar::before,
        .contact-topbar::before {
            content: "";
            position: absolute;
            top: -35%;
            bottom: -35%;
            left: -42%;
            width: 36%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.38), transparent);
            pointer-events: none;
            animation: softShimmer 1.15s ease-out 220ms both;
        }

        .dashboard-stat,
        .subject-card,
        .card,
        .message,
        .homework-card,
        .planning-card,
        .exam-card,
        .shared-file-card {
            transform: translateZ(0);
            will-change: transform, box-shadow;
        }

        .dashboard-stat:hover,
        .subject-card:hover,
        .planning-card:hover,
        .exam-card:hover,
        .shared-file-card:hover,
        .card:hover,
        .message:hover,
        .homework-card:hover {
            transform: translateY(-5px) scale(1.006);
            box-shadow: 0 30px 70px rgba(15, 23, 42, 0.13) !important;
        }

        div[data-testid="stButton"] > button:active,
        div[data-testid="stLinkButton"] > a:active,
        div[data-testid="stDownloadButton"] > button:active,
        div[data-testid="stFormSubmitButton"] button:active {
            transform: translateY(1px) scale(0.985) !important;
        }

        .chat-user,
        .chat-assistant {
            width: fit-content;
            max-width: min(760px, 100%);
            margin: 10px 0;
            padding: 14px 16px;
            border-radius: 18px;
            line-height: 1.6;
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
        }

        .chat-user {
            margin-left: auto;
            color: #ffffff;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
        }

        .chat-assistant {
            color: #0f172a;
            background: #ffffff;
            border: 1px solid rgba(99, 102, 241, 0.18);
        }

        @media (prefers-reduced-motion: reduce) {
            .subject-icon,
            .dashboard-stat .stat-icon,
            .contact-icon,
            .login-icon,
            .welcome-brand-mark,
            .welcome-orbit,
            .welcome-mini-card,
            .welcome-visual,
            .page-transition {
                animation: none !important;
            }

            .dashboard-hero::before,
            .courses-hero::before,
            .contact-hero::before,
            .files-hero::before,
            .exam-page-shell::before,
            .planning-shell::before,
            .app-topbar::before,
            .login-topbar::before,
            .contact-topbar::before {
                display: none !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_header(data=None):
    user_label = st.session_state.get("platform_user_label", "Etudiant")
    st.markdown(
        f"""
        <div class="app-topbar">
            <div class="app-brand">BTS <span>SMART</span>CAMPUS</div>
            <div class="app-user">
                <span>Bonjour, {user_label}</span>
                <span class="app-user-avatar"></span>
            </div>
        </div>
        <div class="dashboard-hero">
            <h1>Bienvenue sur<br>BTS <span>SMARTCAMPUS</span></h1>
            <p>
                Plateforme pour centraliser les cours, les fiches Drive, les examens
                nationaux precedents et les messages destines aux etudiants.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_creator_footer():
    st.markdown(
        """
        <div class="creator-footer">
            Plateforme creee par <strong>Ayman Marzagui</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_topbar(role_label):
    st.markdown(
        f"""
        <div class="login-topbar">
            <div class="login-brand">BTS <span>SMART</span>CAMPUS</div>
            <div class="login-user">
                <span>Bonjour,<br><strong>{role_label}</strong></span>
                <span class="login-avatar"></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_intro(title, subtitle, icon):
    st.markdown(
        f"""
        <div class="login-intro">
            <div class="login-icon">{icon}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
            <div class="login-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_visual():
    st.markdown(
        """
        <div class="login-visual">
            <div class="login-visual-card"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def validate_platform_login(email, password, data):
    clean_email = email.strip().lower()
    clean_password = password.strip()

    if clean_email == STUDENT_EMAIL.lower() and verify_password(clean_password, STUDENT_PASSWORD):
        return {"label": "Etudiant", "role": "student", "email": clean_email}

    if clean_email == GUEST_EMAIL.lower() and verify_password(clean_password, GUEST_PASSWORD):
        return {"label": "Invite", "role": "guest", "email": clean_email}

    student_account = data.get("student_accounts", {}).get(clean_email)
    if student_account and verify_password(clean_password, student_account.get("password")):
        full_name = f"{student_account.get('prenom', '').strip()} {student_account.get('nom', '').strip()}".strip()
        label = full_name or "Etudiant"
        if student_account.get("banned"):
            return {
                "label": label,
                "role": "student",
                "email": clean_email,
                "blocked": True,
                "reason": "banned",
            }
        if student_account.get("status") != "approved":
            return {
                "label": label,
                "role": "student",
                "email": clean_email,
                "blocked": True,
                "status": student_account.get("status", "pending"),
            }
        return {"label": label, "role": "student", "email": clean_email}

    if clean_email == DIRECTION_EMAIL.lower() and verify_password(clean_password, DIRECTION_PASSWORD):
        return {"label": "Direction", "role": "direction", "email": clean_email}

    accounts = data.get("prof_accounts", PROF_ACCOUNTS)
    account = accounts.get(clean_email)
    if account and verify_password(clean_password, account.get("password")):
        if account.get("banned"):
            return {
                "label": account.get("name", "Professeur"),
                "role": account.get("role", "prof"),
                "email": clean_email,
                "blocked": True,
                "reason": "banned",
            }
        return {
            "label": account.get("name", "Professeur"),
            "role": account.get("role", "prof"),
            "email": clean_email,
        }

    return None


def register_student_account(data, first_name, last_name, email, group, password, confirm_password):
    clean_email = email.strip().lower()
    clean_first_name = first_name.strip()
    clean_last_name = last_name.strip()
    clean_group = group.strip()
    clean_password = password.strip()
    clean_confirm = confirm_password.strip()

    if not clean_first_name or not clean_last_name or not clean_email or not clean_password:
        return False, "Le prenom, le nom, l'email et le mot de passe sont obligatoires."
    if "@" not in clean_email or "." not in clean_email:
        return False, "Email invalide."
    if len(clean_password) < 6:
        return False, "Le mot de passe doit contenir au moins 6 caracteres."
    if clean_password != clean_confirm:
        return False, "Les deux mots de passe ne sont pas identiques."
    if clean_email in data.get("student_accounts", {}):
        return False, "Un compte etudiant existe deja avec cet email."
    if clean_email in data.get("prof_accounts", {}) or clean_email in (DIRECTION_EMAIL.lower(), ADMIN_EMAIL.lower()):
        return False, "Cet email est reserve a l'administration."

    data.setdefault("student_accounts", {})[clean_email] = {
        "prenom": clean_first_name,
        "nom": clean_last_name,
        "groupe": clean_group,
        "password": hash_password(clean_password),
        "status": "pending",
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "validated_at": "",
    }
    save_data(data)
    return True, "Votre demande est envoyee. La direction doit valider votre compte."


def show_platform_login(data):
    st.markdown(
        """
        <div class="platform-login-shell">
            <div class="platform-login-top">
                <div class="platform-login-brand">BTS <span>SMART</span>CAMPUS</div>
                <div class="platform-login-pill">Acces securise a la plateforme</div>
            </div>
            <div class="platform-login-hero">
                <div class="platform-login-copy">
                    <h1>Connectez-vous a<br><span>BTS SMARTCAMPUS</span></h1>
                    <p>
                        Accedez a vos cours, examens, fichiers partages, messages et planning
                        depuis un espace moderne pense pour accompagner votre reussite.
                    </p>
                </div>
                <div class="platform-login-card">
                    <div class="platform-login-card-title">Connexion</div>
                    <div class="platform-login-card-subtitle">Entrez vos identifiants pour continuer.</div>
        """,
        unsafe_allow_html=True,
    )

    submitted = False
    signup_submitted = False
    login_tab, signup_tab = st.tabs(["Connexion", "Inscription etudiant"])

    with login_tab:
        with st.form("platform_login_form"):
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Acceder a la plateforme")

    with signup_tab:
        with st.form("student_signup_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            first_name = col1.text_input("Prenom")
            last_name = col2.text_input("Nom")
            signup_email = st.text_input("Email personnel")
            group = st.text_input("Classe ou groupe")
            signup_password = st.text_input("Mot de passe", type="password")
            confirm_password = st.text_input("Confirmer le mot de passe", type="password")
            signup_submitted = st.form_submit_button("Envoyer la demande")

    st.markdown(
        """
                    <div class="platform-login-note">
                        <span>i</span>
                        <span>Les nouveaux comptes etudiants doivent etre valides par la direction.</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    show_creator_footer()

    if signup_submitted:
        success, message = register_student_account(
            data,
            first_name,
            last_name,
            signup_email,
            group,
            signup_password,
            confirm_password,
        )
        if success:
            st.success(message)
        else:
            st.error(message)

    if submitted:
        auth = validate_platform_login(email, password, data)
        if auth and auth.get("blocked"):
            if auth.get("reason") == "banned":
                st.error("Votre compte est bloque par l'administration.")
            else:
                st.warning("Votre compte est encore en attente de validation par la direction.")
        elif auth:
            st.session_state.platform_logged_in = True
            st.session_state.platform_user_label = auth.get("label", "Etudiant")
            st.session_state.platform_user_email = auth.get("email", "")
            st.session_state.platform_user_role = auth.get("role", "student")
            st.session_state.login_transition = True
            st.success("Connexion reussie.")
            st.rerun()
        else:
            st.error("Email ou mot de passe incorrect.")


def show_welcome():
    st.markdown(
        """
        <div class="welcome-shell">
            <div class="welcome-topbar">
                <div class="welcome-brand">
                    <span class="welcome-brand-mark"></span>
                    <span class="welcome-brand-text">
                        <span class="welcome-brand-main">BTS <span>SMART</span></span>
                        <span class="welcome-brand-sub">CAMPUS</span>
                    </span>
                </div>
            </div>
            <div class="welcome-hero">
                <div class="welcome-orbit orbit-one">PDF</div>
                <div class="welcome-orbit orbit-two">+</div>
                <div class="welcome-orbit orbit-three">BTS</div>
                <div class="welcome-copy">
                    <h1>Bienvenue sur<br>BTS <span>SMARTCAMPUS</span></h1>
                    <p>
                        Est une plateforme dediee aux etudiants souhaitant reviser efficacement.
                        Vous y trouverez tous les cours, exercices corriges et examens des annees
                        precedentes, organises et accessibles en un seul endroit. Un espace simple,
                        moderne et complet pour accompagner votre reussite tout au long de l'annee.
                    </p>
                    <div class="welcome-feature-row">
                        <span class="welcome-feature"><b>▣</b>Cours de qualite</span>
                        <span class="welcome-feature"><b>◌</b>Ressources Drive</span>
                        <span class="welcome-feature"><b>☆</b>Examens precedents</span>
                    </div>
                </div>
                <div class="welcome-visual">
                    <div class="welcome-mini-card mini-cours">
                        <strong>12+</strong>
                        <span>Matieres organisees</span>
                    </div>
                    <div class="welcome-mini-card mini-examens">
                        <strong>PDF</strong>
                        <span>Cours et fiches Drive</span>
                    </div>
                    <div class="welcome-mini-card mini-drive">
                        <strong>Exam</strong>
                        <span>Preparation nationale</span>
                    </div>
                    <div class="welcome-mini-card mini-profs">
                        <strong>Prof</strong>
                        <span>Messages et partage</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="welcome-actions">', unsafe_allow_html=True)
    if st.button("Commencer maintenant", width="stretch"):
        st.session_state.platform_started = True
        st.session_state.entry_animation = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="welcome-tags-outside">
            <span class="welcome-tag tag-academy">Smart Campus</span>
            <span class="welcome-tag tag-ressources">Ressources</span>
            <span class="welcome-tag tag-examens">Examens</span>
            <span class="welcome-tag tag-direction">Direction</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    show_creator_footer()


def show_entry_transition():
    st.markdown(
        """
        <div class="entry-transition">
            <div class="entry-transition-content">
                <h2>BTS SMARTCAMPUS</h2>
                <p>Chargement de votre espace de travail...</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.entry_animation = False


def show_login_to_welcome_transition():
    st.markdown(
        """
        <div class="login-gateway-transition">
            <div class="login-gateway-card">
                <div class="login-gateway-mark">SC</div>
                <h2>BTS <span>SMART</span>CAMPUS</h2>
                <p>Connexion reussie. Preparation de votre espace...</p>
                <div class="login-gateway-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.login_transition = False


def show_resource_card(resource, extra=""):
    badges = [
        f'<span class="badge">{resource.get("type", "Cours")}</span>',
        f'<span class="badge">{resource.get("statut", "Disponible")}</span>',
    ]
    if is_new(resource.get("date")):
        badges.append('<span class="badge badge-new">Nouveau</span>')

    st.markdown(
        f"""
        <div class="card">
            <h3>{resource.get("titre", "Ressource")}</h3>
            <div>{''.join(badges)}</div>
            <div class="muted">{extra}</div>
            <p>{resource.get("description", "")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button("Ouvrir le lien Drive", resource.get("url", "https://drive.google.com/"))


def show_home(data):
    show_header(data)
    current_email = st.session_state.get("platform_user_email", "")
    student_account = data.get("student_accounts", {}).get(current_email)
    if student_account:
        admin_messages = student_account.get("admin_messages", [])
        if admin_messages:
            st.subheader("Messages de l'administration")
            for message in sorted(admin_messages, key=lambda item: parse_date(item.get("date")), reverse=True)[:3]:
                st.markdown(
                    f"""
                    <div class="message message-important">
                        <div class="message-title">{message.get("titre", "Message administration")}</div>
                        <div class="message-meta">Admin | Date: {message.get("date", "Date non indiquee")}</div>
                        <div class="message-content">{message.get("contenu", "")}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    total_courses = sum(len(resources) for resources in data["cours"].values())
    dashboard_updates = unread_updates(data, limit=4)
    new_courses = len(dashboard_updates)
    total_files = len(data.get("shared_files", []))
    total_exams = len(data.get("examens", []))
    st.markdown(
        f"""
        <div class="dashboard-stat-grid">
            <div class="dashboard-stat stat-blue">
                <div class="stat-icon">M</div>
                <div class="label">Matieres</div>
                <div class="value">{len(SUBJECTS)}</div>
                <div class="hint">Toutes les matieres</div>
            </div>
            <div class="dashboard-stat stat-teal">
                <div class="stat-icon">C</div>
                <div class="label">Cours disponibles</div>
                <div class="value">{total_courses}</div>
                <div class="hint">Cours a votre disposition</div>
            </div>
            <div class="dashboard-stat stat-amber">
                <div class="stat-icon">N</div>
                <div class="label">Nouveautes</div>
                <div class="value">{new_courses}</div>
                <div class="hint">Non lues</div>
            </div>
            <div class="dashboard-stat stat-violet">
                <div class="stat-icon">F</div>
                <div class="label">Fichiers & examens</div>
                <div class="value">{total_files + total_exams}</div>
                <div class="hint">Fichiers disponibles</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Historique des nouveautes", key="open_updates_history_from_dashboard", width="stretch"):
        st.session_state.current_page = "Historique des nouveautes"
        st.rerun()

    planned_exams = [
        devoir
        for devoir in data.get("devoirs", [])
        if devoir.get("date_limite") and not is_weekend_date(devoir.get("date_limite"))
    ]
    planned_exams = sorted(
        planned_exams,
        key=lambda devoir: parse_deadline(devoir.get("date_limite")),
    )[:6]

    recent_files = sorted(
        data.get("shared_files", []),
        key=lambda shared_file: parse_date(shared_file.get("date")),
        reverse=True,
    )[:4]

    dash_left, dash_right = st.columns(2)
    with dash_left:
        st.subheader("Planification des examens")
        if not planned_exams:
            st.info("Aucun examen planifie pour le moment.")
        else:
            for devoir in planned_exams:
                exam_date = devoir.get("date_limite", "")
                st.markdown(
                    f"""
                    <div class="homework-card">
                        <h3>{devoir.get("matiere", "General")}</h3>
                        <div class="homework-meta">
                            Date d'examen: {exam_date or "Non indiquee"}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with dash_right:
        st.subheader("Fichiers partages recents")
        if not recent_files:
            st.info("Aucun fichier partage pour le moment.")
        else:
            for shared_file in recent_files:
                render_shared_file(shared_file)

    updates_left, messages_right = st.columns([1, 1])
    with updates_left:
        st.subheader("Nouveautes non lues")
        if not dashboard_updates:
            st.info("Aucune nouvelle nouveaute. Consultez l'historique pour revoir les anciennes publications.")
        for item in dashboard_updates:
            extra = f"{item.get('matiere')} | {item.get('type')} | {item.get('statut')} | {item.get('date')}"
            show_resource_card(item, extra=extra)
        mark_updates_seen(data, dashboard_updates)

    with messages_right:
        st.subheader("Messages aux etudiants")
        if not data["messages"]:
            st.info("Aucun message pour le moment.")

        messages = sorted(
            data["messages"],
            key=lambda message: (message.get("important", False), parse_date(message.get("date"))),
            reverse=True,
        )

        for message in messages[:5]:
            subject_label = message.get("matiere", "General")
            prof_label = message.get("prof", "Administration")
            is_direction_message = "direction" in prof_label.lower()
            author_label = (
                "Message officiel de la direction"
                if is_direction_message
                else f"Prof: {prof_label}"
            )
            date_label = message.get("date", "Date non indiquee")
            important_class = " message-important" if message.get("important") else ""
            important_badge = (
                '<span class="badge badge-important">Important</span>' if message.get("important") else ""
            )
            direction_badge = (
                '<span class="badge badge-important">Direction</span>' if is_direction_message else ""
            )
            st.markdown(
                f"""
                <div class="message{important_class}">
                    <div class="message-title">{direction_badge}{important_badge}{message["titre"]}</div>
                    <div class="message-meta">
                        {author_label} | Matiere: {subject_label} | Date: {date_label}
                    </div>
                    <div class="message-content">{message["contenu"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def show_courses(data):
    if "selected_course_subject" not in st.session_state:
        st.session_state.selected_course_subject = None

    if st.session_state.selected_course_subject is None:
        st.markdown(
            """
            <div class="courses-hero">
                <div>
                    <h1>Cours</h1>
                    <p>Choisissez une matiere pour afficher la liste des cours disponibles.</p>
                </div>
                <div class="courses-hero-art"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        columns = st.columns(3)
        for index, subject in enumerate(SUBJECTS):
            resources_count = len(data["cours"].get(subject, []))
            theme = subject_theme(subject)
            with columns[index % 3]:
                st.markdown(
                    f"""
                    <div class="subject-card" style="--subject-color:{theme['color']}; --subject-soft:{theme['soft']};">
                        <div class="subject-icon">{theme['icon']}</div>
                        <div>
                            <strong>{subject}</strong>
                            <div class="subject-count">{resources_count} cours disponible(s)</div>
                            <div class="subject-action">Acceder aux ressources</div>
                            <div class="subject-label">{theme['label']}</div>
                        </div>
                        <div class="subject-card-button-space"></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Ouvrir cette matiere ->", key=f"open_subject_{subject}", width="stretch"):
                    st.session_state.selected_course_subject = subject
                    st.rerun()
        return

    subject = st.session_state.selected_course_subject
    if st.button("Retour aux matieres"):
        st.session_state.selected_course_subject = None
        st.rerun()

    st.subheader(subject)
    st.write("Cliquez sur un cours pour ouvrir directement son fichier PDF ou son dossier Drive.")

    resources = data["cours"].get(subject, [])
    resource_type = st.selectbox(
        "Filtrer par type",
        ["Tous"] + RESOURCE_TYPES,
        key=f"type_filter_{subject}",
    )
    status = st.selectbox(
        "Filtrer par statut",
        ["Tous"] + COURSE_STATUS,
        key=f"status_filter_{subject}",
    )
    resources = [
        resource
        for resource in resources
        if (resource_type == "Tous" or resource.get("type") == resource_type)
        and (status == "Tous" or resource.get("statut") == status)
    ]
    if not resources:
        st.info("Aucun cours publie pour cette matiere.")
        return

    for resource in resources:
        badges = [
            f'<span class="badge">{resource.get("type", "Cours")}</span>',
            f'<span class="badge">{resource.get("statut", "Disponible")}</span>',
        ]
        if is_new(resource.get("date")):
            badges.append('<span class="badge badge-new">Nouveau</span>')
        st.markdown(
            f"""
            <div class="course-row">
                <h3>{resource.get("titre", "Cours")}</h3>
                <div>{''.join(badges)}</div>
                <div class="muted">Ajoute par {resource.get("prof", "Administration")} | {resource.get("date", "Date non indiquee")}</div>
                <p>{resource.get("description", "")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.link_button(
            "Ouvrir le fichier du cours",
            resource.get("url", "https://drive.google.com/"),
            width="stretch",
        )


def show_search(data):
    st.subheader("Recherche rapide")
    query = st.text_input(
        "Rechercher un cours",
        placeholder="Exemple: prix, inflation, GRH, anglais...",
    )
    col1, col2 = st.columns(2)
    resource_type = col1.selectbox("Type", ["Tous"] + RESOURCE_TYPES)
    status = col2.selectbox("Statut", ["Tous"] + COURSE_STATUS)

    results = search_courses(data, query, resource_type, status)
    st.caption(f"{len(results)} resultat(s)")

    if not results:
        st.info("Aucun resultat trouve.")
        return

    for item in results:
        extra = f"{item.get('matiere')} | {item.get('date', 'Date non indiquee')}"
        show_resource_card(item, extra=extra)


def show_updates(data):
    st.markdown(
        """
        <div class="courses-hero">
            <div>
                <h1>Historique des nouveautes</h1>
                <p>Toutes les publications deja affichees sur le dashboard restent disponibles ici.</p>
            </div>
            <div class="courses-hero-art"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    items = latest_updates(data, limit=30)
    if not items:
        st.info("Aucune nouveaute pour le moment.")
        return

    for item in items:
        extra = (
            f"{item.get('matiere')} | {item.get('type')} | "
            f"{item.get('statut')} | {item.get('prof')} | {item.get('date')}"
        )
        show_resource_card(item, extra=extra)


def show_exams(data):
    st.markdown(
        """
        <div class="exam-page-shell">
            <div class="exam-hero">
                <div class="exam-icon-main">E</div>
                <div>
                    <h1>Examens nationaux precedents</h1>
                    <p>Consultez les anciens examens nationaux par matiere, annee et session.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    subject_filter = col1.selectbox("Filtrer par matiere", ["Toutes les matieres"] + SUBJECTS)
    years = sorted({exam.get("annee", "Archive") for exam in data["examens"]})
    year_filter = col2.selectbox("Annee", ["Toutes"] + years)
    sessions = sorted({exam.get("session", "Archive") for exam in data["examens"]})
    session_filter = col3.selectbox("Session", ["Toutes"] + sessions)

    exams = data["examens"]
    if subject_filter != "Toutes les matieres":
        exams = [
            exam
            for exam in exams
            if exam["matiere"] in (subject_filter, "Toutes les matieres")
        ]
    if year_filter != "Toutes":
        exams = [exam for exam in exams if exam.get("annee") == year_filter]
    if session_filter != "Toutes":
        exams = [exam for exam in exams if exam.get("session") == session_filter]

    if not exams:
        st.info("Aucun examen trouve pour cette matiere.")

    grouped_years = sorted(
        {exam.get("annee", "Archive") for exam in exams},
        reverse=True,
    )
    for year in grouped_years:
        st.markdown(f'<div class="section-title">{year}</div>', unsafe_allow_html=True)
        for exam in [exam for exam in exams if exam.get("annee", "Archive") == year]:
            st.markdown(
                f"""
                <div class="exam-card">
                    <div class="exam-card-head">
                        <div class="exam-card-icon">E</div>
                        <div>
                            <h3>{exam.get("titre", "Examen national")}</h3>
                            <div>
                                <span class="badge">Examen</span>
                                <span class="badge badge-new">Disponible</span>
                            </div>
                            <div class="exam-meta">
                                <span>{exam.get("matiere", "Toutes les matieres")}</span>
                                <span>{exam.get("annee", "Archive")}</span>
                                <span>{exam.get("session", "Archive")}</span>
                                <span>{exam.get("date", "Date non indiquee")}</span>
                            </div>
                            <div class="exam-description">{exam.get("description", "")}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('<div class="exam-action-wrap">', unsafe_allow_html=True)
            st.link_button("Ouvrir le lien Drive", exam.get("url", "https://drive.google.com/"), width="stretch")
            st.markdown("</div>", unsafe_allow_html=True)
            corrige_url = exam.get("corrige_url", "")
            if corrige_url:
                st.link_button("Ouvrir le corrige", corrige_url)


def show_homework_plan(data):
    st.markdown(
        """
        <div class="planning-shell">
            <div class="planning-hero">
                <div class="planning-title-wrap">
                    <div class="planning-icon-main">P</div>
                    <div>
                        <h1>Planification des examens</h1>
                        <p>Consultez uniquement la matiere et la date de chaque examen.</p>
                        <strong>Les dates de week-end ne sont pas affichees.</strong>
                    </div>
                </div>
                <div class="planning-art"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    subject_filter = st.selectbox(
        "Filtrer par matiere",
        ["Toutes les matieres"] + SUBJECTS,
    )

    devoirs = data.get("devoirs", [])
    if subject_filter != "Toutes les matieres":
        devoirs = [devoir for devoir in devoirs if devoir.get("matiere") == subject_filter]

    devoirs = [
        devoir for devoir in devoirs if not is_weekend_date(devoir.get("date_limite"))
    ]

    devoirs = sorted(devoirs, key=lambda devoir: parse_deadline(devoir.get("date_limite")))

    if not devoirs:
        st.markdown(
            """
            <div class="planning-empty">
                Aucun examen planifie pour le moment.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for devoir in devoirs:
        exam_date = devoir.get("date_limite", "")
        st.markdown(
            f"""
            <div class="planning-card">
                <div class="planning-card-icon">E</div>
                <div>
                    <h3>{devoir.get("matiere", "General")}</h3>
                    <div class="planning-date">
                        Date d'examen: <strong>{exam_date or "Non indiquee"}</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_shared_files(data):
    st.markdown(
        """
        <div class="files-hero">
            <div class="files-title-wrap">
                <div class="files-icon">F</div>
                <div>
                    <h1>Fichiers partages</h1>
                    <p>Documents, images, PDF, Word, Excel et autres fichiers partages par la direction ou les professeurs.</p>
                </div>
            </div>
            <div class="files-art"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    subject_filter = col1.selectbox(
        "Filtrer par matiere",
        ["Tous les fichiers", "Toutes les matieres"] + SUBJECTS,
    )
    source_filter = col2.selectbox(
        "Publie par",
        ["Tous", "Direction", "Professeur"],
    )

    files = data.get("shared_files", [])
    if subject_filter != "Tous les fichiers":
        files = [
            shared_file
            for shared_file in files
            if shared_file.get("matiere") in (subject_filter, "Toutes les matieres")
        ]

    if source_filter != "Tous":
        role = "direction" if source_filter == "Direction" else "prof"
        files = [shared_file for shared_file in files if shared_file.get("role") == role]

    files = sorted(files, key=lambda shared_file: parse_date(shared_file.get("date")), reverse=True)

    if not files:
        st.info("Aucun fichier partage pour le moment.")
        return

    for shared_file in files:
        render_shared_file(shared_file)


def show_student_space(data):
    st.subheader("Espace etudiant")
    st.write("Acces rapide aux cours, fiches Drive, examens et annonces importantes.")

    selected_subject = st.selectbox("Choisir une matiere", SUBJECTS)
    st.markdown(f"#### {selected_subject}")

    for resource in data["cours"].get(selected_subject, []):
        show_resource_card(resource, extra="Cours")

    st.markdown("#### Examens lies")
    related_exams = [
        exam
        for exam in data["examens"]
        if exam["matiere"] in (selected_subject, "Toutes les matieres")
    ]
    for exam in related_exams:
        show_resource_card(exam, extra=exam.get("annee", ""))


def add_course_form(data, subject, prof_name="Administration"):
    st.markdown("#### Ajouter un cours")
    st.caption(
        f"Remplissez ces informations pour publier un nouveau cours dans {subject}."
    )
    with st.form("add_course_form", clear_on_submit=True):
        st.text_input("Matiere du cours", value=subject, disabled=True)
        title = st.text_input(
            "Nom du cours",
            placeholder="Exemple: Politique de prix",
            help="Ecrivez le titre qui sera visible par les etudiants.",
        )
        description = st.text_area(
            "Description du cours",
            placeholder="Exemple: Cours PDF avec explication et exercices.",
            help="Ajoutez une courte phrase pour expliquer le contenu du cours.",
        )
        url = st.text_input(
            "Lien Drive/PDF du cours",
            placeholder="Exemple: https://drive.google.com/file/d/.../view",
            help="Collez le lien Google Drive du fichier PDF ou du dossier du cours.",
        )
        resource_type = st.selectbox(
            "Type de ressource",
            RESOURCE_TYPES,
            help="Classez la ressource pour faciliter la recherche.",
        )
        status = st.selectbox(
            "Statut du cours",
            COURSE_STATUS,
            help="Indiquez l'etat actuel du cours.",
        )
        submitted = st.form_submit_button("Ajouter le cours")

    if submitted:
        if not title or not url:
            st.error("Le titre et le lien Drive sont obligatoires.")
            return

        data["cours"].setdefault(subject, []).append(
            {
                "titre": title,
                "description": description,
                "url": url,
                "type": resource_type,
                "statut": status,
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "prof": prof_name,
            }
        )
        save_data(data)
        st.success("Cours ajoute avec succes.")
        st.rerun()


def delete_course_form(data, subject):
    st.markdown("#### Supprimer un cours")
    st.caption(
        f"Vous pouvez supprimer uniquement les cours de {subject}."
    )
    st.text_input("Matiere du cours a supprimer", value=subject, disabled=True)
    resources = data["cours"].get(subject, [])

    if not resources:
        st.info("Aucun cours a supprimer pour cette matiere.")
        return

    labels = [f"{index + 1}. {resource['titre']}" for index, resource in enumerate(resources)]
    selected = st.selectbox(
        "Cours a supprimer",
        labels,
        help="Selectionnez le cours exact avant de cliquer sur supprimer.",
    )

    if st.button("Supprimer ce cours", type="secondary"):
        selected_index = labels.index(selected)
        resources.pop(selected_index)
        save_data(data)
        st.success("Cours supprime.")
        st.rerun()


def add_exam_form(data, subject):
    st.markdown("#### Ajouter un examen national")
    st.caption(f"Ajoutez ici les examens nationaux de {subject}.")
    with st.form("add_exam_form", clear_on_submit=True):
        st.text_input("Matiere de l'examen", value=subject, disabled=True)
        year = st.text_input(
            "Annee de l'examen",
            placeholder="Exemple: 2024",
            help="Indiquez l'annee de l'examen. Si vous laissez vide, Archive sera utilise.",
        )
        session = st.selectbox(
            "Session",
            ["Session normale", "Rattrapage", "Archive"],
            help="Choisissez le type de session.",
        )
        title = st.text_input(
            "Nom de l'examen",
            placeholder="Exemple: Examen national 2024 - session normale",
            help="Ecrivez le titre visible par les etudiants.",
        )
        description = st.text_area(
            "Description de l'examen",
            placeholder="Exemple: Sujet national avec corrige.",
            help="Precisez si le fichier contient le sujet, le corrige ou les deux.",
        )
        url = st.text_input(
            "Lien Drive/PDF de l'examen",
            placeholder="Exemple: https://drive.google.com/file/d/.../view",
            help="Collez le lien Google Drive du fichier PDF ou du dossier d'examens.",
        )
        corrige_url = st.text_input(
            "Lien Drive/PDF du corrige",
            placeholder="Optionnel: https://drive.google.com/file/d/.../view",
            help="Ajoutez le corrige si vous l'avez. Ce champ peut rester vide.",
        )
        submitted = st.form_submit_button("Ajouter l'examen")

    if submitted:
        if not title or not url:
            st.error("Le titre et le lien Drive sont obligatoires.")
            return

        data["examens"].append(
            {
                "titre": title,
                "matiere": subject,
                "annee": year or "Archive",
                "session": session,
                "description": description,
                "url": url,
                "corrige_url": corrige_url,
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
        )
        save_data(data)
        st.success("Examen ajoute avec succes.")
        st.rerun()


def delete_exam_form(data, subject):
    st.markdown("#### Supprimer un examen")
    st.caption(f"Vous pouvez supprimer uniquement les examens de {subject}.")
    subject_exams = [
        exam for exam in data["examens"] if exam.get("matiere") == subject
    ]

    if not subject_exams:
        st.info("Aucun examen a supprimer.")
        return

    labels = [
        f"{index + 1}. {exam['titre']} - {exam.get('annee', '')}"
        for index, exam in enumerate(subject_exams)
    ]
    selected = st.selectbox(
        "Examen a supprimer",
        labels,
        help="Selectionnez l'examen exact avant de cliquer sur supprimer.",
    )

    if st.button("Supprimer cet examen", type="secondary"):
        selected_index = labels.index(selected)
        exam_to_delete = subject_exams[selected_index]
        data["examens"].remove(exam_to_delete)
        save_data(data)
        st.success("Examen supprime.")
        st.rerun()


def message_admin(data, subject, prof_name):
    st.markdown("#### Messages aux etudiants")
    st.caption(f"Publiez une annonce visible pour la matiere {subject}.")
    with st.form("add_message_form", clear_on_submit=True):
        st.text_input("Matiere du message", value=subject, disabled=True)
        title = st.text_input(
            "Titre du message",
            placeholder="Exemple: Controle le lundi 27 mai",
            help="Titre court de l'annonce visible par les etudiants.",
        )
        content = st.text_area(
            "Contenu du message",
            placeholder="Exemple: Merci de reviser les chapitres 1 et 2 avant le controle.",
            help="Ecrivez le message complet a afficher aux etudiants.",
        )
        important = st.checkbox(
            "Message important",
            help="Les messages importants restent en haut du dashboard.",
        )
        submitted = st.form_submit_button("Publier le message")

    if submitted:
        if not title or not content:
            st.error("Le titre et le message sont obligatoires.")
            return

        data["messages"].insert(
            0,
            {
                "titre": title,
                "matiere": subject,
                "prof": prof_name,
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "important": important,
                "contenu": content,
            },
        )
        save_data(data)
        st.success("Message publie.")
        st.rerun()

    subject_messages = [
        message for message in data["messages"] if message.get("matiere") == subject
    ]

    if subject_messages:
        labels = [
            f"{index + 1}. {message['titre']}"
            for index, message in enumerate(subject_messages)
        ]
        selected = st.selectbox(
            "Message a supprimer",
            labels,
            help="Selectionnez l'annonce a retirer de la page d'accueil.",
        )

        if st.button("Supprimer ce message", type="secondary"):
            selected_index = labels.index(selected)
            message_to_delete = subject_messages[selected_index]
            data["messages"].remove(message_to_delete)
            save_data(data)
            st.success("Message supprime.")
            st.rerun()
    else:
        st.info("Aucun message publie pour votre matiere.")


def homework_admin(data, subject, prof_name):
    st.markdown("#### Ajouter une date d'examen")
    st.caption(f"Planifiez une date d'examen pour {subject}.")

    st.text_input("Matiere", value=subject, disabled=True)
    selected_deadline = weekday_calendar_picker(f"exam_calendar_{subject}")
    submitted = st.button("Publier la date d'examen")

    if submitted:
        if not selected_deadline:
            st.error("Choisissez une date avant de publier.")
            return

        data.setdefault("devoirs", []).append(
            {
                "matiere": subject,
                "titre": f"Examen - {subject}",
                "description": "",
                "date_limite": selected_deadline,
                "lien": "",
                "prof": prof_name,
                "date_publication": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
        )
        save_data(data)
        st.success("Date d'examen publiee.")
        st.rerun()

    st.divider()
    st.markdown("#### Supprimer une date d'examen")
    subject_homework = [
        devoir for devoir in data.get("devoirs", []) if devoir.get("matiere") == subject
    ]

    if not subject_homework:
        st.info("Aucune date d'examen a supprimer pour cette matiere.")
        return

    labels = [
        f"{index + 1}. {devoir.get('matiere', subject)} - {devoir.get('date_limite', '')}"
        for index, devoir in enumerate(subject_homework)
    ]
    selected = st.selectbox("Date d'examen a supprimer", labels)

    if st.button("Supprimer cette date", type="secondary"):
        selected_index = labels.index(selected)
        data["devoirs"].remove(subject_homework[selected_index])
        save_data(data)
        st.success("Date d'examen supprimee.")
        st.rerun()


def shared_file_admin(data, subject, author, role):
    st.markdown("#### Partager un fichier")
    st.caption("Vous pouvez partager une image, un PDF, un fichier Word, Excel ou tout autre type de fichier.")

    with st.form(f"share_file_form_{role}_{subject}", clear_on_submit=True):
        if role == "direction":
            target_subject = st.selectbox(
                "Destination",
                ["Toutes les matieres"] + SUBJECTS,
                help="Choisissez Toutes les matieres pour publier a tous les etudiants.",
            )
        else:
            target_subject = subject
            st.text_input("Matiere", value=target_subject, disabled=True)

        title = st.text_input(
            "Titre du fichier",
            placeholder="Exemple: Planning general, modele Excel, affiche, document important...",
        )
        description = st.text_area(
            "Description",
            placeholder="Expliquez rapidement le contenu du fichier.",
        )
        uploaded_file = st.file_uploader(
            "Choisir un fichier",
            accept_multiple_files=False,
            help="Tous les formats sont acceptes: PDF, Word, Excel, image, archive, etc.",
        )
        submitted = st.form_submit_button("Partager le fichier")

    if submitted:
        if not title or uploaded_file is None:
            st.error("Le titre et le fichier sont obligatoires.")
            return

        path = save_uploaded_file(uploaded_file, folder=target_subject)
        data.setdefault("shared_files", []).insert(
            0,
            {
                "titre": title,
                "description": description,
                "matiere": target_subject,
                "auteur": author,
                "role": role,
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "filename": uploaded_file.name,
                "path": str(path),
                "mime": uploaded_file.type or "application/octet-stream",
            },
        )
        save_data(data)
        st.success("Fichier partage avec succes.")
        st.rerun()

    st.divider()
    st.markdown("#### Supprimer un fichier partage")
    if role == "direction":
        manageable_files = data.get("shared_files", [])
    else:
        manageable_files = [
            shared_file
            for shared_file in data.get("shared_files", [])
            if shared_file.get("matiere") == subject and shared_file.get("auteur") == author
        ]

    if not manageable_files:
        st.info("Aucun fichier a supprimer.")
        return

    labels = [
        f"{index + 1}. {shared_file.get('titre')} - {shared_file.get('matiere')}"
        for index, shared_file in enumerate(manageable_files)
    ]
    selected = st.selectbox("Fichier a supprimer", labels)
    if st.button("Supprimer ce fichier", type="secondary"):
        selected_index = labels.index(selected)
        file_to_delete = manageable_files[selected_index]
        data["shared_files"].remove(file_to_delete)
        save_data(data)
        st.success("Fichier retire de la plateforme.")
        st.rerun()


def student_contact_inbox(data, subject):
    st.markdown("#### Messages des etudiants")
    messages = [
        contact
        for contact in data.get("student_contacts", [])
        if contact.get("matiere") == subject
    ]
    messages = sorted(messages, key=lambda contact: parse_date(contact.get("date")), reverse=True)

    if not messages:
        st.info("Aucun message d'etudiant pour votre matiere.")
        return

    for index, contact in enumerate(messages):
        st.markdown(
            f"""
            <div class="message">
                <div class="message-title">{contact.get("prenom", "")} {contact.get("nom", "")}</div>
                <div class="message-meta">
                    Matiere: {contact.get("matiere", "")} | Date: {contact.get("date", "Date non indiquee")}
                </div>
                <div class="message-content">{contact.get("message", "")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if contact.get("reponse"):
            st.success(f"Reponse envoyee: {contact.get('reponse')}")
        else:
            response = st.text_area(
                "Repondre a cet etudiant",
                key=f"response_{subject}_{index}_{contact.get('date')}",
            )
            if st.button("Envoyer la reponse", key=f"send_response_{subject}_{index}_{contact.get('date')}"):
                if not response.strip():
                    st.error("La reponse ne peut pas etre vide.")
                else:
                    contact["reponse"] = response.strip()
                    contact["date_reponse"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    save_data(data)
                    st.success("Reponse enregistree.")
                    st.rerun()


def student_accounts_admin(data):
    st.markdown("#### Validation des comptes etudiants")
    accounts = data.setdefault("student_accounts", {})

    if not accounts:
        st.info("Aucune demande d'inscription pour le moment.")
        return

    status_filter = st.selectbox(
        "Filtrer par statut",
        ["Tous", "En attente", "Valides", "Refuses"],
        key="student_account_status_filter",
    )
    status_map = {
        "En attente": "pending",
        "Valides": "approved",
        "Refuses": "rejected",
    }
    filtered_accounts = list(accounts.items())
    if status_filter != "Tous":
        filtered_accounts = [
            (email, account)
            for email, account in filtered_accounts
            if account.get("status") == status_map[status_filter]
        ]

    if not filtered_accounts:
        st.info("Aucun compte dans ce filtre.")
        return

    for email, account in sorted(filtered_accounts, key=lambda item: item[1].get("created_at", ""), reverse=True):
        status = account.get("status", "pending")
        status_label = {
            "pending": "En attente",
            "approved": "Valide",
            "rejected": "Refuse",
        }.get(status, status)
        st.markdown(
            f"""
            <div class="card">
                <h3>{account.get('prenom', '')} {account.get('nom', '')}</h3>
                <p>
                    Email: <strong>{email}</strong><br>
                    Groupe: <strong>{account.get('groupe', 'Non indique')}</strong><br>
                    Statut: <strong>{status_label}</strong><br>
                    Demande envoyee: {account.get('created_at', 'Date non indiquee')}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns(3)
        if col1.button("Valider", key=f"approve_student_{email}", disabled=status == "approved"):
            accounts[email]["status"] = "approved"
            accounts[email]["validated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            save_data(data)
            st.success("Compte etudiant valide.")
            st.rerun()
        if col2.button("Refuser", key=f"reject_student_{email}", disabled=status == "rejected"):
            accounts[email]["status"] = "rejected"
            save_data(data)
            st.warning("Compte etudiant refuse.")
            st.rerun()
        if col3.button("Supprimer", key=f"delete_student_{email}"):
            del accounts[email]
            save_data(data)
            st.success("Compte etudiant supprime.")
            st.rerun()


def support_tickets_admin(data):
    st.markdown(
        """
        <div class="contact-hero">
            <div class="contact-title-wrap">
                <div class="contact-icon">S</div>
                <div>
                    <h1>Support admin</h1>
                    <p>Consultez les reclamations envoyees par les utilisateurs et repondez directement depuis cette page.</p>
                </div>
            </div>
            <div class="contact-art"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tickets = data.get("support_tickets", [])
    if not tickets:
        st.info("Aucune reclamation pour le moment.")
        return

    status_filter = st.selectbox(
        "Filtrer par statut",
        ["Tous", "Nouveau", "En cours", "Traite"],
        key="support_status_filter",
    )
    filtered_tickets = tickets
    if status_filter != "Tous":
        filtered_tickets = [
            ticket for ticket in tickets if ticket.get("statut", "Nouveau") == status_filter
        ]

    if not filtered_tickets:
        st.info("Aucune reclamation dans ce filtre.")
        return

    for index, ticket in enumerate(filtered_tickets):
        original_index = tickets.index(ticket)
        st.markdown(
            f"""
            <div class="message">
                <div class="message-title">{ticket.get('sujet', 'Reclamation')}</div>
                <div class="message-meta">
                    Type: {ticket.get('type', 'Reclamation')} | Statut: {ticket.get('statut', 'Nouveau')} | Date: {ticket.get('date', 'Date non indiquee')}
                </div>
                <div class="message-content">
                    Utilisateur: <strong>{ticket.get('nom', 'Utilisateur')}</strong><br>
                    Email: <strong>{ticket.get('email', 'Non indique')}</strong><br><br>
                    {ticket.get('message', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_local_attachment(
            ticket.get("screenshot_path", ""),
            ticket.get("screenshot_name", ""),
            ticket.get("screenshot_mime", "application/octet-stream"),
            key_prefix=f"support_ticket_{original_index}_{ticket.get('date', '')}",
        )

        if ticket.get("reponse"):
            st.success(
                f"Reponse admin ({ticket.get('date_reponse', 'Date non indiquee')}): {ticket.get('reponse')}"
            )

        response = st.text_area(
            "Reponse a envoyer a l'utilisateur",
            value=ticket.get("reponse", ""),
            key=f"support_response_{original_index}_{ticket.get('date', '')}",
        )
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Enregistrer la reponse", key=f"support_reply_{original_index}_{ticket.get('date')}"):
            if not response.strip():
                st.error("La reponse ne peut pas etre vide.")
            else:
                tickets[original_index]["reponse"] = response.strip()
                tickets[original_index]["date_reponse"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                tickets[original_index]["statut"] = "Traite"
                save_data(data)
                st.success("Reponse envoyee et reclamation marquee comme traitee.")
                st.rerun()
        if col2.button("En cours", key=f"support_progress_{original_index}_{ticket.get('date')}"):
            tickets[original_index]["statut"] = "En cours"
            save_data(data)
            st.rerun()
        if col3.button("Traite", key=f"support_done_{original_index}_{ticket.get('date')}"):
            tickets[original_index]["statut"] = "Traite"
            tickets[original_index]["date_reponse"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            save_data(data)
            st.rerun()
        if col4.button("Supprimer", key=f"support_delete_{original_index}_{ticket.get('date')}"):
            tickets.pop(original_index)
            save_data(data)
            st.rerun()


def user_management_admin(data):
    st.markdown("#### Gestion des utilisateurs")
    st.caption("Identifiants, messages, bannissement, suppression et mots de passe.")

    users = []
    users.append({
        "email": STUDENT_EMAIL,
        "name": "Compte etudiant general",
        "role": "Etudiant general",
        "password": "Protege par configuration",
        "status": "Actif",
        "kind": "system",
    })
    users.append({
        "email": GUEST_EMAIL,
        "name": "Compte invite test",
        "role": "Invite",
        "password": "Protege par configuration",
        "status": "Actif",
        "kind": "system",
    })
    users.append({
        "email": DIRECTION_EMAIL,
        "name": "Direction BTS SMARTCAMPUS",
        "role": "Direction",
        "password": "Protege par configuration",
        "status": "Actif",
        "kind": "system",
    })

    for email, account in data.get("prof_accounts", {}).items():
        users.append({
            "email": email,
            "name": account.get("name", "Professeur"),
            "role": account.get("role", "prof"),
            "password": "Protege",
            "status": "Banni" if account.get("banned") else "Actif",
            "kind": "prof",
        })

    for email, account in data.get("student_accounts", {}).items():
        status = account.get("status", "pending")
        status_label = {"pending": "En attente", "approved": "Valide", "rejected": "Refuse"}.get(status, status)
        if account.get("banned"):
            status_label = "Banni"
        users.append({
            "email": email,
            "name": f"{account.get('prenom', '')} {account.get('nom', '')}".strip() or "Etudiant",
            "role": f"Etudiant - {account.get('groupe', 'Sans groupe')}",
            "password": "Protege",
            "status": status_label,
            "kind": "student",
        })

    search = st.text_input("Rechercher un utilisateur", placeholder="Nom, email, role...")
    if search.strip():
        needle = search.strip().lower()
        users = [
            user for user in users
            if needle in user["email"].lower()
            or needle in user["name"].lower()
            or needle in user["role"].lower()
        ]

    if not users:
        st.info("Aucun utilisateur trouve.")
        return

    actionable_users = [user for user in users if user["kind"] != "system"]
    if actionable_users:
        st.markdown("#### Panneau d'action rapide")
        selected_email = st.selectbox(
            "Choisir un utilisateur a gerer",
            [user["email"] for user in actionable_users],
            format_func=lambda email: next(
                f"{user['name']} | {user['email']} | {user['role']} | {user['status']}"
                for user in actionable_users
                if user["email"] == email
            ),
            key="admin_quick_user_select",
        )
        selected_user = next(user for user in actionable_users if user["email"] == selected_email)
        st.markdown(
            f"""
            <div class="card">
                <h3>Utilisateur selectionne: {selected_user["name"]}</h3>
                <p>
                    Role: <strong>{selected_user["role"]}</strong><br>
                    Email: <strong>{selected_user["email"]}</strong><br>
                    Statut: <strong>{selected_user["status"]}</strong>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        new_password = st.text_input(
            "Nouveau mot de passe",
            type="password",
            key=f"quick_password_{selected_user['kind']}_{selected_user['email']}",
        )
        msg_title = st.text_input(
            "Titre du message",
            key=f"quick_message_title_{selected_user['kind']}_{selected_user['email']}",
        )
        msg_content = st.text_area(
            "Message a envoyer",
            key=f"quick_message_content_{selected_user['kind']}_{selected_user['email']}",
        )
        col1, col2, col3, col4 = st.columns(4)

        if col1.button("Changer mot de passe", key=f"quick_pwd_{selected_user['kind']}_{selected_user['email']}"):
            if not new_password.strip():
                st.error("Le nouveau mot de passe est obligatoire.")
            elif selected_user["kind"] == "prof":
                data["prof_accounts"][selected_user["email"]]["password"] = hash_password(new_password.strip())
                save_data(data)
                st.success("Mot de passe professeur modifie.")
                st.rerun()
            else:
                data["student_accounts"][selected_user["email"]]["password"] = hash_password(new_password.strip())
                save_data(data)
                st.success("Mot de passe etudiant modifie.")
                st.rerun()

        is_banned = selected_user["status"] == "Banni"
        ban_label = "Debannir" if is_banned else "Bannir"
        if col2.button(ban_label, key=f"quick_ban_{selected_user['kind']}_{selected_user['email']}"):
            if selected_user["kind"] == "prof":
                data["prof_accounts"][selected_user["email"]]["banned"] = not is_banned
            else:
                data["student_accounts"][selected_user["email"]]["banned"] = not is_banned
            save_data(data)
            st.success("Statut de bannissement mis a jour.")
            st.rerun()

        if col3.button("Envoyer message", key=f"quick_msg_{selected_user['kind']}_{selected_user['email']}"):
            if not msg_title.strip() or not msg_content.strip():
                st.error("Le titre et le message sont obligatoires.")
            elif selected_user["kind"] == "student":
                data["student_accounts"][selected_user["email"]].setdefault("admin_messages", []).insert(
                    0,
                    {
                        "titre": msg_title.strip(),
                        "contenu": msg_content.strip(),
                        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    },
                )
                save_data(data)
                st.success("Message envoye a l'etudiant.")
                st.rerun()
            else:
                data.setdefault("messages", []).insert(
                    0,
                    {
                        "titre": msg_title.strip(),
                        "matiere": data["prof_accounts"][selected_user["email"]].get("subject", "General"),
                        "prof": "Administration BTS SMARTCAMPUS",
                        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "important": True,
                        "contenu": f"Message destine a {selected_user['name']}: {msg_content.strip()}",
                    },
                )
                save_data(data)
                st.success("Message enregistre pour le professeur.")
                st.rerun()

        if col4.button("Supprimer", key=f"quick_delete_{selected_user['kind']}_{selected_user['email']}"):
            if selected_user["kind"] == "prof":
                if selected_user["email"] == ADMIN_EMAIL:
                    st.error("Impossible de supprimer le compte admin.")
                else:
                    del data["prof_accounts"][selected_user["email"]]
                    save_data(data)
                    st.success("Compte professeur supprime.")
                    st.rerun()
            else:
                del data["student_accounts"][selected_user["email"]]
                save_data(data)
                st.success("Compte etudiant supprime.")
                st.rerun()

    st.markdown("#### Liste des identifiants")
    for user in users:
        is_system = user["kind"] == "system"
        st.markdown(
            f"""
            <div class="card">
                <h3>{user["name"]}</h3>
                <p>
                    Role: <strong>{user["role"]}</strong><br>
                    Email: <strong>{user["email"]}</strong><br>
                    Mot de passe: <strong>{user["password"]}</strong><br>
                    Statut: <strong>{user["status"]}</strong>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if is_system:
            st.caption("Compte systeme: changez ces identifiants dans les variables d'environnement ou dans le code.")
        else:
            st.caption("Pour modifier ce compte, utilisez le panneau d'action rapide en haut.")


def show_admin_space(data):
    st.success("Connecte: Administration BTS SMARTCAMPUS | Acces complet")

    section = st.radio(
        "Choisir une section",
        ["Cours", "Examens", "Messages", "Planning examens", "Fichiers", "Discussion", "Utilisateurs", "Comptes etudiants", "Support"],
        horizontal=True,
        key="admin_section_choice",
    )

    if section == "Cours":
        subject = st.selectbox("Matiere a gerer", SUBJECTS, key="admin_course_subject")
        add_course_form(data, subject, "Administration BTS SMARTCAMPUS")
        st.divider()
        delete_course_form(data, subject)

    elif section == "Examens":
        subject = st.selectbox("Matiere des examens", SUBJECTS, key="admin_exam_subject")
        add_exam_form(data, subject)
        st.divider()
        delete_exam_form(data, subject)

    elif section == "Messages":
        subject = st.selectbox("Matiere du message", SUBJECTS, key="admin_message_subject")
        message_admin(data, subject, "Administration BTS SMARTCAMPUS")

    elif section == "Planning examens":
        subject = st.selectbox("Matiere de l'examen", SUBJECTS, key="admin_homework_subject")
        homework_admin(data, subject, "Administration BTS SMARTCAMPUS")

    elif section == "Fichiers":
        subject = st.selectbox("Matiere du fichier", SUBJECTS, key="admin_file_subject")
        shared_file_admin(data, subject, "Administration BTS SMARTCAMPUS", "direction")

    elif section == "Discussion":
        subject = st.selectbox("Matiere des messages", SUBJECTS, key="admin_contact_subject")
        student_contact_inbox(data, subject)

    elif section == "Utilisateurs":
        user_management_admin(data)
    elif section == "Comptes etudiants":
        student_accounts_admin(data)
    else:
        support_tickets_admin(data)


def show_prof_space(data):
    user_role = st.session_state.get("platform_user_role", "student")
    user_email = st.session_state.get("platform_user_email", "")

    if user_role not in ("prof", "admin"):
        st.error("Acces reserve aux professeurs et a l'administration.")
        return

    if user_role == "admin":
        show_admin_space(data)
        return

    account = data.get("prof_accounts", {}).get(user_email)
    if not account:
        st.error("Compte professeur introuvable.")
        return

    st.subheader("Espace professeur")
    subject = account.get("subject", "General")
    prof_name = account.get("name", "Professeur")
    st.success(f"Connecte: {prof_name} | Matiere: {subject}")

    section = st.radio(
        "Choisir une section",
        ["Cours", "Examens", "Messages", "Planning examens", "Fichiers", "Discussion"],
        horizontal=True,
        key="prof_section_choice",
    )

    if section == "Cours":
        add_course_form(data, subject, prof_name)
        st.divider()
        delete_course_form(data, subject)

    elif section == "Examens":
        add_exam_form(data, subject)
        st.divider()
        delete_exam_form(data, subject)

    elif section == "Messages":
        message_admin(data, subject, prof_name)

    elif section == "Planning examens":
        homework_admin(data, subject, prof_name)

    elif section == "Fichiers":
        shared_file_admin(data, subject, prof_name, "prof")

    else:
        student_contact_inbox(data, subject)


def show_direction_space(data):
    user_role = st.session_state.get("platform_user_role", "student")
    if user_role not in ("direction", "admin"):
        st.error("Acces reserve a la direction.")
        return

    st.subheader("Espace direction")
    st.success("Connecte: Direction BTS SMARTCAMPUS")

    section = st.radio(
        "Choisir une section",
        ["Messages officiels", "Fichiers partages", "Comptes etudiants"],
        horizontal=True,
        key="direction_section_choice",
    )

    if section == "Messages officiels":
        st.markdown("#### Diffuser un message officiel")
        with st.form("direction_message_form", clear_on_submit=True):
            title = st.text_input(
                "Titre du message",
                placeholder="Exemple: Reunion importante, annonce officielle...",
            )
            target_subject = st.selectbox("Destination", ["Toutes les matieres"] + SUBJECTS)
            content = st.text_area("Message")
            important = st.checkbox("Message important", value=True)
            uploaded_file = st.file_uploader(
                "Ajouter un fichier au message",
                accept_multiple_files=False,
                help="Optionnel: image, PDF, Word, Excel ou autre fichier.",
            )
            submitted = st.form_submit_button("Diffuser le message")

        if submitted:
            if not title or not content:
                st.error("Le titre et le message sont obligatoires.")
                return

            data["messages"].insert(
                0,
                {
                    "titre": title,
                    "matiere": target_subject,
                    "prof": "Direction BTS SMARTCAMPUS",
                    "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "important": important,
                    "contenu": content,
                },
            )

            if uploaded_file is not None:
                path = save_uploaded_file(uploaded_file, folder=target_subject)
                data.setdefault("shared_files", []).insert(
                    0,
                    {
                        "titre": title,
                        "description": content,
                        "matiere": target_subject,
                        "auteur": "Direction BTS SMARTCAMPUS",
                        "role": "direction",
                        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "filename": uploaded_file.name,
                        "path": str(path),
                        "mime": uploaded_file.type or "application/octet-stream",
                    },
                )

            save_data(data)
            st.success("Message officiel diffuse.")
            st.rerun()

    elif section == "Fichiers partages":
        shared_file_admin(data, "Toutes les matieres", "Direction BTS SMARTCAMPUS", "direction")
    elif section == "Comptes etudiants":
        student_accounts_admin(data)


def show_contact(data):
    current_email = st.session_state.get("platform_user_email", "")
    current_student = data.get("student_accounts", {}).get(current_email, {})
    default_first_name = current_student.get("prenom", "")
    default_last_name = current_student.get("nom", "")
    st.markdown(
        """
        <div class="contact-topbar">
            <div class="contact-brand">BTS <span>SMART</span>CAMPUS</div>
            <div class="contact-user">
                <span>Bonjour,<br><strong>Etudiant</strong></span>
                <span class="contact-avatar"></span>
            </div>
        </div>
        <div class="contact-hero">
            <div class="contact-title-wrap">
                <div class="contact-icon">C</div>
                <div>
                    <h1>Discussion avec les professeurs</h1>
                    <p>Choisissez une matiere, puis envoyez votre message au professeur concerne.</p>
                </div>
            </div>
            <div class="contact-art"></div>
        </div>
        <div class="contact-form-title">Envoyer une demande</div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("student_contact_form", clear_on_submit=True):
        subject = st.selectbox("Matiere", SUBJECTS)
        col1, col2 = st.columns(2)
        first_name = col1.text_input("Prenom", value=default_first_name, placeholder="Votre prenom")
        last_name = col2.text_input("Nom", value=default_last_name, placeholder="Votre nom")
        message = st.text_area(
            "Message",
            placeholder="Ecrivez votre question ou votre demande au professeur...",
        )
        submitted = st.form_submit_button("Envoyer au professeur")

    if submitted:
        if not first_name.strip() or not last_name.strip() or not message.strip():
            st.error("La matiere, le nom, le prenom et le message sont obligatoires.")
            return

        data.setdefault("student_contacts", []).insert(
            0,
            {
                "matiere": subject,
                "nom": last_name.strip(),
                "prenom": first_name.strip(),
                "message": message.strip(),
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "reponse": "",
                "date_reponse": "",
            },
        )
        save_data(data)
        st.success("Votre message a ete envoye au professeur.")

    st.markdown(
        """
        <div class="contact-help">
            <span class="contact-help-icon">i</span>
            <span>Votre message sera transmis directement au professeur de la matiere selectionnee.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_support(data):
    user_label = st.session_state.get("platform_user_label", "Utilisateur")
    user_email = st.session_state.get("platform_user_email", "")
    user_role = st.session_state.get("platform_user_role", "student")

    if user_role == "admin":
        support_tickets_admin(data)
        return

    st.markdown(
        """
        <div class="contact-topbar">
            <div class="contact-brand">BTS <span>SMART</span>CAMPUS</div>
            <div class="contact-user">
                <span>Centre<br><strong>Support</strong></span>
                <span class="contact-avatar"></span>
            </div>
        </div>
        <div class="contact-hero">
            <div class="contact-title-wrap">
                <div class="contact-icon">S</div>
                <div>
                    <h1>Contact & support</h1>
                    <p>Envoyez une reclamation, un probleme technique ou une demande d'aide au support de la plateforme.</p>
                </div>
            </div>
            <div class="contact-art"></div>
        </div>
        <div class="contact-form-title">Nouvelle reclamation</div>
        """,
        unsafe_allow_html=True,
    )

    show_support_assistant(data, user_label, user_email, user_role)
    st.divider()

    with st.form("support_ticket_form", clear_on_submit=True):
        ticket_type = st.selectbox(
            "Type de demande",
            ["Reclamation", "Probleme technique", "Probleme de compte", "Suggestion", "Autre"],
        )
        col1, col2 = st.columns(2)
        name = col1.text_input("Nom complet", value=user_label if user_label != "Invite" else "")
        email = col2.text_input("Email", value=user_email)
        subject = st.text_input("Sujet")
        message = st.text_area(
            "Message",
            placeholder="Expliquez clairement votre reclamation ou le probleme rencontre...",
        )
        screenshot = st.file_uploader(
            "Capture d'ecran ou fichier du probleme (optionnel)",
            accept_multiple_files=False,
            help="Optionnel: ajoutez une capture d'ecran, une image, un PDF ou un autre fichier si cela aide le support.",
        )
        submitted = st.form_submit_button("Envoyer au support")

    if submitted:
        if not name.strip() or not subject.strip() or not message.strip():
            st.error("Le nom, le sujet et le message sont obligatoires.")
            return

        screenshot_path = ""
        screenshot_name = ""
        screenshot_mime = ""
        if screenshot is not None:
            path = save_uploaded_file(screenshot, folder="support")
            screenshot_path = str(path)
            screenshot_name = screenshot.name
            screenshot_mime = screenshot.type or "application/octet-stream"

        data.setdefault("support_tickets", []).insert(
            0,
            {
                "type": ticket_type,
                "nom": name.strip(),
                "email": email.strip(),
                "role": user_role,
                "sujet": subject.strip(),
                "message": message.strip(),
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "statut": "Nouveau",
                "reponse": "",
                "date_reponse": "",
                "screenshot_path": screenshot_path,
                "screenshot_name": screenshot_name,
                "screenshot_mime": screenshot_mime,
            },
        )
        save_data(data)
        st.success("Votre demande a ete envoyee au support.")

    st.markdown(
        """
        <div class="contact-help">
            <span class="contact-help-icon">i</span>
            <span>Votre reclamation sera geree par l'admin ou le support de la plateforme.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_tickets = [
        ticket
        for ticket in data.get("support_tickets", [])
        if ticket.get("email", "").strip().lower() == user_email.strip().lower()
    ]
    if user_tickets:
        st.markdown("#### Mes reclamations")
        for index, ticket in enumerate(sorted(user_tickets, key=lambda item: parse_date(item.get("date")), reverse=True)):
            response_html = ""
            if ticket.get("reponse"):
                response_html = f"""
                    <div class="message-content">
                        <strong>Reponse support:</strong><br>
                        {ticket.get('reponse', '')}<br>
                        <span class="message-meta">Date de reponse: {ticket.get('date_reponse', 'Date non indiquee')}</span>
                    </div>
                """
            st.markdown(
                f"""
                <div class="message">
                    <div class="message-title">{ticket.get('sujet', 'Reclamation')}</div>
                    <div class="message-meta">
                        Type: {ticket.get('type', 'Reclamation')} | Statut: {ticket.get('statut', 'Nouveau')} | Date: {ticket.get('date', 'Date non indiquee')}
                    </div>
                    <div class="message-content">{ticket.get('message', '')}</div>
                    {response_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_local_attachment(
                ticket.get("screenshot_path", ""),
                ticket.get("screenshot_name", ""),
                ticket.get("screenshot_mime", "application/octet-stream"),
                key_prefix=f"user_support_ticket_{index}_{ticket.get('date', '')}",
            )


def show_direct_messages(data):
    current_email = st.session_state.get("platform_user_email", "")
    current_role = st.session_state.get("platform_user_role", "student")
    current_name = st.session_state.get("platform_user_label", "Utilisateur")

    st.markdown(
        """
        <div class="contact-topbar">
            <div class="contact-brand">BTS <span>SMART</span>CAMPUS</div>
            <div class="contact-user">
                <span>Boite<br><strong>Messages</strong></span>
                <span class="contact-avatar"></span>
            </div>
        </div>
        <div class="contact-hero">
            <div class="contact-title-wrap">
                <div class="contact-icon">M</div>
                <div>
                    <h1>Messages</h1>
                    <p>Consultez vos messages administratifs et les pieces jointes envoyees.</p>
                </div>
            </div>
            <div class="contact-art"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if current_role == "admin":
        st.markdown("#### Envoyer un message a un utilisateur")
        recipients = platform_users_directory(data)
        recipient_email = st.selectbox(
            "Utilisateur destinataire",
            [user["email"] for user in recipients],
            format_func=lambda email: next(
                f"{user['name']} | {user['email']} | {user['role']}"
                for user in recipients
                if user["email"] == email
            ),
            key="direct_message_recipient",
        )
        recipient = next(user for user in recipients if user["email"] == recipient_email)

        with st.form("direct_message_form", clear_on_submit=True):
            title = st.text_input("Titre du message")
            content = st.text_area("Message")
            uploaded_file = st.file_uploader(
                "Ajouter une photo, PDF, Word, Excel ou autre fichier (optionnel)",
                accept_multiple_files=False,
            )
            submitted = st.form_submit_button("Envoyer le message")

        if submitted:
            if not title.strip() or not content.strip():
                st.error("Le titre et le message sont obligatoires.")
            else:
                attachment_path = ""
                attachment_name = ""
                attachment_mime = "application/octet-stream"
                if uploaded_file is not None:
                    path = save_uploaded_file(uploaded_file, folder="direct_messages")
                    attachment_path = str(path)
                    attachment_name = uploaded_file.name
                    attachment_mime = uploaded_file.type or "application/octet-stream"

                data.setdefault("direct_messages", []).insert(
                    0,
                    {
                        "from_email": current_email or ADMIN_EMAIL,
                        "from_name": current_name or "Administration BTS SMARTCAMPUS",
                        "to_email": recipient["email"],
                        "to_name": recipient["name"],
                        "titre": title.strip(),
                        "contenu": content.strip(),
                        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "attachment_path": attachment_path,
                        "attachment_name": attachment_name,
                        "attachment_mime": attachment_mime,
                        "read": False,
                    },
                )
                save_data(data)
                st.success("Message envoye.")
                st.rerun()

    st.markdown("#### Boite de reception")
    messages = [
        message
        for message in data.get("direct_messages", [])
        if message.get("to_email") == current_email or current_role == "admin"
    ]
    messages = sorted(messages, key=lambda message: parse_date(message.get("date")), reverse=True)

    if not messages:
        st.info("Aucun message pour le moment.")
        return

    for index, message in enumerate(messages):
        target_line = (
            f" | Destinataire: {message.get('to_name', '')} ({message.get('to_email', '')})"
            if current_role == "admin"
            else ""
        )
        st.markdown(
            f"""
            <div class="message">
                <div class="message-title">{message.get("titre", "Message")}</div>
                <div class="message-meta">
                    De: {message.get("from_name", "Administration BTS SMARTCAMPUS")} | Date: {message.get("date", "Date non indiquee")}{target_line}
                </div>
                <div class="message-content">{message.get("contenu", "")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_local_attachment(
            message.get("attachment_path", ""),
            message.get("attachment_name", ""),
            message.get("attachment_mime", "application/octet-stream"),
            key_prefix=f"direct_message_{index}_{message.get('date', '')}",
        )

        if current_role == "admin":
            if st.button("Supprimer ce message", key=f"delete_direct_message_{index}_{message.get('date', '')}"):
                data["direct_messages"].remove(message)
                save_data(data)
                st.success("Message supprime.")
                st.rerun()


def sidebar_navigation():
    student_pages = [
        ("Accueil", "Accueil"),
        ("Cours", "Cours"),
        ("Fichiers partages", "Fichiers Drive"),
        ("Examens nationaux", "Examens"),
        ("Planification des examens", "Calendrier"),
        ("Messages directs", "Messages"),
        ("Contact", "Contact"),
        ("Contact et support", "Support"),
    ]
    user_role = st.session_state.get("platform_user_role", "student")
    if user_role == "prof":
        pages = [
            ("Accueil", "Accueil"),
            ("Espace professeur", "Professeurs"),
            ("Messages directs", "Messages"),
            ("Contact et support", "Support"),
        ]
    elif user_role == "admin":
        pages = [
            ("Accueil", "Accueil"),
            ("Cours", "Cours"),
            ("Fichiers partages", "Fichiers Drive"),
            ("Examens nationaux", "Examens"),
            ("Planification des examens", "Calendrier"),
            ("Espace professeur", "Professeurs"),
            ("Espace direction", "Direction"),
            ("Utilisateurs", "Utilisateurs"),
            ("Messages directs", "Messages"),
            ("Contact et support", "Support"),
        ]
    elif user_role == "direction":
        pages = [
            ("Accueil", "Accueil"),
            ("Espace direction", "Direction"),
            ("Messages directs", "Messages"),
            ("Contact et support", "Support"),
        ]
    else:
        pages = list(student_pages)

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Accueil"
    allowed_pages = [page_name for page_name, _ in pages] + ["Historique des nouveautes"]
    if st.session_state.current_page not in allowed_pages:
        st.session_state.current_page = "Accueil"

    st.sidebar.markdown("### BTS SMARTCAMPUS")
    st.sidebar.caption("Navigation")

    for page_name, label in pages:
        is_active = st.session_state.current_page == page_name
        button_label = f"  {label}" if is_active else f"  {label}"
        if st.sidebar.button(
            button_label,
            key=f"nav_{page_name}",
            width="stretch",
            type="primary" if is_active else "secondary",
        ):
            st.session_state.current_page = page_name
            st.rerun()

    return st.session_state.current_page


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="SC", layout="wide")
    inject_style()
    data = load_data()

    if "platform_logged_in" not in st.session_state:
        st.session_state.platform_logged_in = False
    if "platform_user_label" not in st.session_state:
        st.session_state.platform_user_label = "Etudiant"
    if "platform_user_email" not in st.session_state:
        st.session_state.platform_user_email = ""
    if "platform_user_role" not in st.session_state:
        st.session_state.platform_user_role = "student"
    if "login_transition" not in st.session_state:
        st.session_state.login_transition = False
    if "platform_started" not in st.session_state:
        st.session_state.platform_started = False
    if "entry_animation" not in st.session_state:
        st.session_state.entry_animation = False

    if not st.session_state.platform_logged_in:
        show_platform_login(data)
        return

    if not st.session_state.platform_started:
        if st.session_state.login_transition:
            show_login_to_welcome_transition()
        show_welcome()
        return

    if st.session_state.entry_animation:
        show_entry_transition()

    page = sidebar_navigation()

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Connecte: {st.session_state.platform_user_label}")
    if st.sidebar.button("Se deconnecter", key="platform_logout"):
        st.session_state.platform_logged_in = False
        st.session_state.platform_started = False
        st.session_state.entry_animation = False
        st.session_state.login_transition = False
        st.session_state.platform_user_email = ""
        st.session_state.platform_user_role = "student"
        st.session_state.current_page = "Accueil"
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Les cours, examens et messages sont sauvegardes dans btsmtacademy_data.json."
    )

    st.markdown(f'<div class="page-transition" data-page="{page}">', unsafe_allow_html=True)
    if page == "Accueil":
        show_home(data)
    elif page == "Recherche rapide":
        show_search(data)
    elif page in ("Dernieres mises a jour", "Historique des nouveautes"):
        show_updates(data)
    elif page == "Cours":
        show_courses(data)
    elif page == "Examens nationaux":
        show_exams(data)
    elif page == "Planification des examens":
        show_homework_plan(data)
    elif page == "Fichiers partages":
        show_shared_files(data)
    elif page == "Espace professeur":
        show_prof_space(data)
    elif page == "Espace direction":
        show_direction_space(data)
    elif page == "Utilisateurs":
        user_management_admin(data)
    elif page == "Messages directs":
        show_direct_messages(data)
    elif page == "Contact et support":
        show_support(data)
    else:
        show_contact(data)

    show_creator_footer()
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
