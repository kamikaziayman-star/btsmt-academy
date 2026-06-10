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
import textwrap
import urllib.error
import urllib.request
import uuid
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
COURSE_STATUS = ["Disponible", "À réviser", "Corrigé ajouté", "Mis à jour"]
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


def generate_temporary_password(length=10):
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))

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
        "subject": "Toutes les matières",
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
        "seen_dashboard": {},
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
                "titre": "Examens nationaux précédents",
                "matiere": "Toutes les matières",
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
        message.setdefault("date", "Date non indiquée")
        message.setdefault("important", False)
        for field in ("titre", "prof", "contenu"):
            message[field] = normalize_brand_text(message.get(field, ""))

    for subject in SUBJECTS:
        data.setdefault("cours", {}).setdefault(subject, [])
        for resource in data["cours"][subject]:
            resource.setdefault("type", "Cours")
            resource.setdefault("statut", "Disponible")
            resource.setdefault("date", "Date non indiquée")
            resource.setdefault("prof", "Administration")
            resource.setdefault("source", "drive")
            resource.setdefault("path", "")
            resource.setdefault("filename", "")
            resource.setdefault("mime", "")
            for field in ("titre", "description", "prof"):
                resource[field] = normalize_brand_text(resource.get(field, ""))

    for exam in data.get("examens", []):
        exam.setdefault("session", "Archive")
        exam.setdefault("corrige_url", "")
        exam.setdefault("date", "Date non indiquée")

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
        account.setdefault("created_at", "Date non indiquée")
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
        devoir.setdefault("date_publication", "Date non indiquée")
        for field in ("titre", "description", "prof"):
            devoir[field] = normalize_brand_text(devoir.get(field, ""))

    data.setdefault("shared_files", [])
    for shared_file in data["shared_files"]:
        shared_file.setdefault("titre", "Fichier partage")
        shared_file.setdefault("description", "")
        shared_file.setdefault("matiere", "Toutes les matières")
        shared_file.setdefault("auteur", "Administration")
        shared_file.setdefault("role", "direction")
        shared_file.setdefault("date", "Date non indiquée")
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
        contact.setdefault("date", "Date non indiquée")
        contact.setdefault("reponse", "")
        contact.setdefault("date_reponse", "")

    data.setdefault("support_tickets", [])
    for ticket in data["support_tickets"]:
        ticket.setdefault("type", "Réclamation")
        ticket.setdefault("nom", "")
        ticket.setdefault("email", "")
        ticket.setdefault("role", "Utilisateur")
        ticket.setdefault("sujet", "")
        ticket.setdefault("message", "")
        ticket.setdefault("date", "Date non indiquée")
        ticket.setdefault("statut", "Nouveau")
        ticket.setdefault("reponse", "")
        ticket.setdefault("date_reponse", "")
        ticket.setdefault("screenshot_path", "")
        ticket.setdefault("screenshot_name", "")
        ticket.setdefault("screenshot_mime", "")
        if ticket.get("statut") == "Traite":
            ticket["statut"] = "Traité"
        for field in ("sujet", "message", "reponse"):
            ticket[field] = normalize_brand_text(ticket.get(field, ""))

    data.setdefault("seen_updates", {})
    data.setdefault("seen_dashboard", {})

    data.setdefault("direct_messages", [])
    for message in data["direct_messages"]:
        message.setdefault("from_email", ADMIN_EMAIL)
        message.setdefault("from_name", "Administration BTS SMARTCAMPUS")
        message.setdefault("to_email", "")
        message.setdefault("to_name", "")
        message.setdefault("titre", "Message")
        message.setdefault("contenu", "")
        message.setdefault("date", "Date non indiquée")
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
        try:
            backup_data_file()
        except OSError:
            pass
    save_data_to_database(data)
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError:
        # The JSON file can be locked by the host or by another local process.
        # The database/Supabase write above is durable, so keep the app running.
        return


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
                        <span>Matière : {shared_file.get("matiere", "Toutes les matières")}</span>
                        <span>Publié par: {role_label}</span>
                        <span>Date: {shared_file.get("date", "Date non indiquée")}</span>
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


def shared_file_extension(shared_file):
    file_name = str(shared_file.get("filename") or shared_file.get("titre") or "fichier.pdf")
    suffix = Path(file_name).suffix.replace(".", "").upper()
    if suffix:
        return suffix[:4]
    mime = str(shared_file.get("mime", "")).lower()
    if "pdf" in mime:
        return "PDF"
    if "word" in mime or "document" in mime:
        return "DOCX"
    if "excel" in mime or "spreadsheet" in mime:
        return "XLSX"
    if "powerpoint" in mime or "presentation" in mime:
        return "PPTX"
    if "image" in mime:
        return "IMG"
    return "FILE"


def shared_file_size(path):
    try:
        size = path.stat().st_size
    except OSError:
        return ""
    units = ["o", "Ko", "Mo", "Go"]
    value = float(size)
    unit = units[0]
    for unit in units:
        if value < 1024 or unit == units[-1]:
            break
        value /= 1024
    if unit == "o":
        return f"{int(value)} {unit}"
    return f"{value:.1f} {unit}"


def render_shared_file_preview(shared_file, key):
    path = Path(shared_file.get("path", ""))
    if not path.exists() or not path.is_file():
        st.warning("Le fichier n'existe plus dans le dossier local.")
        return

    mime = shared_file.get("mime", "application/octet-stream")
    if mime.startswith("image/"):
        st.image(str(path), width="stretch")
        return

    if mime == "application/pdf" or path.suffix.lower() == ".pdf":
        encoded_pdf = base64.b64encode(path.read_bytes()).decode("ascii")
        st.markdown(
            f"""
            <iframe class="shared-file-preview-frame"
                src="data:application/pdf;base64,{encoded_pdf}">
            </iframe>
            """,
            unsafe_allow_html=True,
        )
        return

    if mime.startswith("text/") or path.suffix.lower() in {".txt", ".csv", ".md"}:
        try:
            st.text_area(
                "Aperçu du fichier",
                path.read_text(encoding="utf-8", errors="replace")[:6000],
                height=260,
                key=f"preview_text_{key}",
            )
        except OSError:
            st.warning("Impossible de lire ce fichier.")
        return

    st.info("Aperçu non disponible pour ce type de fichier. Utilisez le bouton Télécharger.")


