import calendar
import base64
import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st


APP_TITLE = "BTSMT Academy"
DATA_FILE = Path("btsmtacademy_data.json")
BACKUP_DIR = Path("btsmtacademy_backups")
UPLOAD_DIR = Path("btsmtacademy_uploads")
LOGO_PATH = Path(r"c:\Users\pc\Downloads\plf logo.png")
RESOURCE_TYPES = ["Cours", "Exercice", "Correction", "Examen", "Fiche resume"]
COURSE_STATUS = ["Disponible", "A reviser", "Corrige ajoute", "Mis a jour"]
ADMIN_EMAIL = "admin@btsmtacademy.com"
ADMIN_PASSWORD = os.getenv("BTSMT_ADMIN_PASSWORD", "admin123")
DIRECTION_EMAIL = "direction@btsmtacademy.com"
DIRECTION_PASSWORD = os.getenv("BTSMT_DIRECTION_PASSWORD", "direction123")


def env_password(name, default):
    return os.getenv(name, default)

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

PROF_ACCOUNTS = {
    ADMIN_EMAIL: {
        "name": "Administration BTSMT",
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
        "devoirs": [],
        "shared_files": [],
        "student_contacts": [],
        "messages": [
            {
                "titre": "Bienvenue sur BTSMT Academy",
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


def load_data():
    if not DATA_FILE.exists():
        save_data(default_data())

    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    for message in data.get("messages", []):
        message.setdefault("matiere", "General")
        message.setdefault("prof", "Administration")
        message.setdefault("date", "Date non indiquee")
        message.setdefault("important", False)

    for subject in SUBJECTS:
        data.setdefault("cours", {}).setdefault(subject, [])
        for resource in data["cours"][subject]:
            resource.setdefault("type", "Cours")
            resource.setdefault("statut", "Disponible")
            resource.setdefault("date", "Date non indiquee")
            resource.setdefault("prof", "Administration")

    for exam in data.get("examens", []):
        exam.setdefault("session", "Archive")
        exam.setdefault("corrige_url", "")
        exam.setdefault("date", "Date non indiquee")

    data.setdefault("prof_accounts", PROF_ACCOUNTS)
    for email, account in PROF_ACCOUNTS.items():
        data["prof_accounts"].setdefault(email, account)
        env_var = ACCOUNT_PASSWORD_ENV.get(email)
        if env_var and os.getenv(env_var):
            data["prof_accounts"][email]["password"] = os.getenv(env_var)

    data.setdefault("devoirs", [])
    for devoir in data["devoirs"]:
        devoir.setdefault("matiere", "General")
        devoir.setdefault("titre", "Devoir")
        devoir.setdefault("description", "")
        devoir.setdefault("date_limite", "")
        devoir.setdefault("lien", "")
        devoir.setdefault("prof", "Administration")
        devoir.setdefault("date_publication", "Date non indiquee")

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

    data.setdefault("student_contacts", [])
    for contact in data["student_contacts"]:
        contact.setdefault("matiere", "General")
        contact.setdefault("nom", "")
        contact.setdefault("prenom", "")
        contact.setdefault("message", "")
        contact.setdefault("date", "Date non indiquee")
        contact.setdefault("reponse", "")
        contact.setdefault("date_reponse", "")

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


def save_data(data):
    backup_data_file()
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
    st.markdown(
        f"""
        <div class="card">
            <h3>{shared_file.get("titre", "Fichier partage")}</h3>
            <div class="muted">
                Matiere: {shared_file.get("matiere", "Toutes les matieres")} |
                Publie par: {shared_file.get("auteur", "Administration")} |
                Date: {shared_file.get("date", "Date non indiquee")}
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
            min-height: 62vh;
            margin: -1.6rem calc(50% - 50vw) -2rem calc(50% - 50vw);
            background:
                linear-gradient(110deg, rgba(2, 6, 23, 0.94) 0%, rgba(18, 53, 91, 0.84) 46%, rgba(15, 118, 110, 0.72) 100%),
                repeating-linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0 1px, transparent 1px 22px);
            background-size: cover;
            background-position: center;
            color: #ffffff;
            animation: fadeSlideIn 220ms ease-out;
            position: relative;
            overflow: hidden;
        }

        .welcome-topbar {
            min-height: 96px;
            background: rgba(2, 6, 23, 0.46);
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: center;
            padding: 0 7vw;
            gap: 24px;
        }

        .welcome-nav {
            display: flex;
            gap: 34px;
            align-items: center;
            color: #ffffff;
            font-size: 14px;
            font-weight: 800;
            text-transform: uppercase;
        }

        .welcome-nav.right {
            justify-content: flex-end;
        }

        .welcome-brand {
            color: #f59e0b;
            font-size: 34px;
            font-weight: 900;
            letter-spacing: 1px;
            white-space: nowrap;
        }

        .welcome-hero {
            min-height: calc(62vh - 96px);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding: 8vh 12vw;
        }

        .welcome-copy {
            max-width: 660px;
            color: #ffffff;
            animation: fadeSlideIn 260ms ease-out;
            position: relative;
            z-index: 2;
        }

        .welcome-copy h1 {
            color: #ffffff;
            font-size: 68px;
            line-height: 1.08;
            margin: 0 0 24px 0;
            font-weight: 900;
            letter-spacing: 0;
        }

        .welcome-copy p {
            color: #ffffff;
            max-width: 560px;
            font-size: 24px;
            line-height: 1.35;
            margin: 0;
            font-weight: 700;
        }

        .welcome-copy::before {
            content: "BTS Management Touristique";
            display: inline-block;
            color: #111827;
            background: #f59e0b;
            padding: 8px 12px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 900;
            margin-bottom: 18px;
            text-transform: uppercase;
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
            margin: -120px auto 0 auto;
            position: relative;
            z-index: 4;
        }

        .welcome-actions div[data-testid="stButton"] > button {
            background: #f59e0b !important;
            border-color: #f59e0b !important;
            color: #111827 !important;
            min-height: 56px;
            font-size: 18px !important;
            box-shadow: 0 18px 36px rgba(245, 158, 11, 0.30) !important;
        }

        .welcome-actions div[data-testid="stButton"] > button * {
            color: #111827 !important;
            font-weight: 950 !important;
        }

        .welcome-actions + div {
            margin-top: 18px;
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
                font-size: 28px;
            }

            .welcome-hero {
                justify-content: center;
                padding: 7vh 8vw;
            }

            .welcome-copy h1 {
                font-size: 44px;
            }

            .welcome-copy p {
                font-size: 20px;
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
            margin-top: 36px;
            padding: 14px 16px;
            text-align: center;
            color: #475569;
            font-weight: 800;
            border-top: 1px solid #dbe4ef;
        }

        .creator-footer strong {
            color: #12355b;
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
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_header():
    st.markdown(
        """
        <div class="hero">
            <h1>BTSMT Academy</h1>
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


def show_welcome():
    st.markdown(
        """
        <div class="welcome-shell">
            <div class="welcome-topbar">
                <div class="welcome-nav">
                    <span>Academy</span>
                    <span>Ressources</span>
                </div>
                <div class="welcome-brand">BTSMT Academy</div>
                <div class="welcome-nav right">
                    <span>Examens</span>
                    <span>Direction</span>
                </div>
            </div>
            <div class="welcome-hero">
                <div class="welcome-copy">
                    <h1>Organisez votre reussite</h1>
                    <p>
                        Un espace moderne pour suivre les cours, les examens,
                        les annonces et les fichiers importants de votre formation.
                    </p>
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
    show_creator_footer()


def show_entry_transition():
    st.markdown(
        """
        <div class="entry-transition">
            <div class="entry-transition-content">
                <h2>BTSMT Academy</h2>
                <p>Chargement de votre espace de travail...</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.entry_animation = False


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
    show_header()

    total_courses = sum(len(resources) for resources in data["cours"].values())
    new_courses = sum(1 for item in all_course_items(data) if is_new(item.get("date")))
    total_files = len(data.get("shared_files", []))
    total_exams = len(data.get("examens", []))
    st.markdown(
        f"""
        <div class="dashboard-stat-grid">
            <div class="dashboard-stat stat-blue">
                <div class="label">Matieres</div>
                <div class="value">{len(SUBJECTS)}</div>
            </div>
            <div class="dashboard-stat stat-teal">
                <div class="label">Cours disponibles</div>
                <div class="value">{total_courses}</div>
            </div>
            <div class="dashboard-stat stat-amber">
                <div class="label">Nouveautes</div>
                <div class="value">{new_courses}</div>
            </div>
            <div class="dashboard-stat stat-violet">
                <div class="label">Fichiers & examens</div>
                <div class="value">{total_files + total_exams}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        st.subheader("Dernieres mises a jour")
        for item in latest_updates(data, limit=4):
            extra = f"{item.get('matiere')} | {item.get('type')} | {item.get('statut')} | {item.get('date')}"
            show_resource_card(item, extra=extra)

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
            date_label = message.get("date", "Date non indiquee")
            important_class = " message-important" if message.get("important") else ""
            important_badge = (
                '<span class="badge badge-important">Important</span>' if message.get("important") else ""
            )
            st.markdown(
                f"""
                <div class="message{important_class}">
                    <div class="message-title">{important_badge}{message["titre"]}</div>
                    <div class="message-meta">
                        Prof: {prof_label} | Matiere: {subject_label} | Date: {date_label}
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
        st.subheader("Cours")
        st.write("Choisissez une matiere pour afficher la liste des cours disponibles.")

        columns = st.columns(3)
        for index, subject in enumerate(SUBJECTS):
            resources_count = len(data["cours"].get(subject, []))
            with columns[index % 3]:
                st.markdown(
                    f"""
                    <div class="subject-card">
                        <strong>{subject}</strong><br>
                        <span class="muted">{resources_count} cours disponible(s)</span>
                        <div class="subject-action">Acceder aux ressources</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Ouvrir cette matiere", key=f"open_subject_{subject}", width="stretch"):
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
    st.subheader("Dernieres mises a jour")
    st.write("Les derniers cours, fiches, exercices et corrections ajoutes par les professeurs.")

    items = latest_updates(data, limit=30)
    if not items:
        st.info("Aucune mise a jour pour le moment.")
        return

    for item in items:
        extra = (
            f"{item.get('matiere')} | {item.get('type')} | "
            f"{item.get('statut')} | {item.get('prof')} | {item.get('date')}"
        )
        show_resource_card(item, extra=extra)


def show_exams(data):
    st.subheader("Examens nationaux precedents")

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
            extra = (
                f"{exam.get('matiere', '')} | {exam.get('session', 'Archive')} | "
                f"{exam.get('date', 'Date non indiquee')}"
            )
            show_resource_card(exam, extra=extra)
            corrige_url = exam.get("corrige_url", "")
            if corrige_url:
                st.link_button("Ouvrir le corrige", corrige_url)


def show_homework_plan(data):
    st.subheader("Planification des examens")
    st.write("Consultez uniquement la matiere et la date de chaque examen. Les dates de week-end ne sont pas affichees.")

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
        st.info("Aucun examen planifie pour le moment.")
        return

    for devoir in devoirs:
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


def show_shared_files(data):
    st.subheader("Fichiers partages")
    st.write("Documents, images, PDF, Word, Excel et autres fichiers partages par la direction ou les professeurs.")

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


def show_admin_space(data):
    st.success("Connecte: Administration BTSMT | Acces complet")
    if st.button("Se deconnecter", key="admin_logout"):
        st.session_state.prof_connected = False
        st.session_state.prof_subject = None
        st.session_state.prof_name = None
        st.session_state.prof_role = None
        st.rerun()

    section = st.radio(
        "Choisir une section",
        ["Cours", "Examens", "Messages", "Planning examens", "Fichiers", "Discussion", "Comptes professeurs"],
        horizontal=True,
        key="admin_section_choice",
    )

    if section == "Cours":
        subject = st.selectbox("Matiere a gerer", SUBJECTS, key="admin_course_subject")
        add_course_form(data, subject, "Administration BTSMT")
        st.divider()
        delete_course_form(data, subject)

    elif section == "Examens":
        subject = st.selectbox("Matiere des examens", SUBJECTS, key="admin_exam_subject")
        add_exam_form(data, subject)
        st.divider()
        delete_exam_form(data, subject)

    elif section == "Messages":
        subject = st.selectbox("Matiere du message", SUBJECTS, key="admin_message_subject")
        message_admin(data, subject, "Administration BTSMT")

    elif section == "Planning examens":
        subject = st.selectbox("Matiere de l'examen", SUBJECTS, key="admin_homework_subject")
        homework_admin(data, subject, "Administration BTSMT")

    elif section == "Fichiers":
        subject = st.selectbox("Matiere du fichier", SUBJECTS, key="admin_file_subject")
        shared_file_admin(data, subject, "Administration BTSMT", "direction")

    elif section == "Discussion":
        subject = st.selectbox("Matiere des messages", SUBJECTS, key="admin_contact_subject")
        student_contact_inbox(data, subject)

    else:
        st.markdown("#### Emails et mots de passe")
        accounts = data.get("prof_accounts", PROF_ACCOUNTS)
        for email, account in accounts.items():
            st.code(
                f"{account['subject']} | {email} | {account['password']}",
                language="text",
            )

        st.markdown("#### Modifier un mot de passe")
        professor_emails = [email for email in accounts if email != ADMIN_EMAIL]
        selected_email = st.selectbox("Compte professeur", professor_emails)
        new_password = st.text_input(
            "Nouveau mot de passe",
            type="password",
        )
        if st.button("Mettre a jour le mot de passe"):
            clean_new_password = new_password.strip()
            if not clean_new_password:
                st.error("Le nouveau mot de passe est obligatoire.")
            else:
                data["prof_accounts"][selected_email]["password"] = clean_new_password
                save_data(data)
                st.success("Mot de passe mis a jour.")
                st.rerun()


def show_prof_space(data):
    st.subheader("Espace professeur")

    if "prof_connected" not in st.session_state:
        st.session_state.prof_connected = False
    if "prof_subject" not in st.session_state:
        st.session_state.prof_subject = None
    if "prof_name" not in st.session_state:
        st.session_state.prof_name = None
    if "prof_role" not in st.session_state:
        st.session_state.prof_role = None

    if not st.session_state.prof_connected:
        with st.form("prof_login_form"):
            username = st.text_input(
                "Email ou identifiant professeur",
                help="Entrez l'email ou l'identifiant donne par l'administration.",
                key="prof_login_email",
            )
            password = st.text_input(
                "Mot de passe",
                type="password",
                help="Entrez le mot de passe associe a votre compte professeur.",
                key="prof_login_password",
            )
            submitted = st.form_submit_button("Se connecter")

        if submitted:
            accounts = data.get("prof_accounts", PROF_ACCOUNTS)
            clean_username = username.strip().lower()
            clean_password = password.strip()
            account = accounts.get(clean_username)
            if account and clean_password == str(account["password"]).strip():
                st.session_state.prof_connected = True
                st.session_state.prof_subject = account["subject"]
                st.session_state.prof_name = account["name"]
                st.session_state.prof_role = account.get("role", "prof")
                st.success("Connexion reussie.")
                st.rerun()
            elif account:
                st.error("Email correct, mais mot de passe incorrect.")
            else:
                st.error("Compte professeur introuvable.")
        st.caption(
            "Chaque compte professeur donne acces seulement a sa matiere."
        )
        return

    if st.session_state.prof_role == "admin":
        show_admin_space(data)
        return

    subject = st.session_state.prof_subject
    prof_name = st.session_state.prof_name or "Professeur"
    st.success(f"Connecte: {prof_name} | Matiere: {subject}")
    if st.button("Se deconnecter"):
        st.session_state.prof_connected = False
        st.session_state.prof_subject = None
        st.session_state.prof_name = None
        st.session_state.prof_role = None
        st.rerun()

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
    st.subheader("Espace direction")

    if "direction_connected" not in st.session_state:
        st.session_state.direction_connected = False

    if not st.session_state.direction_connected:
        with st.form("direction_login_form"):
            email = st.text_input(
                "Email direction",
            )
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter")

        if submitted:
            if email.strip().lower() == DIRECTION_EMAIL and password.strip() == DIRECTION_PASSWORD:
                st.session_state.direction_connected = True
                st.success("Connexion direction reussie.")
                st.rerun()
            else:
                st.error("Identifiant direction incorrect.")
        return

    st.success("Connecte: Direction BTSMT")
    if st.button("Se deconnecter", key="direction_logout"):
        st.session_state.direction_connected = False
        st.rerun()

    section = st.radio(
        "Choisir une section",
        ["Messages officiels", "Fichiers partages"],
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
                    "prof": "Direction BTSMT",
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
                        "auteur": "Direction BTSMT",
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

    else:
        shared_file_admin(data, "Toutes les matieres", "Direction BTSMT", "direction")


def show_contact(data):
    st.subheader("Discussion avec les professeurs")
    st.write("Choisissez une matiere, puis envoyez votre message au professeur concerne.")

    with st.form("student_contact_form", clear_on_submit=True):
        subject = st.selectbox("Matiere", SUBJECTS)
        col1, col2 = st.columns(2)
        first_name = col1.text_input("Prenom", placeholder="Votre prenom")
        last_name = col2.text_input("Nom", placeholder="Votre nom")
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

    st.markdown("#### Reponses des professeurs")
    student_name = st.text_input(
        "Rechercher vos reponses par nom ou prenom",
        placeholder="Tapez votre nom ou prenom",
    )
    if student_name.strip():
        needle = student_name.strip().lower()
        replies = [
            contact
            for contact in data.get("student_contacts", [])
            if contact.get("reponse")
            and (
                needle in contact.get("nom", "").lower()
                or needle in contact.get("prenom", "").lower()
            )
        ]
        if not replies:
            st.info("Aucune reponse trouvee pour ce nom.")
        for contact in replies:
            st.markdown(
                f"""
                <div class="message">
                    <div class="message-title">{contact.get("matiere", "")}</div>
                    <div class="message-meta">Reponse du professeur | {contact.get("date_reponse", "")}</div>
                    <div class="message-content">{contact.get("reponse", "")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def sidebar_navigation():
    pages = [
        ("Accueil", "Dashboard"),
        ("Dernieres mises a jour", "Mises a jour"),
        ("Cours", "Cours"),
        ("Examens nationaux", "Examens"),
        ("Planification des examens", "Planification des examens"),
        ("Fichiers partages", "Fichiers partages"),
        ("Espace professeur", "Professeurs"),
        ("Espace direction", "Direction"),
        ("Contact", "Discussion profs"),
    ]

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Accueil"

    st.sidebar.markdown("### BTSMT Academy")
    st.sidebar.caption("Navigation")

    for page_name, label in pages:
        is_active = st.session_state.current_page == page_name
        button_label = f"> {label}" if is_active else label
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
    st.set_page_config(page_title=APP_TITLE, page_icon="BT", layout="wide")
    inject_style()
    data = load_data()

    if "platform_started" not in st.session_state:
        st.session_state.platform_started = False
    if "entry_animation" not in st.session_state:
        st.session_state.entry_animation = False

    if not st.session_state.platform_started:
        show_welcome()
        return

    if st.session_state.entry_animation:
        show_entry_transition()

    page = sidebar_navigation()

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Les cours, examens et messages sont sauvegardes dans btsmtacademy_data.json."
    )

    if page == "Accueil":
        show_home(data)
    elif page == "Recherche rapide":
        show_search(data)
    elif page == "Dernieres mises a jour":
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
    else:
        show_contact(data)

    show_creator_footer()


if __name__ == "__main__":
    main()
