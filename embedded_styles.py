# Auto-generated from assets/styles.css. Do not edit by hand.

def get_embedded_styles():
    return '''/* BTS SMARTCAMPUS - stable academic interface */
:root {
    --bts-navy: #06265a;
    --bts-navy-2: #031a3d;
    --bts-blue: #1677ff;
    --bts-sky: #5db5ff;
    --bts-gold: #f5bf3d;
    --bts-purple: #7137e8;
    --bts-teal: #0aa889;
    --bts-orange: #ff6a1a;
    --bts-pink: #e93580;
    --bts-ink: #071d45;
    --bts-muted: #587094;
    --bts-line: #dbe6f6;
    --bts-bg: #eef4fb;
    --bts-card: #ffffff;
    --bts-radius: 18px;
    --bts-shadow: 0 18px 50px rgba(6, 38, 90, 0.10);
    --bts-soft-shadow: 0 10px 28px rgba(6, 38, 90, 0.08);
}

html,
body,
.stApp {
    background: var(--bts-bg) !important;
    color: var(--bts-ink) !important;
    font-family: Inter, "Segoe UI", Arial, sans-serif !important;
}

* {
    box-sizing: border-box;
    letter-spacing: 0 !important;
    hyphens: none !important;
}

p,
span,
small,
strong,
b,
h1,
h2,
h3,
h4,
label,
button,
a,
div {
    word-break: normal !important;
    overflow-wrap: normal !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
}

#MainMenu,
footer {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 12% 6%, rgba(22, 119, 255, 0.10), transparent 28%),
        radial-gradient(circle at 85% 12%, rgba(10, 168, 137, 0.10), transparent 30%),
        linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%) !important;
}

[data-testid="stMain"],
.main {
    background: transparent !important;
    min-width: 0 !important;
}

.block-container,
[data-testid="stMainBlockContainer"] {
    width: min(1180px, calc(100vw - 48px)) !important;
    max-width: 1180px !important;
    margin: 0 auto !important;
    padding: 46px 0 72px !important;
}

section[data-testid="stSidebar"] {
    width: 270px !important;
    min-width: 270px !important;
    max-width: 270px !important;
    background: linear-gradient(180deg, #06285f 0%, #031735 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.10) !important;
    box-shadow: 18px 0 45px rgba(6, 38, 90, 0.16) !important;
}

section[data-testid="stSidebar"] > div {
    background: transparent !important;
    padding: 28px 16px 24px !important;
}

section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] small {
    color: rgba(255, 255, 255, 0.92) !important;
    white-space: normal !important;
}

.academic-sidebar-brand {
    text-align: center;
    padding: 12px 8px 26px;
}

.academic-sidebar-crest,
.platform-login-crest,
.welcome-brand-mark,
.sidebar-study-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 70px;
    height: 70px;
    border-radius: 22px;
    border: 2px solid rgba(255, 255, 255, 0.75);
    color: #fff !important;
    font-size: 22px;
    font-weight: 900;
    background: rgba(255, 255, 255, 0.08);
}

.academic-sidebar-brand h2 {
    margin: 16px 0 4px !important;
    color: #fff !important;
    font-size: 24px !important;
    line-height: 1.05 !important;
    font-weight: 900 !important;
}

.academic-sidebar-brand h2 span,
.brand-blue,
.welcome-brand-main span,
.platform-login-brand-text span,
.academic-dashboard-hero h1 span {
    color: var(--bts-blue) !important;
}

.academic-sidebar-brand p,
.academic-sidebar-label {
    color: rgba(255, 255, 255, 0.68) !important;
    font-size: 12px !important;
    font-weight: 800 !important;
    text-transform: uppercase;
}

.academic-sidebar-label {
    margin: 12px 12px 10px;
    text-align: left;
}

section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    width: 100% !important;
    min-height: 52px !important;
    justify-content: flex-start !important;
    border-radius: 10px !important;
    border: 0 !important;
    padding: 0 16px !important;
    margin: 4px 0 !important;
    background: transparent !important;
    color: rgba(255, 255, 255, 0.92) !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"],
section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #1677ff 0%, #0c5ee8 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 12px 28px rgba(22, 119, 255, 0.28) !important;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.14) !important;
}

.sidebar-study-card {
    margin: 28px 8px 18px;
    padding: 18px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.16);
}

.sidebar-study-card strong {
    display: block;
    margin: 12px 0;
    color: #fff !important;
    font-size: 14px;
    line-height: 1.45;
}

.sidebar-progress {
    height: 8px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.12);
    overflow: hidden;
    margin: 12px 0;
}

.sidebar-progress span {
    display: block;
    width: 62%;
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, #5ee7ff, #1677ff);
}

button[data-testid="collapsedControl"],
[data-testid="collapsedControl"],
div[data-testid="stSidebarCollapsedControl"] button,
button[title="Open sidebar"],
button[title="Close sidebar"],
button[aria-label="Open sidebar"],
button[aria-label="Close sidebar"],
header button[aria-label*="sidebar" i],
header button[title*="sidebar" i] {
    display: inline-flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    z-index: 999999 !important;
    top: 18px !important;
    left: 18px !important;
    width: 48px !important;
    height: 48px !important;
    min-width: 48px !important;
    min-height: 48px !important;
    align-items: center !important;
    justify-content: center !important;
    border-radius: 14px !important;
    background: #ffffff !important;
    color: var(--bts-navy) !important;
    border: 1px solid var(--bts-line) !important;
    box-shadow: 0 12px 28px rgba(6, 38, 90, 0.16) !important;
}

button[data-testid="collapsedControl"] svg,
[data-testid="collapsedControl"] svg,
div[data-testid="stSidebarCollapsedControl"] button svg,
header button[aria-label*="sidebar" i] svg,
header button[title*="sidebar" i] svg {
    width: 24px !important;
    height: 24px !important;
    color: var(--bts-navy) !important;
    stroke: var(--bts-navy) !important;
}

.stButton > button,
.stDownloadButton > button,
a[data-testid="stLinkButton"] {
    border-radius: 10px !important;
    border: 1px solid var(--bts-line) !important;
    background: #ffffff !important;
    color: #0b5ff4 !important;
    min-height: 44px !important;
    font-weight: 800 !important;
    box-shadow: 0 8px 20px rgba(6, 38, 90, 0.06) !important;
    white-space: normal !important;
}

.stButton > button[kind="primary"],
.stFormSubmitButton > button,
a[data-testid="stLinkButton"]:hover {
    background: linear-gradient(135deg, #0b61ff 0%, #1677ff 100%) !important;
    color: #ffffff !important;
    border-color: transparent !important;
}

input,
textarea,
select,
[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border-color: #cad7ea !important;
    background: #fbfdff !important;
    color: var(--bts-ink) !important;
}

.platform-login-shell,
.welcome-shell,
.welcome-topbar,
.welcome-hero,
.welcome-copy,
.academic-dashboard-userbar,
.academic-dashboard-topbar,
.academic-dashboard-hero,
.courses-hero,
.files-hero,
.exam-page-shell,
.planning-shell,
.contact-topbar,
.app-topbar,
.drive-filter-shell,
.drive-list-shell,
.card,
.course-row,
.exam-card,
.planning-card {
    animation: fadeIn 0.35s ease both;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

.creator-footer {
    margin: 46px 0 0;
    padding-top: 22px;
    border-top: 1px solid var(--bts-line);
    text-align: right;
    color: var(--bts-muted);
    font-weight: 700;
}

.creator-footer strong {
    color: #0b61ff !important;
}

/* Login */
.platform-login-shell {
    overflow: hidden;
    border: 1px solid var(--bts-line);
    border-radius: 8px;
    background: #ffffff;
    box-shadow: var(--bts-shadow);
}

.platform-login-top {
    height: 96px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 42px;
    background: #fff;
}

.login-topbar,
.contact-topbar,
.academic-dashboard-topbar {
    min-height: 78px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    margin-bottom: 26px;
    padding: 18px 24px;
}

.login-brand,
.contact-brand,
.academic-dashboard-brand {
    color: var(--bts-navy) !important;
    font-size: 22px;
    font-weight: 950;
}

.login-brand span,
.contact-brand span,
.academic-dashboard-brand span {
    color: var(--bts-blue) !important;
}

.login-user,
.contact-user,
.academic-dashboard-user {
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--bts-ink) !important;
    font-weight: 800;
}

.login-avatar,
.contact-avatar {
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: var(--bts-navy);
}

.platform-login-brand,
.welcome-brand {
    display: flex;
    align-items: center;
    gap: 18px;
}

.platform-login-crest {
    width: 58px;
    height: 58px;
    border-color: var(--bts-navy);
    color: var(--bts-navy) !important;
    background: #f5f9ff;
}

.platform-login-brand-text,
.welcome-brand-main {
    color: var(--bts-navy) !important;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 30px;
    font-weight: 900;
}

.platform-login-actions {
    display: flex;
    align-items: center;
    gap: 14px;
}

.platform-login-pill {
    padding: 14px 22px;
    border-radius: 6px;
    background: var(--bts-navy);
    color: #fff !important;
    font-weight: 800;
}

.platform-login-help {
    width: 42px;
    height: 42px;
    display: grid;
    place-items: center;
    border: 1px solid #9cb4d7;
    border-radius: 6px;
    color: var(--bts-navy) !important;
    font-weight: 900;
}

.platform-login-hero {
    display: grid;
    grid-template-columns: 1.05fr 0.95fr;
    min-height: 430px;
    background:
        linear-gradient(110deg, rgba(4, 24, 57, 0.98) 0%, rgba(8, 49, 100, 0.96) 52%, rgba(142, 170, 211, 0.82) 52.2%, rgba(190, 210, 238, 0.92) 100%);
}

.platform-login-copy {
    padding: 96px 78px;
    color: #fff !important;
}

.platform-login-copy h1,
.platform-login-copy h1 span {
    color: #fff !important;
    font-family: Georgia, "Times New Roman", serif;
    font-size: clamp(38px, 5vw, 58px);
    line-height: 1.12;
    margin: 0;
}

.platform-login-copy h1 span {
    color: #4da0ff !important;
}

.platform-login-gold-line,
.welcome-gold-line,
.dashboard-gold-line {
    width: 72px;
    height: 4px;
    border-radius: 4px;
    background: var(--bts-gold);
    margin: 24px 0;
}

.platform-login-copy p {
    max-width: 540px;
    color: #eef5ff !important;
    font-size: 19px;
    line-height: 1.55;
    font-weight: 650;
}

.platform-login-card {
    align-self: center;
    justify-self: center;
    width: min(420px, 82%);
    min-height: 230px;
    border-radius: 8px;
    padding: 34px;
    text-align: center;
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid rgba(255, 255, 255, 0.8);
    box-shadow: 0 24px 70px rgba(6, 38, 90, 0.20);
}

.platform-login-card-icon,
.platform-login-card-title {
    color: var(--bts-navy) !important;
}

.platform-login-card-icon {
    font-size: 38px;
    margin-bottom: 16px;
}

.platform-login-card-title {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 31px;
    font-weight: 900;
}

.platform-login-card-line {
    width: 70px;
    height: 3px;
    border-radius: 3px;
    margin: 16px auto;
    background: var(--bts-gold);
}

.platform-login-card-subtitle {
    color: #5b6680 !important;
    font-weight: 700;
}

.platform-login-note {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 28px 0 0;
    padding: 18px 22px;
    border: 1px solid #b6d1ff;
    border-radius: 8px;
    background: #f2f7ff;
    color: var(--bts-navy) !important;
    font-weight: 700;
}

.platform-login-note span:first-child {
    width: 28px;
    height: 28px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    border: 2px solid #0b61ff;
    color: #0b61ff !important;
}

/* Welcome */
.academic-welcome-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px 4px 28px;
}

.academic-welcome-crest {
    border-color: var(--bts-navy);
    color: var(--bts-navy) !important;
    background: #fff;
}

.welcome-brand-sub {
    display: block;
    margin-top: 4px;
    color: #61718f !important;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 3px !important;
}

.academic-welcome-panel {
    display: grid;
    grid-template-columns: 1.15fr 0.95fr;
    gap: 24px;
}

.academic-welcome-shell,
.welcome-shell {
    width: 100%;
}

.academic-welcome-brand {
    display: flex;
    align-items: center;
    gap: 18px;
}

.welcome-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
}

.welcome-brand-text {
    display: flex;
    flex-direction: column;
}

.welcome-hero {
    border-radius: 12px;
}

.welcome-start-panel {
    border: 1px solid #b6d1ff;
    border-radius: 12px;
    background: #f4f9ff;
}

.welcome-tags-outside {
    display: grid;
    gap: 18px;
}

.welcome-visual {
    min-width: 0;
}

.welcome-floating-badge,
.welcome-orbit {
    display: none !important;
}

.entry-transition-content,
.login-gateway-card,
.login-gateway-mark,
.login-gateway-dots {
    display: none !important;
}

.academic-welcome-copy {
    min-height: 580px;
    padding: 58px 52px;
    border-radius: 8px;
    color: #fff !important;
    background:
        linear-gradient(135deg, rgba(3, 24, 56, 0.98), rgba(6, 55, 120, 0.96)),
        radial-gradient(circle at 78% 28%, rgba(93, 181, 255, 0.22), transparent 30%);
    box-shadow: var(--bts-shadow);
}

.welcome-eyebrow {
    display: inline-flex;
    padding: 12px 18px;
    border-radius: 999px;
    background: rgba(22, 119, 255, 0.75);
    color: #fff !important;
    font-weight: 900;
    font-size: 13px;
}

.academic-welcome-copy h1,
.academic-welcome-copy h1 span {
    color: #fff !important;
    font-family: Georgia, "Times New Roman", serif;
    font-size: clamp(44px, 5vw, 64px);
    line-height: 1.1;
}

.academic-welcome-copy h1 span {
    color: #69b5ff !important;
}

.academic-welcome-copy p {
    color: #f1f6ff !important;
    font-size: 18px;
    line-height: 1.75;
    font-weight: 600;
}

.welcome-feature-row {
    display: flex;
    flex-wrap: wrap;
    gap: 18px;
    margin-top: 34px;
}

.welcome-feature {
    color: #fff !important;
    font-weight: 800;
}

.academic-welcome-grid {
    display: grid;
    gap: 16px;
}

.welcome-mini-card,
.welcome-tag,
.dashboard-card,
.dash-panel,
.subject-card,
.drive-stat-card,
.drive-file-row {
    border: 1px solid var(--bts-line);
    background: rgba(255, 255, 255, 0.96);
    box-shadow: var(--bts-soft-shadow);
}

.welcome-mini-card {
    min-height: 125px;
    display: grid;
    grid-template-columns: 84px 1fr;
    align-items: center;
    gap: 22px;
    padding: 24px;
    border-radius: 12px;
}

.welcome-mini-card strong {
    display: grid;
    place-items: center;
    width: 72px;
    height: 72px;
    border-radius: 10px;
    color: #fff !important;
    background: linear-gradient(135deg, #0b61ff, #1677ff);
    font-size: 24px;
}

.mini-examens strong { background: linear-gradient(135deg, #7c3aed, #5b21b6); }
.mini-drive strong { background: linear-gradient(135deg, #0aa889, #007e71); }
.mini-profs strong { background: linear-gradient(135deg, #e93580, #c2185b); }

.welcome-mini-card span,
.welcome-mini-card b {
    color: var(--bts-ink) !important;
}

.welcome-mini-card b {
    display: block;
    font-size: 18px;
    margin-bottom: 8px;
}

.academic-welcome-start-panel {
    margin: 28px 0 16px;
    padding: 22px 28px;
    border: 1px solid #b6d1ff;
    border-radius: 10px;
    background: #f4f9ff;
}

.academic-welcome-start-panel strong {
    display: block;
    color: var(--bts-navy) !important;
    font-size: 24px;
}

.academic-welcome-start-panel span {
    color: var(--bts-muted) !important;
    font-weight: 700;
}

.academic-welcome-links {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 22px;
    margin-top: 26px;
}

.welcome-tag {
    min-height: 170px;
    border-radius: 12px;
    padding: 28px;
    text-align: center;
    border-bottom: 4px solid #1677ff;
}

.welcome-tag b,
.welcome-tag small {
    display: block;
    color: var(--bts-navy) !important;
}

.welcome-tag b {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 20px;
}

.welcome-tag small {
    margin-top: 12px;
    color: var(--bts-muted) !important;
    font-size: 15px;
}

.tag-ressources { border-bottom-color: var(--bts-purple); }
.tag-examens { border-bottom-color: var(--bts-teal); }
.tag-direction { border-bottom-color: var(--bts-pink); }

/* Dashboard */
.academic-dashboard-userbar {
    min-height: 84px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
    padding: 18px 26px;
    border: 1px solid var(--bts-line);
    border-radius: 12px;
    background: #fff;
    box-shadow: var(--bts-soft-shadow);
}

.academic-dashboard-user {
    display: flex;
    align-items: center;
    gap: 14px;
    color: var(--bts-ink) !important;
    font-weight: 800;
}

.academic-dashboard-user span {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    color: var(--bts-muted) !important;
}

.academic-dashboard-user strong {
    color: var(--bts-ink) !important;
}

.academic-dashboard-user b {
    display: grid;
    place-items: center;
    width: 52px;
    height: 52px;
    border-radius: 50%;
    color: #fff !important;
    background: var(--bts-navy);
}

.contact-hero,
.login-intro {
    margin-bottom: 26px;
    padding: 34px;
    border-radius: 12px;
    background: linear-gradient(135deg, #08275a, #0b3b86);
    color: #ffffff !important;
    box-shadow: var(--bts-shadow);
}

.contact-title-wrap,
.files-title-wrap,
.drive-title-wrap,
.planning-title-wrap,
.exam-card-head,
.shared-file-head {
    display: flex;
    align-items: center;
    gap: 18px;
}

.contact-hero h1,
.login-intro h1 {
    margin: 0 0 10px;
    color: #ffffff !important;
    font-size: 34px;
}

.contact-hero p,
.login-intro p {
    color: #eef6ff !important;
    font-weight: 650;
}

.contact-form-title,
.contact-help {
    margin: 16px 0;
    padding: 20px;
    border: 1px solid var(--bts-line);
    border-radius: 12px;
    background: #ffffff;
    box-shadow: var(--bts-soft-shadow);
}

.contact-help {
    display: flex;
    align-items: center;
    gap: 16px;
    color: var(--bts-muted) !important;
    font-weight: 750;
}

.contact-help-icon,
.files-icon,
.drive-folder-icon,
.exam-icon-main,
.planning-icon-main,
.shared-file-icon,
.university-announcement-icon,
.university-feature-icon {
    display: grid;
    place-items: center;
    width: 62px;
    height: 62px;
    flex: 0 0 auto;
    border-radius: 14px;
    color: #ffffff !important;
    background: linear-gradient(135deg, #1677ff, #0b61ff);
    font-weight: 900;
    font-size: 22px;
}

.login-visual,
.login-visual-card,
.contact-art {
    min-height: 120px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.08);
}

.login-line {
    width: 72px;
    height: 4px;
    margin-top: 18px;
    border-radius: 4px;
    background: var(--bts-gold);
}

.academic-dashboard-hero,
.courses-hero,
.files-hero,
.exam-hero,
.planning-hero {
    position: relative;
    overflow: hidden;
    min-height: 285px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    padding: 54px 62px;
    border-radius: 12px;
    background:
        repeating-radial-gradient(circle at 88% 20%, rgba(255, 255, 255, 0.17) 0 1px, transparent 2px 18px),
        linear-gradient(135deg, #08275a 0%, #0b3b86 56%, #1677ff 100%);
    box-shadow: var(--bts-shadow);
    color: #fff !important;
}

.academic-dashboard-hero h1,
.courses-hero h1,
.files-hero h1,
.exam-hero h1,
.planning-hero h1 {
    color: #fff !important;
    font-family: Georgia, "Times New Roman", serif;
    font-size: clamp(34px, 4.6vw, 56px);
    line-height: 1.12;
    margin: 0;
}

.academic-dashboard-hero p,
.courses-hero p,
.files-hero p,
.exam-hero p,
.planning-hero p {
    max-width: 560px;
    color: #eef6ff !important;
    font-size: 18px;
    line-height: 1.55;
    font-weight: 650;
}

.academic-dashboard-illustration,
.courses-hero-art,
.files-art,
.planning-art {
    width: 270px;
    height: 180px;
    border-radius: 22px;
    background:
        radial-gradient(circle at 60% 35%, rgba(255, 255, 255, 0.22), transparent 32%),
        rgba(255, 255, 255, 0.08);
    opacity: 0.9;
}

.dashboard-stat-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 18px;
    margin: 28px 0;
}

.dashboard-stat {
    min-height: 150px;
    padding: 22px;
    border-radius: 12px;
    border: 1px solid var(--bts-line);
    background: #ffffff;
    box-shadow: var(--bts-soft-shadow);
    display: grid;
    grid-template-columns: 64px minmax(0, 1fr);
    gap: 18px;
    align-items: center;
}

.dashboard-stat .stat-icon {
    display: grid;
    place-items: center;
    width: 58px;
    height: 58px;
    border-radius: 12px;
    color: #ffffff !important;
    background: linear-gradient(135deg, #1677ff, #0b61ff);
    font-size: 22px;
    font-weight: 900;
    box-shadow: 0 14px 30px rgba(22, 119, 255, 0.20);
}

.dashboard-stat.stat-teal .stat-icon { background: linear-gradient(135deg, #7c3aed, #5b21b6); }
.dashboard-stat.stat-amber .stat-icon { background: linear-gradient(135deg, #0aa889, #007e71); }
.dashboard-stat.stat-violet .stat-icon { background: linear-gradient(135deg, #ff6a1a, #ea580c); }

.dashboard-stat .label {
    color: var(--bts-ink) !important;
    font-size: 13px;
    font-weight: 900;
    text-transform: uppercase;
}

.dashboard-stat .value {
    margin-top: 8px;
    color: var(--bts-ink) !important;
    font-size: 34px;
    line-height: 1;
    font-weight: 950;
}

.dashboard-stat .hint {
    margin-top: 8px;
    color: var(--bts-muted) !important;
    font-weight: 750;
}

.dashboard-card {
    min-height: 150px;
    padding: 22px;
    border-radius: 12px;
    display: grid;
    grid-template-columns: 64px 1fr;
    gap: 18px;
    align-items: center;
}

.dashboard-card-icon,
.drive-stat-card span,
.subject-icon,
.exam-card-icon,
.planning-card-icon {
    display: grid;
    place-items: center;
    width: 58px;
    height: 58px;
    border-radius: 12px;
    color: #fff !important;
    background: linear-gradient(135deg, #1677ff, #0b61ff);
    font-weight: 900;
    font-size: 22px;
}

.dashboard-card h3,
.drive-stat-card b {
    margin: 0 0 8px;
    color: var(--bts-ink) !important;
    font-size: 13px;
    font-weight: 900;
    text-transform: uppercase;
}

.dashboard-card strong,
.drive-stat-card strong {
    display: block;
    color: var(--bts-ink) !important;
    font-size: 34px;
    line-height: 1;
}

.dashboard-card p,
.drive-stat-card small {
    margin: 8px 0 0;
    color: var(--bts-muted) !important;
    font-weight: 700;
}

.dash-panel-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 22px;
    margin-top: 22px;
}

.dashboard-list-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 22px;
    margin-top: 22px;
}

.dash-panel {
    min-height: 250px;
    padding: 26px;
    border-radius: 12px;
}

.dash-panel h3 {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 0 18px;
    color: var(--bts-ink) !important;
    font-size: 22px;
    line-height: 1.2;
}

.dash-panel h3 span {
    display: grid;
    place-items: center;
    flex: 0 0 auto;
    width: 42px;
    height: 42px;
    border-radius: 10px;
    background: #eef5ff;
    color: #0b61ff !important;
    font-weight: 900;
}

.dash-empty,
.dash-empty-row,
.planning-empty {
    padding: 22px;
    border-radius: 10px;
    background: #f1f6ff;
    color: #4b6388 !important;
    font-weight: 800;
    text-align: center;
}

.dash-list-row,
.dash-exam-row,
.dash-file-row,
.dash-announcement-row,
.dash-message-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    padding: 14px 0;
    border-bottom: 1px solid #edf2fa;
}

.dash-list-row strong,
.dash-list-row small,
.dash-list-row em,
.dash-list-row time {
    display: block;
}

.dash-list-row strong {
    color: var(--bts-ink) !important;
    font-size: 15px;
    line-height: 1.35;
}

.dash-list-row small,
.dash-list-row em {
    color: var(--bts-muted) !important;
    font-size: 13px;
    font-weight: 700;
    font-style: normal;
}

.dash-file-badge,
.dash-message-row > span {
    flex: 0 0 auto;
    display: grid;
    place-items: center;
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: #eef5ff;
    color: #0b61ff !important;
    font-weight: 900;
}

.academic-empty-card,
.academic-section-title,
.synced-page-hero,
.contact-topbar,
.login-topbar {
    border: 1px solid var(--bts-line);
    background: #ffffff;
    box-shadow: var(--bts-soft-shadow);
    border-radius: 12px;
}

.academic-empty-card {
    min-height: 118px;
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 24px;
    color: var(--bts-muted) !important;
    font-weight: 800;
}

.academic-empty-card span,
.academic-section-title span,
.synced-page-icon,
.contact-icon,
.login-icon {
    display: grid;
    place-items: center;
    width: 54px;
    height: 54px;
    flex: 0 0 auto;
    border-radius: 12px;
    background: #eef5ff;
    color: #0b61ff !important;
    font-weight: 900;
}

.academic-section-title {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 26px 0 16px;
    padding: 18px 20px;
}

.academic-section-title h3 {
    margin: 0;
    color: var(--bts-ink) !important;
}

.synced-page-hero {
    display: flex;
    align-items: center;
    gap: 22px;
    margin-bottom: 26px;
    padding: 28px;
}

.synced-page-hero h1 {
    margin: 0 0 8px;
    color: var(--bts-ink) !important;
    font-size: 34px;
}

.synced-page-hero p {
    margin: 0;
    color: var(--bts-muted) !important;
    font-weight: 700;
}

/* Generic pages */
.courses-hero,
.files-hero,
.exam-hero,
.planning-hero {
    margin-bottom: 26px;
}

.subject-card {
    min-height: 170px;
    display: grid;
    grid-template-columns: 64px 1fr;
    gap: 18px;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 10px;
}

.subject-icon {
    background: var(--subject-color, #1677ff);
}

.subject-card strong,
.course-row h3,
.card h3,
.exam-card h3,
.planning-card h3,
.drive-file-title {
    color: var(--bts-ink) !important;
    font-size: 18px;
    line-height: 1.28;
}

.exam-action-wrap {
    margin: -6px 0 18px;
}

.subject-card-button-space {
    display: none;
}

.shared-file-preview-frame {
    width: 100%;
    min-height: 360px;
    border: 1px solid var(--bts-line);
    border-radius: 12px;
    background: #f8fbff;
}

.subject-count,
.subject-action,
.subject-label,
.muted,
.exam-meta,
.exam-description,
.planning-date,
.drive-file-meta,
.drive-file-description {
    color: var(--bts-muted) !important;
    font-weight: 700;
    line-height: 1.45;
}

.subject-action {
    margin-top: 12px;
    font-size: 12px;
    color: var(--bts-navy) !important;
    text-transform: uppercase;
}

.card,
.course-row,
.exam-card,
.planning-card {
    margin: 16px 0;
    padding: 24px;
    border-radius: 12px;
}

.badge,
.badge-new,
.drive-file-type {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 26px;
    padding: 5px 10px;
    border-radius: 999px;
    background: #eef5ff;
    color: #0b61ff !important;
    font-size: 12px;
    font-weight: 900;
}

.badge-new {
    background: #fff5df;
    color: #b87500 !important;
}

.drive-stat-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
    margin-bottom: 22px;
}

.drive-stat-card {
    min-height: 110px;
    display: grid;
    grid-template-columns: 64px 1fr;
    gap: 18px;
    align-items: center;
    padding: 22px;
    border-radius: 12px;
}

.stat-teal span { background: linear-gradient(135deg, #7c3aed, #5b21b6); }
.stat-amber span { background: linear-gradient(135deg, #0aa889, #007e71); }

.drive-filter-shell,
.drive-list-shell {
    margin: 20px 0;
    padding: 24px;
    border-radius: 12px;
    border: 1px solid var(--bts-line);
    background: #fff;
    box-shadow: var(--bts-soft-shadow);
}

.drive-file-card-shell {
    margin: 18px 0;
    padding: 0;
    border-radius: 12px;
    border: 1px solid var(--bts-line);
    background: #ffffff;
    box-shadow: var(--bts-soft-shadow);
    overflow: hidden;
}

.drive-list-head {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    align-items: center;
}

.drive-filter-shell h3,
.drive-list-shell h3 {
    margin: 0;
    color: var(--bts-ink) !important;
}

.drive-file-row {
    display: grid;
    grid-template-columns: 70px minmax(0, 1fr) auto;
    gap: 18px;
    align-items: center;
    padding: 18px 0;
    border: 0;
    border-bottom: 1px solid #edf2fa;
    box-shadow: none;
    background: transparent;
}

.drive-file-type {
    width: 56px;
    height: 56px;
    border-radius: 10px;
    background: #e21d2f;
    color: #fff !important;
}

.drive-file-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: flex-end;
}

.drive-file-info {
    min-width: 0;
}

.drive-file-title {
    font-weight: 900;
}

.drive-file-size {
    color: var(--bts-muted) !important;
    font-weight: 800;
}

.shared-file-card,
.message,
.homework-card,
.university-announcement,
.university-feature-card {
    margin: 16px 0;
    padding: 22px;
    border: 1px solid var(--bts-line);
    border-radius: 12px;
    background: #ffffff;
    box-shadow: var(--bts-soft-shadow);
}

.message-title,
.message-content,
.message-meta,
.shared-file-meta {
    color: var(--bts-ink) !important;
    line-height: 1.5;
}

.message-meta,
.shared-file-meta {
    color: var(--bts-muted) !important;
    font-size: 13px;
    font-weight: 750;
}

.section-title {
    margin: 28px 0 14px;
    color: var(--bts-ink) !important;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 24px;
    font-weight: 900;
}

/* Streamlit forms and tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 22px;
    border-bottom: 1px solid var(--bts-line);
}

.stTabs [data-baseweb="tab"] {
    color: var(--bts-muted) !important;
    font-weight: 800 !important;
}

.stTabs [aria-selected="true"] {
    color: #0b61ff !important;
}

[data-testid="stForm"],
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
    border-color: var(--bts-line) !important;
    background: rgba(255, 255, 255, 0.92) !important;
    box-shadow: var(--bts-soft-shadow) !important;
}

.stAlert {
    border-radius: 10px !important;
}

pre,
code {
    white-space: pre-wrap !important;
    word-break: break-word !important;
}

/* Safety against old broken overlay classes. */
.entry-transition,
.login-gateway-transition {
    display: none !important;
}

@media (max-width: 980px) {
    .block-container,
    [data-testid="stMainBlockContainer"] {
        width: min(100%, calc(100vw - 24px)) !important;
        padding-top: 72px !important;
    }

    .platform-login-top,
    .platform-login-actions,
    .academic-welcome-topbar {
        flex-direction: column;
        height: auto;
        gap: 14px;
        align-items: flex-start;
        padding: 24px;
    }

    .platform-login-hero,
    .academic-welcome-panel,
    .dashboard-stat-grid,
    .dash-panel-grid,
    .drive-stat-grid,
    .academic-welcome-links {
        grid-template-columns: 1fr !important;
    }

    .platform-login-copy,
    .academic-welcome-copy,
    .academic-dashboard-hero,
    .courses-hero,
    .files-hero,
    .exam-hero,
    .planning-hero {
        padding: 34px 26px;
    }

    .academic-dashboard-hero,
    .courses-hero,
    .files-hero,
    .exam-hero,
    .planning-hero {
        flex-direction: column;
        align-items: flex-start;
    }

    .drive-file-row {
        grid-template-columns: 1fr;
    }

    .drive-file-actions {
        justify-content: flex-start;
    }
}

@media (max-width: 760px) {
    section[data-testid="stSidebar"] {
        width: 245px !important;
        min-width: 245px !important;
        max-width: 245px !important;
    }

    .platform-login-copy h1,
    .academic-welcome-copy h1,
    .academic-dashboard-hero h1 {
        font-size: 36px !important;
    }

    .dashboard-card,
    .drive-stat-card,
    .subject-card,
    .welcome-mini-card {
        grid-template-columns: 1fr;
    }
}
'''