def render_local_attachment(path_value, file_name="", mime="application/octet-stream", key_prefix="attachment"):
    raw_path = str(path_value or "").strip()
    if not raw_path or raw_path in {".", "./", "/", "\\"}:
        return

    path = Path(raw_path)
    if not path.exists() or not path.is_file():
        st.info("Pièce jointe indisponible sur ce serveur.")
        return

    try:
        attachment_bytes = path.read_bytes()
    except (OSError, IsADirectoryError, PermissionError):
        st.info("Pièce jointe indisponible sur ce serveur.")
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
            "Si le problème continue, envoyez cette conversation à l'admin : il pourra vérifier votre compte ou changer le mot de passe."
        )
    if any(word in text for word in course_words):
        return (
            "Pour un cours ou un lien Drive, indiquez la matiere et le nom du cours. "
            "Si le lien ne s'ouvre pas, l'admin/professeur pourra le corriger après réception de votre réclamation."
        )
    if any(word in text for word in account_words):
        return (
            "Pour un compte ou une validation, votre demande doit etre traitee par l'administration. "
            "Envoyez cette conversation à l'admin avec votre nom, votre email et votre groupe."
        )
    if any(word in text for word in exam_words):
        return (
            "Pour les examens ou la planification, verifiez d'abord l'onglet Calendrier et Examens. "
            "Si une date ou un fichier manque, envoyez la conversation à l'admin."
        )
    if any(word in text for word in bug_words):
        return (
            "D'accord. Decrivez ce qui ne marche pas, la page concernee et le moment exact du probleme. "
            "Une capture est utile mais pas obligatoire. Vous pouvez envoyer cette conversation au support."
        )
    return (
        "Merci pour votre message. Je peux vous aider en darija, francais ou anglais. "
        "Expliquez le problème avec plus de détails, puis envoyez la conversation à l'admin si vous voulez une intervention."
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
            placeholder="Exemple: ma kaykhdemch lien dyal cours marketing / je n'arrive pas à ouvrir le PDF...",
            key="support_bot_input",
        )
        send_bot_message = st.form_submit_button("Envoyer à l'assistant")

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
    if col_send.button("Envoyer cette conversation à l'admin", key="send_support_bot_to_admin"):
        transcript = support_bot_transcript(st.session_state.support_bot_messages)
        if not any(message.get("role") == "user" for message in st.session_state.support_bot_messages):
            st.error("Discutez d'abord avec l'assistant avant d'envoyer à l'admin.")
        else:
            data.setdefault("support_tickets", []).insert(
                0,
                {
                    "type": "Assistant support",
                    "nom": user_label or "Utilisateur",
                    "email": user_email,
                    "role": user_role,
                    "sujet": "Conversation envoyée depuis l'assistant support",
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
            st.success("Conversation envoyée à l'admin.")
            st.session_state.support_bot_messages = [
                {
                    "role": "assistant",
                    "content": "Votre conversation a été envoyée. Vous pouvez commencer une nouvelle demande si besoin.",
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
            "name": "Compte étudiant général",
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


def item_update_date(item):
    return (
        item.get("date")
        or item.get("date_publication")
        or item.get("date_limite")
        or "Date non indiquée"
    )


def latest_updates(data, limit=8):
    items = []
    for item in all_course_items(data):
        items.append({**item, "_update_category": "courses", "_update_label": "Cours"})
    for message in data.get("messages", []):
        items.append(
            {
                **message,
                "type": "Message",
                "statut": "Publie",
                "_update_category": "messages",
                "_update_label": "Message",
            }
        )
    for shared_file in data.get("shared_files", []):
        items.append(
            {
                **shared_file,
                "type": "Fichier",
                "statut": "Partage",
                "url": shared_file.get("path", ""),
                "_update_category": "files",
                "_update_label": "Fichier",
            }
        )
    for devoir in data.get("devoirs", []):
        items.append(
            {
                **devoir,
                "titre": devoir.get("titre") or f"Examen - {devoir.get('matiere', 'General')}",
                "date": devoir.get("date_publication") or devoir.get("date_limite", ""),
                "type": "Planning",
                "statut": "Planifie",
                "_update_category": "planning",
                "_update_label": "Planning",
            }
        )
    for exam in data.get("examens", []):
        items.append(
            {
                **exam,
                "type": "Examen",
                "statut": exam.get("session", "Disponible"),
                "_update_category": "exams",
                "_update_label": "Examen",
            }
        )
    return sorted(items, key=lambda item: parse_date(item_update_date(item)), reverse=True)[:limit]


def recent_update_items(data, days=7, limit=50):
    items = [item for item in latest_updates(data, limit=200) if is_new(item_update_date(item), days=days)]
    return sorted(items, key=lambda item: parse_date(item_update_date(item)), reverse=True)[:limit]


def update_identity(item):
    parts = [
        item.get("_update_category", ""),
        item.get("matiere", ""),
        item.get("titre", ""),
        item.get("type", ""),
        item.get("statut", ""),
        item.get("date", ""),
        item.get("date_limite", ""),
        item.get("date_publication", ""),
        item.get("url", ""),
        item.get("path", ""),
        item.get("filename", ""),
        item.get("prof", ""),
        item.get("auteur", ""),
        item.get("contenu", ""),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def current_user_key():
    email = st.session_state.get("platform_user_email", "").strip().lower()
    role = st.session_state.get("platform_user_role", "student")
    return email or f"session-{role}"


def seen_update_ids(data):
    seen = data.setdefault("seen_updates", {})
    key = current_user_key()
    persisted_seen = set(seen.setdefault(key, []))
    session_seen_store = st.session_state.setdefault("seen_updates_session", {})
    session_seen = set(session_seen_store.setdefault(key, []))
    return persisted_seen | session_seen


def unread_updates(data, limit=4):
    seen_ids = seen_update_ids(data)
    items = recent_update_items(data, days=7, limit=50)
    return [item for item in items if update_identity(item) not in seen_ids][:limit]


def mark_updates_seen(data, items):
    if not items:
        return
    seen = data.setdefault("seen_updates", {})
    key = current_user_key()
    session_seen_store = st.session_state.setdefault("seen_updates_session", {})
    session_seen = set(session_seen_store.setdefault(key, []))
    current_seen = set(seen.setdefault(key, []))
    current_seen.update(session_seen)
    before = len(current_seen)
    current_seen.update(update_identity(item) for item in items)
    session_seen_store[key] = sorted(current_seen)
    if len(current_seen) != before:
        seen[key] = sorted(current_seen)
        save_data(data)


def dashboard_item_identity(category, item):
    fields = [
        category,
        item.get("titre", ""),
        item.get("matiere", ""),
        item.get("date", ""),
        item.get("date_limite", ""),
        item.get("url", ""),
        item.get("filename", ""),
        item.get("auteur", ""),
        item.get("prof", ""),
        item.get("contenu", ""),
        item.get("message", ""),
    ]
    return hashlib.sha256("|".join(str(field) for field in fields).encode("utf-8")).hexdigest()


def seen_dashboard_ids(data, category):
    seen = data.setdefault("seen_dashboard", {})
    user_seen = seen.setdefault(current_user_key(), {})
    persisted_seen = set(user_seen.setdefault(category, []))
    session_store = st.session_state.setdefault("seen_dashboard_session", {})
    session_user_seen = session_store.setdefault(current_user_key(), {})
    session_seen = set(session_user_seen.setdefault(category, []))
    return persisted_seen | session_seen


def unseen_dashboard_items(data, category, items, limit=None):
    seen_ids = seen_dashboard_ids(data, category)
    unseen = [item for item in items if dashboard_item_identity(category, item) not in seen_ids]
    return unseen[:limit] if limit else unseen


def mark_dashboard_items_seen(data, category, items):
    if not items:
        return
    seen = data.setdefault("seen_dashboard", {})
    key = current_user_key()
    user_seen = seen.setdefault(key, {})
    session_store = st.session_state.setdefault("seen_dashboard_session", {})
    session_user_seen = session_store.setdefault(key, {})
    current_seen = set(user_seen.setdefault(category, []))
    current_seen.update(session_user_seen.setdefault(category, []))
    before = len(current_seen)
    current_seen.update(dashboard_item_identity(category, item) for item in items)
    session_user_seen[category] = sorted(current_seen)
    if len(current_seen) != before:
        user_seen[category] = sorted(current_seen)
        save_data(data)


def mark_many_dashboard_items_seen(data, grouped_items):
    changed = False
    seen = data.setdefault("seen_dashboard", {})
    key = current_user_key()
    user_seen = seen.setdefault(key, {})
    session_store = st.session_state.setdefault("seen_dashboard_session", {})
    session_user_seen = session_store.setdefault(key, {})

    for category, items in grouped_items.items():
        if not items:
            continue
        current_seen = set(user_seen.setdefault(category, []))
        current_seen.update(session_user_seen.setdefault(category, []))
        before = len(current_seen)
        current_seen.update(dashboard_item_identity(category, item) for item in items)
        session_user_seen[category] = sorted(current_seen)
        if len(current_seen) != before:
            user_seen[category] = sorted(current_seen)
            changed = True

    if changed:
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
        return "Date non indiquée"

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
    st.info(f"Date sélectionnée : {format_exam_date(selected_date)}")
    return selected_date


def inject_style():
    style_path = Path(__file__).resolve().parent / "assets" / "styles.css"
    final_css = ""

    if style_path.exists():
        final_css = style_path.read_text(encoding="utf-8")
    else:
        try:
            from embedded_styles import get_embedded_styles

            final_css = get_embedded_styles()
        except Exception:
            final_css = ""

    if final_css:
        st.markdown(
            "<style>\n" + final_css + "\n</style>",
            unsafe_allow_html=True,
        )

def show_header(data=None):
    user_label = st.session_state.get("platform_user_label", "Etudiant")
    initial = (user_label.strip()[:1] or "A").upper()
    st.markdown(
        f"""
        <div class="academic-dashboard-userbar">
            <div></div>
            <div class="academic-dashboard-user">
                <span>Bonjour,<strong>{html.escape(user_label)}</strong></span>
                <b>{html.escape(initial)}</b>
            </div>
        </div>
        <div class="academic-dashboard-hero">
            <div>
                <h1>Bienvenue sur<br>BTS <span>SMARTCAMPUS</span></h1>
                <div class="dashboard-gold-line"></div>
                <p>
                    Plateforme académique moderne pour centraliser les cours,
                    les ressources, les examens et les communications.
                </p>
            </div>
            <div class="academic-dashboard-illustration">
                <div class="dash-cap"></div>
                <div class="dash-books"></div>
                <div class="dash-screen"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dashboard_feature_card(icon, title, text):
    st.markdown(
        f"""
        <div class="university-feature-card">
            <div class="university-feature-icon">{icon}</div>
            <div>
                <h3>{title}</h3>
                <p>{text}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dashboard_announcement(data, admin_messages):
    message_text = "Réunion pédagogique le 15 mai a 10h en salle 204."
    if admin_messages:
        latest_message = sorted(admin_messages, key=lambda item: parse_date(item.get("date")), reverse=True)[0]
        message_text = latest_message.get("contenu") or latest_message.get("titre", message_text)
    elif data.get("messages"):
        latest_message = sorted(data["messages"], key=lambda item: parse_date(item.get("date")), reverse=True)[0]
        message_text = latest_message.get("titre", message_text)

    st.markdown(
        f"""
        <div class="university-announcement">
            <div class="university-announcement-icon">i</div>
            <div>
                <strong>Annonces importantes</strong>
                <p>{message_text}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_legacy_header(data=None):
    user_label = st.session_state.get("platform_user_label", "Etudiant")
    initial = (user_label.strip()[:1] or "A").upper()
    st.markdown(
        f"""
        <div class="academic-dashboard-topbar">
            <div class="academic-dashboard-brand">BTS <span>SMART</span> CAMPUS</div>
            <div class="academic-dashboard-user">
                <span>Bonjour, {user_label}</span>
                <strong>{initial}</strong>
            </div>
        </div>
        <div class="academic-dashboard-hero">
            <div>
                <h1>Bienvenue sur<br><span>BTS SMARTCAMPUS</span></h1>
                <p>
                    Plateforme pour centraliser les cours, les fiches Drive, les examens
                    nationaux précédents et les messages destinés aux étudiants.
                </p>
            </div>
            <div class="academic-dashboard-illustration">
                <div class="dash-cap"></div>
                <div class="dash-books"></div>
                <div class="dash-screen"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_creator_footer():
    st.markdown(
        """
        <div class="creator-footer">
            Plateforme créée par <strong>Ayman Marzagui</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dashboard_empty_card(icon, message):
    st.markdown(
        f"""
        <div class="academic-empty-card">
            <span>{icon}</span>
            <strong>{message}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dashboard_section_title(icon, title):
    st.markdown(
        f"""
        <div class="academic-section-title">
            <span>{icon}</span>
            <h3>{title}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_academic_page_header(title, subtitle, icon="SC"):
    st.markdown(
        f"""
        <div class="synced-page-hero">
            <div class="synced-page-icon">{icon}</div>
            <div>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_usage_guide(title, steps):
    with st.expander(f"Guide rapide - {title}", expanded=False):
        for index, step in enumerate(steps, start=1):
            st.markdown(f"**{index}.** {step}")


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
        return False, "Un compte étudiant existe déjà avec cet email."
    if clean_email in data.get("prof_accounts", {}) or clean_email in (DIRECTION_EMAIL.lower(), ADMIN_EMAIL.lower()):
        return False, "Cet email est réservé à l'administration."

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
    return True, "Votre demande a été envoyée. La direction doit valider votre compte."


def show_platform_login(data):
    st.markdown(
        """
        <div class="platform-login-shell">
            <div class="platform-login-top">
                <div class="platform-login-brand">
                    <span class="platform-login-crest">BTS</span>
                    <span class="platform-login-brand-text">BTS SMARTCAMPUS</span>
                </div>
                <div class="platform-login-actions">
                    <div class="platform-login-pill">Accès sécurisé à la plateforme</div>
                    <div class="platform-login-help">?</div>
                </div>
            </div>
            <div class="platform-login-hero">
                <div class="platform-login-copy">
                    <h1>Connectez-vous à<br><span>BTS SMARTCAMPUS</span></h1>
                    <div class="platform-login-gold-line"></div>
                    <p>
                        Accédez à vos cours, examens, fichiers partagés, messages et planning
                        depuis un espace moderne pensé pour accompagner votre réussite.
                    </p>
                </div>
                <div class="platform-login-card">
                    <div class="platform-login-card-icon">▰</div>
                    <div class="platform-login-card-title">Connexion</div>
                    <div class="platform-login-card-line"></div>
                    <div class="platform-login-card-subtitle">Entrez vos identifiants pour continuer.</div>
        """,
        unsafe_allow_html=True,
    )

    submitted = False
    signup_submitted = False
    login_tab, signup_tab = st.tabs(["Connexion", "Inscription étudiant"])

    with login_tab:
        with st.form("platform_login_form"):
            email = st.text_input("Email", placeholder="Entrez votre adresse email")
            password = st.text_input("Mot de passe", type="password", placeholder="Entrez votre mot de passe")
            submitted = st.form_submit_button("Accéder à la plateforme")

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
                        <span>Les nouveaux comptes étudiants doivent être validés par la direction.</span>
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
            st.session_state.login_transition = False
            st.success("Connexion réussie.")
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
                        BTS SMARTCAMPUS est une plateforme dédiée aux étudiants qui souhaitent réviser efficacement.
                        Vous y trouverez tous les cours, exercices corrigés et examens des années
                        précédentes, organisés et accessibles en un seul endroit. Un espace simple,
                        moderne et complet pour accompagner votre réussite tout au long de l'année.
                    </p>
                    <div class="welcome-feature-row">
                        <span class="welcome-feature"><b>▣</b>Cours de qualité</span>
                        <span class="welcome-feature"><b>◌</b>Ressources Drive</span>
                        <span class="welcome-feature"><b>☆</b>Examens précédents</span>
                    </div>
                </div>
                <div class="welcome-visual">
                    <div class="welcome-mini-card mini-cours">
                        <strong>12+</strong>
                        <span>Matières organisées</span>
                    </div>
                    <div class="welcome-mini-card mini-examens">
                        <strong>PDF</strong>
                        <span>Cours et fiches Drive</span>
                    </div>
                    <div class="welcome-mini-card mini-drive">
                        <strong>Exam</strong>
                        <span>Préparation nationale</span>
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

    st.markdown('<div class="welcome-start-panel"><div><strong>Commencer maintenant</strong><span>Accédez à tous vos cours, ressources et outils en un clic.</span></div></div>', unsafe_allow_html=True)
    if st.button("Commencer maintenant", width="stretch"):
        st.session_state.platform_started = True
        st.session_state.dashboard_transition_once = True
        st.session_state.entry_animation = False
        st.session_state.login_transition = False
        st.session_state.current_page = "Accueil"
        st.rerun()
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


def show_welcome_academic():
    st.markdown(
        """
        <div class="welcome-shell academic-welcome-shell">
            <div class="welcome-topbar academic-welcome-topbar">
                <div class="welcome-brand academic-welcome-brand">
                    <span class="welcome-brand-mark academic-welcome-crest">BTS</span>
                    <span class="welcome-brand-text">
                        <span class="welcome-brand-main">BTS <span class="brand-blue">SMART</span>CAMPUS</span>
                        <span class="welcome-brand-sub">PLATEFORME ACADEMIQUE</span>
                    </span>
                </div>
            </div>
            <div class="academic-welcome-panel">
                <div class="welcome-copy academic-welcome-copy">
                    <div class="welcome-eyebrow">PLATEFORME DE REVISION INTELLIGENTE</div>
                    <h1>Bienvenue sur<br>BTS <span>SMARTCAMPUS</span></h1>
                    <div class="welcome-gold-line"></div>
                    <p>
                        BTS SMARTCAMPUS est une plateforme dédiée aux étudiants qui souhaitent réviser efficacement.
                        Vous y trouverez tous les cours, exercices corrigés et examens des années
                        précédentes, organisés et accessibles en un seul endroit. Un espace simple,
                        moderne et complet pour accompagner votre réussite tout au long de l'année.
                    </p>
                    <div class="welcome-feature-row">
                        <span class="welcome-feature"><b>II</b>Cours de qualité</span>
                        <span class="welcome-feature"><b>[]</b>Ressources Drive</span>
                        <span class="welcome-feature"><b>*</b>Examens précédents</span>
                    </div>
                </div>
                <div class="welcome-visual academic-welcome-grid">
                    <div class="welcome-mini-card mini-cours">
                        <strong>PDF</strong>
                        <span><b>Matières organisées</b>Tous vos cours classés par matière.</span>
                    </div>
                    <div class="welcome-mini-card mini-examens">
                        <strong>PDF</strong>
                        <span><b>Cours et fiches Drive</b>Accédez aux cours et aux fiches partagées.</span>
                    </div>
                    <div class="welcome-mini-card mini-drive">
                        <strong>Exam</strong>
                        <span><b>Examens</b>Préparation nationale, sujets et annales corrigés.</span>
                    </div>
                    <div class="welcome-mini-card mini-profs">
                        <strong>Prof</strong>
                        <span><b>Professeurs</b>Messages et échanges avec vos enseignants.</span>
                    </div>
                    <div class="welcome-floating-badge">BTS</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="welcome-start-panel academic-welcome-start-panel"><div><strong>Commencer maintenant</strong><span>Accédez à tous vos cours, ressources et outils en un clic.</span></div></div>', unsafe_allow_html=True)
    if st.button("Accéder à la plateforme ->", width="stretch"):
        st.session_state.platform_started = True
        st.session_state.dashboard_transition_once = True
        st.session_state.entry_animation = False
        st.session_state.login_transition = False
        st.session_state.current_page = "Accueil"
        st.rerun()
    st.markdown(
        """
        <div class="welcome-tags-outside academic-welcome-links">
            <span class="welcome-tag tag-academy"><b>SMART CAMPUS</b><small>Accueil et actualités</small></span>
            <span class="welcome-tag tag-ressources"><b>RESSOURCES</b><small>Cours et documents</small></span>
            <span class="welcome-tag tag-examens"><b>EXAMENS</b><small>Annales et corrigés</small></span>
            <span class="welcome-tag tag-direction"><b>DIRECTION</b><small>Informations et annonces</small></span>
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
                <p>Connexion réussie. Préparation de votre espace...</p>
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
    if resource.get("source") == "upload" or resource.get("path"):
        render_local_attachment(
            resource.get("path", ""),
            resource.get("filename", ""),
            resource.get("mime", "application/octet-stream"),
            key_prefix=f"course_card_{resource.get('_id', resource.get('titre', 'resource'))}",
        )
    else:
        st.link_button("Ouvrir le lien Drive", resource.get("url", "https://drive.google.com/"))


def show_home(data):
    show_header(data)
    show_usage_guide(
        "Accueil",
        [
            "Consultez les statistiques pour voir rapidement les cours, examens, ressources et nouveautés.",
            "Ouvrez les blocs du dashboard pour suivre les derniers messages, fichiers et examens.",
            "Utilisez le bouton Historique des nouveautés pour revoir les publications déjà lues.",
        ],
    )
    current_email = st.session_state.get("platform_user_email", "")
    student_account = data.get("student_accounts", {}).get(current_email)
    admin_messages = []
    if student_account:
        admin_messages = student_account.get("admin_messages", [])

    total_courses = sum(len(resources) for resources in data["cours"].values())
    dashboard_updates = unread_updates(data, limit=4)
    unread_total = len(unread_updates(data, limit=50))
    total_files = len(data.get("shared_files", []))
    total_exams = len(data.get("examens", []))

    planned_exams = [
        devoir
        for devoir in data.get("devoirs", [])
        if devoir.get("date_limite") and not is_weekend_date(devoir.get("date_limite"))
    ]
    planned_exams = sorted(
        planned_exams,
        key=lambda devoir: parse_deadline(devoir.get("date_limite")),
    )
    planned_exams = unseen_dashboard_items(data, "planning", planned_exams, limit=6)

    recent_files = sorted(
        data.get("shared_files", []),
        key=lambda shared_file: parse_date(shared_file.get("date")),
        reverse=True,
    )
    recent_files = unseen_dashboard_items(data, "files", recent_files, limit=4)

    messages = sorted(
        data["messages"],
        key=lambda message: (message.get("important", False), parse_date(message.get("date"))),
        reverse=True,
    )
    messages = unseen_dashboard_items(data, "messages", messages, limit=5)

    def clean(value, fallback=""):
        return html.escape(str(value or fallback))

    def short_date(value):
        parsed = parse_date(value)
        if parsed.year <= 1901:
            return clean(value, "")
        return parsed.strftime("%d/%m")

    exam_rows = []
    for devoir in planned_exams[:3]:
        title = clean(devoir.get("titre") or devoir.get("matiere"), "Examen")
        subject = clean(devoir.get("matiere"), "Session")
        deadline = short_date(devoir.get("date_limite"))
        day, month = ("--", "")
        if "/" in deadline:
            day, month = deadline.split("/", 1)
        exam_rows.append(
            f'<div class="dash-list-row dash-exam-row"><div><strong>{title}</strong>'
            f'<small>{subject}</small></div><time><b>{day}</b><span>{month}</span></time></div>'
        )
    if not exam_rows:
        exam_rows.append('<div class="dash-empty-row">Aucun nouvel examen planifié à afficher.</div>')

    file_rows = []
    for item in recent_files[:3]:
        title = clean(item.get("titre") or item.get("name"), "Ressource")
        subject = clean(item.get("matiere") or item.get("subject"), "General")
        ext = clean((Path(str(item.get("file_name", item.get("titre", "PDF")))).suffix or ".pdf").replace(".", "").upper(), "PDF")
        file_rows.append(
            f'<div class="dash-list-row dash-file-row"><span class="dash-file-badge">{ext[:3]}</span>'
            f'<div><strong>{title}</strong><small>{subject}</small></div>'
            f'<em>{clean(item.get("taille") or item.get("size"), "")}</em></div>'
        )
    if not file_rows:
        file_rows.append('<div class="dash-empty-row">Aucune nouvelle ressource partagée.</div>')

    announcement_rows = []
    source_messages = admin_messages or data.get("messages", [])
    for item in sorted(source_messages, key=lambda row: parse_date(row.get("date")), reverse=True)[:3]:
        title = clean(item.get("titre"), "Annonce")
        text = clean(item.get("contenu") or item.get("message"), "")
        date = short_date(item.get("date"))
        announcement_rows.append(
            f'<div class="dash-list-row dash-announcement-row"><div><strong>{title}</strong>'
            f'<small>{text}</small></div><em>{date}</em></div>'
        )
    if not announcement_rows:
        announcement_rows.append('<div class="dash-empty-row">Aucune annonce récente à afficher.</div>')

    message_rows = []
    for item in messages[:3]:
        author = clean(item.get("prof") or item.get("auteur") or item.get("sender") or item.get("titre"), "Direction")
        text = clean(item.get("contenu") or item.get("message") or item.get("titre"), "")
        initials = "".join(part[:1] for part in author.split()[:2]).upper()[:2] or "BT"
        message_rows.append(
            f'<div class="dash-list-row dash-message-row"><span>{clean(initials)}</span>'
            f'<div><strong>{author}</strong><small>{text}</small></div>'
            f'<em>{short_date(item.get("date"))}</em></div>'
        )
    if not message_rows:
        message_rows.append('<div class="dash-empty-row">Aucun nouveau message à afficher.</div>')

    fixed_dashboard_html = textwrap.dedent(f"""
    <div class="dashboard-stat-grid">
        <div class="dashboard-stat stat-blue">
            <div class="stat-icon">▤</div>
            <div class="label">Matières</div>
            <div class="value">{total_courses}</div>
            <div class="hint">Cours disponibles</div>
        </div>
        <div class="dashboard-stat stat-teal">
            <div class="stat-icon">◇</div>
            <div class="label">Examens</div>
            <div class="value">{total_exams}</div>
            <div class="hint">À venir</div>
        </div>
        <div class="dashboard-stat stat-amber">
            <div class="stat-icon">▣</div>
            <div class="label">Ressources</div>
            <div class="value">{total_files}</div>
            <div class="hint">Fichiers disponibles</div>
        </div>
        <div class="dashboard-stat stat-violet">
            <div class="stat-icon">!</div>
            <div class="label">Événements</div>
            <div class="value">{unread_total}</div>
            <div class="hint">Nouveautés</div>
        </div>
    </div>
    <div class="dashboard-list-grid">
        <div class="dash-panel">
            <h3><span>◇</span>Examens à venir</h3>
            {''.join(exam_rows)}
        </div>
        <div class="dash-panel">
            <h3><span>▣</span>Ressources récentes</h3>
            {''.join(file_rows)}
        </div>
        <div class="dash-panel">
            <h3><span>!</span>Annonces</h3>
            {''.join(announcement_rows)}
        </div>
        <div class="dash-panel">
            <h3><span>✉</span>Messages étudiants</h3>
            {''.join(message_rows)}
        </div>
    </div>
    """).strip()
    st.markdown(fixed_dashboard_html, unsafe_allow_html=True)

    dashboard_actions = st.columns([1, 1, 1], gap="medium")
    with dashboard_actions[0]:
        if st.button("Historique des nouveautés", key="open_dashboard_updates", width="stretch"):
            st.session_state.current_page = "Dernières mises à jour"
            st.rerun()

    if unread_total or planned_exams or recent_files or messages:
        with dashboard_actions[1]:
            if st.button("Marquer les nouveautés comme vues", key="mark_all_dashboard_news_seen", width="stretch"):
                mark_updates_seen(data, unread_updates(data, limit=100))
                mark_many_dashboard_items_seen(
                    data,
                    {
                        "planning": planned_exams,
                        "files": recent_files,
                        "messages": messages,
                    },
                )
                st.success("Toutes les nouveautés visibles sont marquées comme vues.")
                st.rerun()

    if st.session_state.get("platform_user_role") == "admin":
        with dashboard_actions[2]:
            if st.button("Réinitialiser les lectures", key="reset_seen_updates_admin", width="stretch"):
                seen = data.setdefault("seen_updates", {})
                seen.pop(current_user_key(), None)
                data.setdefault("seen_dashboard", {}).pop(current_user_key(), None)
                st.session_state.setdefault("seen_updates_session", {}).pop(current_user_key(), None)
                st.session_state.setdefault("seen_dashboard_session", {}).pop(current_user_key(), None)
                save_data(data)
                st.success("Lectures réinitialisées pour votre compte.")
                st.rerun()

    return


def show_courses(data):
    if "selected_course_subject" not in st.session_state:
        st.session_state.selected_course_subject = None

    if st.session_state.selected_course_subject is None:
        st.markdown(
            """
            <div class="courses-hero">
                <div>
                    <h1>Cours</h1>
                    <p>Choisissez une matière pour afficher la liste des cours disponibles.</p>
                </div>
                <div class="courses-hero-art"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        show_usage_guide(
            "Cours",
            [
                "Choisissez une matière pour afficher ses cours et ressources.",
                "Utilisez les filtres pour afficher uniquement les cours, exercices, corrections ou fiches.",
                "Les ressources peuvent être ouvertes par lien Drive ou téléchargées si elles ont été ajoutées comme fichier.",
            ],
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
                            <div class="subject-action">Accéder aux ressources</div>
                            <div class="subject-label">{theme['label']}</div>
                        </div>
                        <div class="subject-card-button-space"></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Ouvrir cette matière →", key=f"open_subject_{subject}", width="stretch"):
                    st.session_state.selected_course_subject = subject
                    st.rerun()
        return

    subject = st.session_state.selected_course_subject
    if st.button("Retour aux matières"):
        st.session_state.selected_course_subject = None
        st.rerun()

    st.subheader(subject)
    st.write("Cliquez sur un cours pour ouvrir son fichier ou son lien Drive.")

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
        st.info("Aucun cours publié pour cette matière.")
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
                <div class="muted">Ajouté par {resource.get("prof", "Administration")} | {resource.get("date", "Date non indiquée")}</div>
                <p>{resource.get("description", "")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if resource.get("source") == "upload" or resource.get("path"):
            render_local_attachment(
                resource.get("path", ""),
                resource.get("filename", ""),
                resource.get("mime", "application/octet-stream"),
                key_prefix=f"course_{subject}_{resource.get('_id', resource.get('titre', 'resource'))}",
            )
        else:
            st.link_button(
                "Ouvrir le lien du cours",
                resource.get("url", "https://drive.google.com/"),
                width="stretch",
            )


def show_search(data):
    show_academic_page_header(
        "Recherche rapide",
        "Retrouvez rapidement un cours, une fiche ou une ressource par mot-clé.",
        "R",
    )
    show_usage_guide(
        "Recherche",
        [
            "Tapez un mot-clé lié au cours, à la matière ou au type de ressource.",
            "Affinez les résultats avec les filtres Type et Statut.",
            "Ouvrez directement la ressource trouvée depuis la liste des résultats.",
        ],
    )
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
        st.info("Aucun résultat trouvé.")
        return

    for item in results:
        extra = f"{item.get('matiere')} | {item.get('date', 'Date non indiquée')}"
        show_resource_card(item, extra=extra)


def show_updates(data):
    st.markdown(
        """
        <div class="courses-hero">
            <div>
                <h1>Dernières nouveautés</h1>
                <p>Toutes les publications déjà affichées sur le dashboard restent disponibles ici.</p>
            </div>
            <div class="courses-hero-art"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    show_usage_guide(
        "Historique",
        [
            "Retrouvez ici toutes les publications déjà affichées sur le dashboard.",
            "Utilisez cette page pour revoir un cours, une annonce ou une ressource ancienne.",
            "Les nouveautés restent consultables même après les avoir marquées comme vues.",
        ],
    )

    items = latest_updates(data, limit=30)
    if not items:
        st.info("Aucune nouveauté pour le moment.")
        return

    for item in items:
        extra = (
            f"{item.get('_update_label', 'Nouveauté')} | {item.get('matiere', 'Général')} | "
            f"{item.get('type', '')} | {item.get('statut', '')} | "
            f"{item.get('prof') or item.get('auteur', '')} | {item_update_date(item)}"
        )
        show_resource_card(item, extra=extra)


def show_exams(data):
    st.markdown(
        """
        <div class="exam-page-shell">
            <div class="exam-hero">
                <div class="exam-icon-main">E</div>
                <div>
                    <h1>Examens nationaux précédents</h1>
                    <p>Consultez les anciens examens nationaux par matiere, annee et session.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    show_usage_guide(
        "Examens",
        [
            "Filtrez les anciens examens par matière, année et session.",
            "Ouvrez le lien Drive de l'examen pour consulter le sujet.",
            "Si un corrigé est disponible, utilisez le bouton Ouvrir le corrigé.",
        ],
    )

    col1, col2, col3 = st.columns(3)
    subject_filter = col1.selectbox("Filtrer par matière", ["Toutes les matières"] + SUBJECTS)
    years = sorted({exam.get("annee", "Archive") for exam in data["examens"]})
    year_filter = col2.selectbox("Année", ["Toutes"] + years)
    sessions = sorted({exam.get("session", "Archive") for exam in data["examens"]})
    session_filter = col3.selectbox("Session", ["Toutes"] + sessions)

    exams = data["examens"]
    if subject_filter != "Toutes les matières":
        exams = [
            exam
            for exam in exams
            if exam["matiere"] in (subject_filter, "Toutes les matières")
        ]
    if year_filter != "Toutes":
        exams = [exam for exam in exams if exam.get("annee") == year_filter]
    if session_filter != "Toutes":
        exams = [exam for exam in exams if exam.get("session") == session_filter]

    if not exams:
        st.info("Aucun examen trouvé pour cette matière.")

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
                                <span>{exam.get("matiere", "Toutes les matières")}</span>
                                <span>{exam.get("annee", "Archive")}</span>
                                <span>{exam.get("session", "Archive")}</span>
                                <span>{exam.get("date", "Date non indiquée")}</span>
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
                st.link_button("Ouvrir le corrigé", corrige_url)


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
    show_usage_guide(
        "Planning",
        [
            "Consultez les examens planifiés avec leur matière et leur date.",
            "Les dates de week-end sont masquées pour garder un planning clair.",
            "Les professeurs et l'administration peuvent ajouter ou supprimer les dates depuis leur espace.",
        ],
    )

    subject_filter = st.selectbox(
        "Filtrer par matière",
        ["Toutes les matières"] + SUBJECTS,
    )

    devoirs = data.get("devoirs", [])
    if subject_filter != "Toutes les matières":
        devoirs = [devoir for devoir in devoirs if devoir.get("matiere") == subject_filter]

    devoirs = [
        devoir for devoir in devoirs if not is_weekend_date(devoir.get("date_limite"))
    ]

    devoirs = sorted(devoirs, key=lambda devoir: parse_deadline(devoir.get("date_limite")))

    if not devoirs:
        st.markdown(
            """
            <div class="planning-empty">
                Aucun examen planifié pour le moment.
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
                        Date d'examen: <strong>{exam_date or "Non indiquée"}</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_shared_files(data):
    files_all = data.get("shared_files", [])
    professors = {
        shared_file.get("auteur", "Professeur")
        for shared_file in files_all
        if shared_file.get("role") != "direction"
    }
    st.markdown(
        """
        <div class="files-hero">
            <div class="files-title-wrap drive-title-wrap">
                <div class="files-icon drive-folder-icon">▰</div>
                <div>
                    <h1>Fichiers partagés</h1>
                    <div class="dashboard-gold-line"></div>
                    <p>Accédez aux documents, cours, PDF, Word, Excel et ressources partagés par les enseignants.</p>
                </div>
            </div>
            <div class="files-art"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    show_usage_guide(
        "Fichiers partagés",
        [
            "Utilisez les filtres pour retrouver un document par matière ou par auteur.",
            "Cliquez sur Télécharger pour récupérer un fichier disponible.",
            "Les images et PDF peuvent être prévisualisés quand le serveur contient encore le fichier.",
        ],
    )

    st.markdown(
        f"""
        <div class="drive-stat-grid">
            <div class="drive-stat-card stat-blue">
                <span>▤</span>
                <div><strong>{len(files_all)}</strong><b>Documents</b><small>fichiers disponibles</small></div>
            </div>
            <div class="drive-stat-card stat-teal">
                <span>▥</span>
                <div><strong>{len(SUBJECTS)}</strong><b>Matières</b><small>concernées</small></div>
            </div>
            <div class="drive-stat-card stat-amber">
                <span>◉</span>
                <div><strong>{max(len(professors), 1 if files_all else 0)}</strong><b>Professeurs</b><small>partageants</small></div>
            </div>
        </div>
        <div class="drive-filter-shell">
            <h3><span>≡</span>Filtres</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    subject_filter = col1.selectbox(
        "Filtrer par matière",
        ["Toutes les matières"] + SUBJECTS,
        key="drive_subject_filter",
    )
    source_filter = col2.selectbox(
        "Publié par",
        ["Tous les professeurs", "Direction", "Professeur"],
        key="drive_source_filter",
    )

    sort_filter = st.selectbox(
        "Trier par",
        ["Plus recents", "Plus anciens", "Titre A-Z"],
        key="drive_sort_filter",
    )

    files = list(files_all)
    if subject_filter != "Toutes les matières":
        files = [
            shared_file
            for shared_file in files
            if shared_file.get("matiere") in (subject_filter, "Toutes les matières")
        ]

    if source_filter != "Tous les professeurs":
        role = "direction" if source_filter == "Direction" else "prof"
        files = [shared_file for shared_file in files if shared_file.get("role") == role]

    if sort_filter == "Plus anciens":
        files = sorted(files, key=lambda shared_file: parse_date(shared_file.get("date")))
    elif sort_filter == "Titre A-Z":
        files = sorted(files, key=lambda shared_file: str(shared_file.get("titre", "")).lower())
    else:
        files = sorted(files, key=lambda shared_file: parse_date(shared_file.get("date")), reverse=True)

    if not files:
        st.info("Aucun fichier partagé pour le moment.")
        return

    st.markdown(
        f"""
        <div class="drive-list-shell">
            <div class="drive-list-head">
                <h3><span>▤</span>Liste des fichiers</h3>
                <small>Affichage de {min(len(files), 1)} à {len(files)} sur {len(files_all)} fichiers</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for index, shared_file in enumerate(files):
        path = Path(shared_file.get("path", ""))
        role_label = "Direction BTS SMARTCAMPUS" if shared_file.get("role") == "direction" else shared_file.get("auteur", "Professeur")
        extension = shared_file_extension(shared_file)
        title = html.escape(str(shared_file.get("titre", "Fichier partage")))
        subject = html.escape(str(shared_file.get("matiere", "Toutes les matières")))
        description = html.escape(str(shared_file.get("description", "")))
        date = html.escape(str(shared_file.get("date", "Date non indiquée")))
        size = shared_file_size(path) if path.exists() else ""
        item_key = f"{path.as_posix()}_{shared_file.get('date', '')}_{index}"

        st.markdown('<div class="drive-file-card-shell">', unsafe_allow_html=True)
        file_col, download_col, preview_col = st.columns([6.4, 1.45, 1.25], vertical_alignment="center")
        with file_col:
            st.markdown(
                f"""
                <div class="drive-file-row">
                    <div class="drive-file-type drive-file-{extension.lower()}">{extension}</div>
                    <div class="drive-file-info">
                        <strong>{title}</strong>
                        <div class="drive-file-meta">
                            <span>Matière : {subject}</span>
                            <span>Publié par : {html.escape(str(role_label))}</span>
                            <span>Date : {date}</span>
                        </div>
                        <p>{description}</p>
                    </div>
                    <div class="drive-file-size">{html.escape(size)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with download_col:
            if path.exists() and path.is_file():
                st.download_button(
                    "Telecharger",
                    data=path.read_bytes(),
                    file_name=shared_file.get("filename") or path.name,
                    mime=shared_file.get("mime", "application/octet-stream"),
                    key=f"drive_download_{item_key}",
                    width="stretch",
                )
            else:
                st.button("Indisponible", key=f"drive_missing_{item_key}", disabled=True, width="stretch")

        with preview_col:
            if st.button("Apercu", key=f"drive_preview_{item_key}", width="stretch"):
                preview_key = st.session_state.get("drive_preview_key")
                st.session_state.drive_preview_key = "" if preview_key == item_key else item_key
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.get("drive_preview_key") == item_key:
            render_shared_file_preview(shared_file, item_key)


def show_student_space(data):
    show_academic_page_header(
        "Espace étudiant",
        "Accès rapide aux cours, fiches Drive, examens et annonces importantes.",
        "E",
    )

    selected_subject = st.selectbox("Choisir une matiere", SUBJECTS)
    st.markdown(f"#### {selected_subject}")

    for resource in data["cours"].get(selected_subject, []):
        show_resource_card(resource, extra="Cours")

    st.markdown("#### Examens lies")
    related_exams = [
        exam
        for exam in data["examens"]
        if exam["matiere"] in (selected_subject, "Toutes les matières")
    ]
    for exam in related_exams:
        show_resource_card(exam, extra=exam.get("annee", ""))


def add_course_form(data, subject, prof_name="Administration"):
    st.markdown("#### Ajouter un cours")
    st.caption(
        f"Remplissez ces informations pour publier un nouveau cours dans {subject}."
    )
    with st.form("add_course_form", clear_on_submit=True):
        st.text_input("Matière du cours", value=subject, disabled=True)
        title = st.text_input(
            "Nom du cours",
            placeholder="Exemple: Politique de prix",
            help="Écrivez le titre qui sera visible par les étudiants.",
        )
        description = st.text_area(
            "Description du cours",
            placeholder="Exemple: Cours PDF avec explication et exercices.",
            help="Ajoutez une courte phrase pour expliquer le contenu du cours.",
        )
        publish_mode = st.radio(
            "Mode de publication",
            ["Lien Drive", "Fichier depuis l'ordinateur"],
            horizontal=True,
            help="Choisissez un lien externe ou téléversez directement un fichier.",
        )
        st.caption(
            "Astuce : choisissez le mode, puis remplissez seulement le lien Drive ou ajoutez seulement le fichier."
        )
        url = st.text_input(
            "Lien Drive du cours",
            placeholder="Exemple: https://drive.google.com/file/d/.../view",
            help="Collez le lien Google Drive du fichier ou du dossier du cours.",
        )
        uploaded_file = st.file_uploader(
            "Fichier du cours",
            accept_multiple_files=False,
            help="Formats acceptés : PDF, Word, PowerPoint, Excel, image, texte, archive ou autre fichier utile au cours.",
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
        title = title.strip()
        description = description.strip()
        url = url.strip()
        if not title:
            st.error("Le titre du cours est obligatoire.")
            return
        if publish_mode == "Lien Drive" and not url:
            st.error("Le lien Drive est obligatoire.")
            return
        if publish_mode == "Fichier depuis l'ordinateur" and uploaded_file is None:
            st.error("Veuillez ajouter un fichier de cours.")
            return

        source = "drive"
        file_path = ""
        file_name = ""
        file_mime = ""
        if publish_mode == "Fichier depuis l'ordinateur":
            saved_path = save_uploaded_file(uploaded_file, folder=f"cours_{subject}")
            source = "upload"
            file_path = str(saved_path)
            file_name = uploaded_file.name
            file_mime = uploaded_file.type or "application/octet-stream"
            url = ""

        data["cours"].setdefault(subject, []).append(
            {
                "titre": title,
                "description": description,
                "url": url,
                "source": source,
                "path": file_path,
                "filename": file_name,
                "mime": file_mime,
                "type": resource_type,
                "statut": status,
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "prof": prof_name,
                "_id": uuid.uuid4().hex[:24],
            }
        )
        save_data(data)
        st.success("Cours ajouté avec succès.")
        st.rerun()


def delete_course_form(data, subject):
    st.markdown("#### Supprimer un cours")
    st.caption(
        f"Vous pouvez supprimer uniquement les cours de {subject}."
    )
    st.text_input("Matière du cours à supprimer", value=subject, disabled=True)
    resources = data["cours"].get(subject, [])

    if not resources:
        st.info("Aucun cours à supprimer pour cette matière.")
        return

    labels = [f"{index + 1}. {resource['titre']}" for index, resource in enumerate(resources)]
    selected = st.selectbox(
        "Cours à supprimer",
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
            "Année de l'examen",
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
            help="Écrivez le titre visible par les étudiants.",
        )
        description = st.text_area(
            "Description de l'examen",
            placeholder="Exemple : sujet national avec corrigé.",
            help="Précisez si le fichier contient le sujet, le corrigé ou les deux.",
        )
        url = st.text_input(
            "Lien Drive/PDF de l'examen",
            placeholder="Exemple: https://drive.google.com/file/d/.../view",
            help="Collez le lien Google Drive du fichier PDF ou du dossier d'examens.",
        )
        corrige_url = st.text_input(
            "Lien Drive/PDF du corrigé",
            placeholder="Optionnel: https://drive.google.com/file/d/.../view",
            help="Ajoutez le corrigé si vous l'avez. Ce champ peut rester vide.",
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
        st.info("Aucun examen à supprimer.")
        return

    labels = [
        f"{index + 1}. {exam['titre']} - {exam.get('annee', '')}"
        for index, exam in enumerate(subject_exams)
    ]
    selected = st.selectbox(
        "Examen à supprimer",
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
    st.markdown("#### Messages aux étudiants")
    st.caption(f"Publiez une annonce visible pour la matiere {subject}.")
    with st.form("add_message_form", clear_on_submit=True):
        st.text_input("Matiere du message", value=subject, disabled=True)
        title = st.text_input(
            "Titre du message",
            placeholder="Exemple: Controle le lundi 27 mai",
            help="Titre court de l'annonce visible par les étudiants.",
        )
        content = st.text_area(
            "Contenu du message",
            placeholder="Exemple: Merci de réviser les chapitres 1 et 2 avant le controle.",
            help="Écrivez le message complet à afficher aux étudiants.",
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
        st.success("Message publié.")
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
            "Message à supprimer",
            labels,
            help="Sélectionnez l'annonce à retirer de la page d'accueil.",
        )

        if st.button("Supprimer ce message", type="secondary"):
            selected_index = labels.index(selected)
            message_to_delete = subject_messages[selected_index]
            data["messages"].remove(message_to_delete)
            save_data(data)
            st.success("Message supprime.")
            st.rerun()
    else:
        st.info("Aucun message publié pour votre matière.")


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
        st.success("Date d'examen publiée.")
        st.rerun()

    st.divider()
    st.markdown("#### Supprimer une date d'examen")
    subject_homework = [
        devoir for devoir in data.get("devoirs", []) if devoir.get("matiere") == subject
    ]

    if not subject_homework:
        st.info("Aucune date d'examen à supprimer pour cette matière.")
        return

    labels = [
        f"{index + 1}. {devoir.get('matiere', subject)} - {devoir.get('date_limite', '')}"
        for index, devoir in enumerate(subject_homework)
    ]
    selected = st.selectbox("Date d'examen à supprimer", labels)

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
                ["Toutes les matières"] + SUBJECTS,
                help="Choisissez Toutes les matières pour publier à tous les étudiants.",
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
        st.info("Aucun fichier à supprimer.")
        return

    labels = [
        f"{index + 1}. {shared_file.get('titre')} - {shared_file.get('matiere')}"
        for index, shared_file in enumerate(manageable_files)
    ]
    selected = st.selectbox("Fichier à supprimer", labels)
    if st.button("Supprimer ce fichier", type="secondary"):
        selected_index = labels.index(selected)
        file_to_delete = manageable_files[selected_index]
        data["shared_files"].remove(file_to_delete)
        save_data(data)
        st.success("Fichier retire de la plateforme.")
        st.rerun()


def student_contact_inbox(data, subject):
    st.markdown("#### Messages des étudiants")
    messages = [
        contact
        for contact in data.get("student_contacts", [])
        if contact.get("matiere") == subject
    ]
    messages = sorted(messages, key=lambda contact: parse_date(contact.get("date")), reverse=True)

    if not messages:
        st.info("Aucun message d'étudiant pour votre matière.")
        return

    for index, contact in enumerate(messages):
        st.markdown(
            f"""
            <div class="message">
                <div class="message-title">{contact.get("prenom", "")} {contact.get("nom", "")}</div>
                <div class="message-meta">
                    Matière : {contact.get("matiere", "")} | Date: {contact.get("date", "Date non indiquée")}
                </div>
                <div class="message-content">{contact.get("message", "")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if contact.get("reponse"):
            st.success(f"Réponse envoyée: {contact.get('reponse')}")
        else:
            response = st.text_area(
                "Répondre à cet étudiant",
                key=f"response_{subject}_{index}_{contact.get('date')}",
            )
            if st.button("Envoyer la reponse", key=f"send_response_{subject}_{index}_{contact.get('date')}"):
                if not response.strip():
                    st.error("La reponse ne peut pas etre vide.")
                else:
                    contact["reponse"] = response.strip()
                    contact["date_reponse"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    save_data(data)
                    st.success("Réponse enregistrée.")
                    st.rerun()


def student_accounts_admin(data):
    st.markdown("#### Validation des comptes étudiants")
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
                    Groupe: <strong>{account.get('groupe', 'Non indiqué')}</strong><br>
                    Statut: <strong>{status_label}</strong><br>
                    Demande envoyée: {account.get('created_at', 'Date non indiquée')}
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
            st.success("Compte étudiant validé.")
            st.rerun()
        if col2.button("Refuser", key=f"reject_student_{email}", disabled=status == "rejected"):
            accounts[email]["status"] = "rejected"
            save_data(data)
            st.warning("Compte étudiant refusé.")
            st.rerun()
        if col3.button("Supprimer", key=f"delete_student_{email}"):
            del accounts[email]
            save_data(data)
            st.success("Compte étudiant supprimé.")
            st.rerun()


def support_tickets_admin(data):
    st.markdown(
        """
        <div class="contact-hero">
            <div class="contact-title-wrap">
                <div class="contact-icon">S</div>
                <div>
                    <h1>Support admin</h1>
                    <p>Consultez les réclamations envoyées par les utilisateurs et repondez directement depuis cette page.</p>
                </div>
            </div>
            <div class="contact-art"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tickets = data.get("support_tickets", [])
    if not tickets:
        st.info("Aucune réclamation pour le moment.")
        return

    status_filter = st.selectbox(
        "Filtrer par statut",
        ["Tous", "Nouveau", "En cours", "Traité"],
        key="support_status_filter",
    )
    filtered_tickets = tickets
    if status_filter != "Tous":
        filtered_tickets = [
            ticket for ticket in tickets if ticket.get("statut", "Nouveau") == status_filter
        ]

    if not filtered_tickets:
        st.info("Aucune réclamation dans ce filtre.")
        return

    for index, ticket in enumerate(filtered_tickets):
        original_index = tickets.index(ticket)
        st.markdown(
            f"""
            <div class="message">
                <div class="message-title">{ticket.get('sujet', 'Réclamation')}</div>
                <div class="message-meta">
                    Type: {ticket.get('type', 'Réclamation')} | Statut: {ticket.get('statut', 'Nouveau')} | Date: {ticket.get('date', 'Date non indiquée')}
                </div>
                <div class="message-content">
                    Utilisateur: <strong>{ticket.get('nom', 'Utilisateur')}</strong><br>
                    Email: <strong>{ticket.get('email', 'Non indiqué')}</strong><br><br>
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
                f"Réponse admin ({ticket.get('date_reponse', 'Date non indiquée')}): {ticket.get('reponse')}"
            )

        response = st.text_area(
            "Réponse à envoyer à l'utilisateur",
            value=ticket.get("reponse", ""),
            key=f"support_response_{original_index}_{ticket.get('date', '')}",
        )
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Enregistrer la réponse", key=f"support_reply_{original_index}_{ticket.get('date')}"):
            if not response.strip():
                st.error("La réponse ne peut pas être vide.")
            else:
                tickets[original_index]["reponse"] = response.strip()
                tickets[original_index]["date_reponse"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                tickets[original_index]["statut"] = "Traité"
                save_data(data)
                st.success("Réponse envoyée et réclamation marquée comme traitée.")
                st.rerun()
        if col2.button("En cours", key=f"support_progress_{original_index}_{ticket.get('date')}"):
            tickets[original_index]["statut"] = "En cours"
            save_data(data)
            st.rerun()
        if col3.button("Traité", key=f"support_done_{original_index}_{ticket.get('date')}"):
            tickets[original_index]["statut"] = "Traité"
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
        "name": "Compte étudiant général",
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
        st.info("Aucun utilisateur trouvé.")
        return

    actionable_users = [user for user in users if user["kind"] != "system"]
    if actionable_users:
        st.markdown("#### Panneau d'action rapide")
        selected_email = st.selectbox(
            "Choisir un utilisateur à gérer",
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
        generated_password_key = f"generated_password_{selected_user['kind']}_{selected_user['email']}"
        st.caption(
            "Sécurité : les anciens mots de passe sont protégés par hash. "
            "L'admin peut seulement définir ou générer un nouveau mot de passe temporaire."
        )
        if st.button(
            "Générer un mot de passe temporaire",
            key=f"quick_generate_pwd_{selected_user['kind']}_{selected_user['email']}",
            width="stretch",
        ):
            temporary_password = generate_temporary_password()
            if selected_user["kind"] == "prof":
                data["prof_accounts"][selected_user["email"]]["password"] = hash_password(temporary_password)
            else:
                data["student_accounts"][selected_user["email"]]["password"] = hash_password(temporary_password)
            st.session_state[generated_password_key] = temporary_password
            save_data(data)
            st.success("Mot de passe temporaire généré et enregistré.")

        if generated_password_key in st.session_state:
            st.warning("Copiez ce mot de passe maintenant. Il ne sera pas visible après changement d'utilisateur.")
            st.code(st.session_state[generated_password_key], language=None)

        msg_title = st.text_input(
            "Titre du message",
            key=f"quick_message_title_{selected_user['kind']}_{selected_user['email']}",
        )
        msg_content = st.text_area(
            "Message à envoyer",
            key=f"quick_message_content_{selected_user['kind']}_{selected_user['email']}",
        )
        col1, col2, col3, col4 = st.columns(4)

        if col1.button("Changer mot de passe", key=f"quick_pwd_{selected_user['kind']}_{selected_user['email']}"):
            if not new_password.strip():
                st.error("Le nouveau mot de passe est obligatoire.")
            elif selected_user["kind"] == "prof":
                data["prof_accounts"][selected_user["email"]]["password"] = hash_password(new_password.strip())
                st.session_state.pop(generated_password_key, None)
                save_data(data)
                st.success("Mot de passe professeur modifie.")
                st.rerun()
            else:
                data["student_accounts"][selected_user["email"]]["password"] = hash_password(new_password.strip())
                st.session_state.pop(generated_password_key, None)
                save_data(data)
                st.success("Mot de passe étudiant modifié.")
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
                st.success("Message envoyé à l'étudiant.")
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
                        "contenu": f"Message destiné à {selected_user['name']}: {msg_content.strip()}",
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
                st.success("Compte étudiant supprimé.")
                st.rerun()

    st.markdown("#### Liste des identifiants")
    for user in users:
        is_system = user["kind"] == "system"
        password_display = (
            "Protégé par configuration"
            if is_system
            else "Protégé par hash sécurisé - réinitialisable par l'admin"
        )
        st.markdown(
            f"""
            <div class="card">
                <h3>{user["name"]}</h3>
                <p>
                    Role: <strong>{user["role"]}</strong><br>
                    Email: <strong>{user["email"]}</strong><br>
                    Mot de passe: <strong>{password_display}</strong><br>
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
    show_academic_page_header(
        "Espace administration",
        "Gestion complète des cours, examens, messages, fichiers et comptes de la plateforme.",
        "A",
    )
    show_usage_guide(
        "Administration",
        [
            "Choisissez une section pour gérer les cours, examens, messages, fichiers ou utilisateurs.",
            "Dans Cours, ajoutez une ressource par lien Drive ou par fichier PDF, Word, image, Excel ou PowerPoint.",
            "Dans Utilisateurs, validez les inscriptions, gérez les comptes et générez un mot de passe temporaire si nécessaire.",
        ],
    )
    st.success("Connecté : Administration BTS SMARTCAMPUS | Accès complet")

    section = st.radio(
        "Choisir une section",
        ["Cours", "Examens", "Messages", "Planning examens", "Fichiers", "Discussion", "Utilisateurs", "Comptes étudiants", "Support"],
        horizontal=True,
        key="admin_section_choice",
    )

    if section == "Cours":
        subject = st.selectbox("Matière à gérer", SUBJECTS, key="admin_course_subject")
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
    elif section == "Comptes étudiants":
        student_accounts_admin(data)
    else:
        support_tickets_admin(data)


def show_prof_space(data):
    user_role = st.session_state.get("platform_user_role", "student")
    user_email = st.session_state.get("platform_user_email", "")

    if user_role not in ("prof", "admin"):
        st.error("Accès réservé aux professeurs et à l'administration.")
        return

    if user_role == "admin":
        show_admin_space(data)
        return

    account = data.get("prof_accounts", {}).get(user_email)
    if not account:
        st.error("Compte professeur introuvable.")
        return

    subject = account.get("subject", "General")
    prof_name = account.get("name", "Professeur")
    show_academic_page_header(
        "Espace professeur",
        f"Publiez et gérez les contenus de la matière {subject}.",
        "P",
    )
    show_usage_guide(
        "Professeur",
        [
            "Ajoutez des cours avec un lien Drive ou un fichier depuis votre ordinateur.",
            "Publiez des messages et dates d'examen pour informer les étudiants.",
            "Consultez les messages envoyés par les étudiants dans la section Discussion.",
        ],
    )
    st.success(f"Connecté : {prof_name} | Matière : {subject}")

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
        st.error("Accès réservé à la direction.")
        return

    show_academic_page_header(
        "Espace direction",
        "Diffusez les annonces officielles, validez les comptes et partagez les documents importants.",
        "D",
    )
    st.success("Connecté : Direction BTS SMARTCAMPUS")

    section = st.radio(
        "Choisir une section",
        ["Messages officiels", "Fichiers partagés", "Comptes étudiants"],
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
            target_subject = st.selectbox("Destination", ["Toutes les matières"] + SUBJECTS)
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

    elif section == "Fichiers partagés":
        shared_file_admin(data, "Toutes les matières", "Direction BTS SMARTCAMPUS", "direction")
    elif section == "Comptes étudiants":
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
    show_usage_guide(
        "Discussion professeur",
        [
            "Sélectionnez la matière concernée par votre question.",
            "Rédigez votre demande clairement avec votre nom et prénom.",
            "Le professeur ou l'administration pourra consulter et traiter votre message.",
        ],
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
        st.success("Votre message a été envoyé au professeur.")

    st.markdown(
        """
        <div class="contact-help">
            <span class="contact-help-icon">i</span>
            <span>Votre message sera transmis directement au professeur de la matière sélectionnée.</span>
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
                    <p>Envoyez une réclamation, un problème technique ou une demande d'aide au support de la plateforme.</p>
                </div>
            </div>
            <div class="contact-art"></div>
        </div>
        <div class="contact-form-title">Nouvelle réclamation</div>
        """,
        unsafe_allow_html=True,
    )
    show_usage_guide(
        "Support",
        [
            "Utilisez l'assistant pour obtenir une première réponse rapide.",
            "Envoyez une réclamation si le problème nécessite une intervention de l'administration.",
            "Ajoutez une capture d'écran ou un fichier si cela peut aider le support à comprendre le problème.",
        ],
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
            placeholder="Expliquez clairement votre réclamation ou le problème rencontré...",
        )
        screenshot = st.file_uploader(
            "Capture d'écran ou fichier du problème (optionnel)",
            accept_multiple_files=False,
            help="Optionnel: ajoutez une capture d'écran, une image, un PDF ou un autre fichier si cela aide le support.",
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
        st.success("Votre demande a été envoyée au support.")

    st.markdown(
        """
        <div class="contact-help">
            <span class="contact-help-icon">i</span>
            <span>Votre réclamation sera gérée par l'admin ou le support de la plateforme.</span>
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
        st.markdown("#### Mes réclamations")
        for index, ticket in enumerate(sorted(user_tickets, key=lambda item: parse_date(item.get("date")), reverse=True)):
            response_html = ""
            if ticket.get("reponse"):
                response_html = f"""
                    <div class="message-content">
                        <strong>Réponse support:</strong><br>
                        {ticket.get('reponse', '')}<br>
                        <span class="message-meta">Date de réponse : {ticket.get('date_reponse', 'Date non indiquée')}</span>
                    </div>
                """
            st.markdown(
                f"""
                <div class="message">
                    <div class="message-title">{ticket.get('sujet', 'Réclamation')}</div>
                    <div class="message-meta">
                        Type: {ticket.get('type', 'Réclamation')} | Statut: {ticket.get('statut', 'Nouveau')} | Date: {ticket.get('date', 'Date non indiquée')}
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
                <span>Boîte<br><strong>Messages</strong></span>
                <span class="contact-avatar"></span>
            </div>
        </div>
        <div class="contact-hero">
            <div class="contact-title-wrap">
                <div class="contact-icon">M</div>
                <div>
                    <h1>Messages</h1>
                    <p>Consultez vos messages administratifs et les pièces jointes envoyées.</p>
                </div>
            </div>
            <div class="contact-art"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    show_usage_guide(
        "Messages",
        [
            "Consultez ici les messages envoyés par l'administration ou les professeurs.",
            "L'administration peut envoyer un message direct à un utilisateur précis.",
            "Les pièces jointes apparaissent sous le message quand elles sont disponibles.",
        ],
    )

    if current_role == "admin":
        st.markdown("#### Envoyer un message à un utilisateur")
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

    st.markdown("#### Boîte de réception")
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
                    De: {message.get("from_name", "Administration BTS SMARTCAMPUS")} | Date: {message.get("date", "Date non indiquée")}{target_line}
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
        ("Fichiers partagés", "Fichiers Drive"),
        ("Examens nationaux", "Examens"),
        ("Planification des examens", "Calendrier"),
        ("Messages directs", "Messages"),
        ("Contact", "Profil"),
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
            ("Fichiers partagés", "Fichiers Drive"),
            ("Examens nationaux", "Examens"),
            ("Planification des examens", "Calendrier"),
            ("Espace professeur", "Professeurs"),
            ("Espace direction", "Annonces"),
            ("Utilisateurs", "Profil"),
            ("Messages directs", "Messages"),
            ("Contact et support", "Support"),
        ]
    elif user_role == "direction":
        pages = [
            ("Accueil", "Accueil"),
            ("Espace direction", "Annonces"),
            ("Messages directs", "Messages"),
            ("Contact et support", "Support"),
        ]
    else:
        pages = list(student_pages)

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Accueil"
    allowed_pages = [page_name for page_name, _ in pages] + ["Dernières mises à jour"]
    if st.session_state.current_page not in allowed_pages:
        st.session_state.current_page = "Accueil"

    st.sidebar.markdown(
        """
        <div class="academic-sidebar-brand">
            <div class="academic-sidebar-crest">BTS</div>
            <h2>BTS <span>SMARTCAMPUS</span></h2>
            <p>PLATEFORME ACADEMIQUE</p>
        </div>
        <div class="academic-sidebar-label">Navigation</div>
        """,
        unsafe_allow_html=True,
    )

    nav_icons = {
        "Accueil": "⌂",
        "Cours": "▤",
        "Fichiers Drive": "▣",
        "Examens": "◇",
        "Calendrier": "□",
        "Professeurs": "◉",
        "Messages": "✉",
        "Annonces": "!",
        "Profil": "○",
        "Support": "?",
    }

    for page_name, label in pages:
        is_active = st.session_state.current_page == page_name
        button_label = f"{nav_icons.get(label, '*')}  {label}"
        if st.sidebar.button(
            button_label,
            key=f"nav_{page_name}",
            width="stretch",
            type="primary" if is_active else "secondary",
        ):
            st.session_state.current_page = page_name
            st.rerun()

    st.sidebar.markdown(
        """
        <div class="sidebar-study-card">
            <div class="sidebar-study-head">
                <div class="sidebar-study-icon">BTS</div>
                <div>
                    <strong>Restez organisé,<br>réussissez vos études.</strong>
                    <small>Session active</small>
                </div>
            </div>
            <div class="sidebar-progress-label">
                <span>Progression annuelle</span>
                <b>2026 - 2027</b>
            </div>
            <div class="sidebar-progress"><span></span></div>
            <div class="sidebar-study-foot">
                <small>Année scolaire</small>
                <b>2026 - 2027</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return st.session_state.current_page


def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="SC",
        layout="wide",
        initial_sidebar_state="expanded",
    )
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
    if "dashboard_transition_once" not in st.session_state:
        st.session_state.dashboard_transition_once = False

    # Keep the production flow reliable: old sessions can keep a transition flag
    # active after a rerun, which hides the app behind a full-screen overlay.
    st.session_state.login_transition = False
    st.session_state.entry_animation = False

    if not st.session_state.platform_logged_in:
        show_platform_login(data)
        return

    if not st.session_state.platform_started:
        show_welcome_academic()
        return

    if st.session_state.get("dashboard_transition_once"):
        st.markdown(
            """
            <style>
            [data-testid="stMainBlockContainer"] {
                animation: dashboardGate3d 0.72s cubic-bezier(.2,.84,.24,1) both !important;
                transform-origin: center top !important;
                will-change: transform, opacity, filter;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.session_state.dashboard_transition_once = False

    page = sidebar_navigation()

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Connecté : {st.session_state.platform_user_label}")
    if st.sidebar.button("Se déconnecter", key="platform_logout"):
        st.session_state.platform_logged_in = False
        st.session_state.platform_started = False
        st.session_state.entry_animation = False
        st.session_state.login_transition = False
        st.session_state.dashboard_transition_once = False
        st.session_state.platform_user_email = ""
        st.session_state.platform_user_role = "student"
        st.session_state.current_page = "Accueil"
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Les cours, examens et messages sont sauvegardés dans btsmtacademy_data.json."
    )

    if page == "Accueil":
        show_home(data)
    elif page == "Recherche rapide":
        show_search(data)
    elif page == "Dernières mises à jour":
        show_updates(data)
    elif page == "Cours":
        show_courses(data)
    elif page == "Examens nationaux":
        show_exams(data)
    elif page == "Planification des examens":
        show_homework_plan(data)
    elif page == "Fichiers partagés":
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


if __name__ == "__main__":
    main()
