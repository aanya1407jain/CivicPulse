"""
CivicPulse — Dark Dashboard Theme
===================================
Matches the UI in the design screenshot:
- Dark navy/charcoal background
- Orange accent (saffron)  
- Top horizontal nav bar (not sidebar tabs)
- Stat tiles with large numbers
- Constituency card on the left
- Party strength horizontal bar
"""

DARK_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&family=Bebas+Neue&display=swap');

/* ── ROOT VARIABLES ───────────────────────────────────────────── */
:root {
    --bg:           #0D0F14;
    --bg2:          #141720;
    --bg3:          #1C2030;
    --bg4:          #242840;
    --card:         #181B26;
    --card2:        #1E2235;
    --border:       rgba(255,255,255,0.07);
    --border2:      rgba(255,255,255,0.12);
    --orange:       #FF6B1A;
    --orange-lt:    rgba(255,107,26,0.15);
    --orange-glow:  rgba(255,107,26,0.35);
    --green:        #27C96E;
    --green-lt:     rgba(39,201,110,0.12);
    --blue:         #4F8EF7;
    --blue-lt:      rgba(79,142,247,0.12);
    --yellow:       #F7C94F;
    --yellow-lt:    rgba(247,201,79,0.12);
    --red:          #F74F4F;
    --red-lt:       rgba(247,79,79,0.12);
    --text:         #E8EAF0;
    --text2:        #9BA3BC;
    --text3:        #5C6480;
    --aitc:         #27C96E;
    --bjp:          #FF6B1A;
    --others:       #9BA3BC;
    --font-body:    'DM Sans', system-ui, sans-serif;
    --font-mono:    'DM Mono', monospace;
    --font-display: 'Bebas Neue', sans-serif;
    --r-sm:  6px;
    --r-md:  10px;
    --r-lg:  16px;
    --r-xl:  22px;
}

/* ── APP SHELL ────────────────────────────────────────────────── */
.stApp {
    background: var(--bg) !important;
    font-family: var(--font-body) !important;
    color: var(--text) !important;
}
.stApp > header {
    background: transparent !important;
}
/* Remove default Streamlit padding */
.main .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}

/* ── HIDE SIDEBAR (we use top nav) ────────────────────────────── */
[data-testid="stSidebar"] {
    display: none !important;
}
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

/* ── ALL TEXT ──────────────────────────────────────────────────── */
.stApp, .stApp * {
    color: var(--text) !important;
}
.stMarkdown p, .stMarkdown span, .stMarkdown li {
    color: var(--text2) !important;
}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
}

/* ── TABS → styled as nav pills ─────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--r-md) !important;
    padding: 4px 6px !important;
    gap: 2px !important;
    flex-wrap: wrap !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: var(--r-sm) !important;
    color: var(--text3) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 7px 16px !important;
    letter-spacing: 0.02em !important;
    transition: all 0.18s ease !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: var(--orange) !important;
    color: #fff !important;
    box-shadow: 0 2px 12px var(--orange-glow) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.2rem !important;
    background: transparent !important;
}

/* ── METRICS ──────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--r-lg) !important;
    padding: 1.2rem 1.4rem !important;
}
[data-testid="stMetric"] label {
    color: var(--text3) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-weight: 700 !important;
    font-size: 1.8rem !important;
}
[data-testid="stMetricDelta"] {
    color: var(--green) !important;
    font-size: 0.78rem !important;
}

/* ── ALERTS ───────────────────────────────────────────────────── */
.stAlert {
    border-radius: var(--r-md) !important;
    border: none !important;
}
div[data-testid="stInfo"] {
    background: rgba(79,142,247,0.08) !important;
    border-left: 3px solid var(--blue) !important;
    color: var(--text2) !important;
}
div[data-testid="stSuccess"] {
    background: var(--green-lt) !important;
    border-left: 3px solid var(--green) !important;
}
div[data-testid="stWarning"] {
    background: var(--yellow-lt) !important;
    border-left: 3px solid var(--yellow) !important;
}
div[data-testid="stError"] {
    background: var(--red-lt) !important;
    border-left: 3px solid var(--red) !important;
}
div[data-testid="stInfo"] p,
div[data-testid="stSuccess"] p,
div[data-testid="stWarning"] p,
div[data-testid="stError"] p { color: var(--text2) !important; }

/* ── BUTTONS ──────────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: var(--orange) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--r-sm) !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    box-shadow: 0 2px 12px var(--orange-glow) !important;
    transition: all 0.18s !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px var(--orange-glow) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--bg3) !important;
    color: var(--text2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--r-sm) !important;
    font-weight: 600 !important;
}
.stLinkButton a {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text2) !important;
    border-radius: var(--r-sm) !important;
    font-weight: 600 !important;
}
.stLinkButton a:hover {
    background: var(--orange-lt) !important;
    border-color: var(--orange) !important;
    color: var(--orange) !important;
}

/* ── INPUTS ───────────────────────────────────────────────────── */
.stTextInput input, .stSelectbox select,
.stNumberInput input, .stTextArea textarea {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--orange) !important;
    box-shadow: 0 0 0 2px var(--orange-glow) !important;
}
.stTextInput input::placeholder { color: var(--text3) !important; }

/* ── PROGRESS BAR ─────────────────────────────────────────────── */
.stProgress > div > div {
    background: var(--orange) !important;
    border-radius: 99px !important;
}
.stProgress > div {
    background: var(--bg3) !important;
    border-radius: 99px !important;
}

/* ── SLIDER ───────────────────────────────────────────────────── */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--orange) !important;
}

/* ── RADIO / CHECKBOX ─────────────────────────────────────────── */
.stRadio label span, .stCheckbox label span {
    color: var(--text2) !important;
}

/* ── EXPANDER ─────────────────────────────────────────────────── */
details {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--r-md) !important;
}
summary { color: var(--text2) !important; }

/* ── DIVIDER ──────────────────────────────────────────────────── */
hr {
    border-color: var(--border) !important;
    margin: 1.2rem 0 !important;
}

/* ── NUMBER INPUT ─────────────────────────────────────────────── */
[data-testid="stNumberInput"] input {
    background: var(--bg3) !important;
    border-color: var(--border2) !important;
    color: var(--text) !important;
}

/* ── SELECTBOX ─────────────────────────────────────────────────── */
[data-testid="stSelectbox"] [data-baseweb="select"] {
    background: var(--bg3) !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] * {
    background: var(--bg3) !important;
    color: var(--text) !important;
    border-color: var(--border2) !important;
}

/* ── CHAT ─────────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--r-md) !important;
}
[data-testid="stChatInput"] > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--r-md) !important;
}

/* ── CAPTION TEXT ─────────────────────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text3) !important;
    font-size: 0.78rem !important;
}

/* ── SCROLLBAR ────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--bg4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text3); }

/* ── PLOTLY CHART BACKGROUNDS ─────────────────────────────────── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ── TOP NAV BAR ─────────────────────────────────────────────── */
.cp-topnav {
    display: flex;
    align-items: center;
    gap: 0;
    background: var(--bg2);
    border: 1px solid var(--border2);
    border-radius: var(--r-lg);
    padding: 10px 16px;
    margin-bottom: 1.4rem;
    position: relative;
}
.cp-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-right: 24px;
    flex-shrink: 0;
}
.cp-logo-icon {
    width: 38px;
    height: 38px;
    background: var(--orange);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    font-weight: 900;
    color: #fff;
    font-family: var(--font-display);
    letter-spacing: 0.02em;
    box-shadow: 0 2px 12px var(--orange-glow);
}
.cp-logo-text { line-height: 1.15; }
.cp-logo-title {
    font-weight: 700;
    font-size: 0.92rem;
    color: var(--text) !important;
    letter-spacing: 0.01em;
}
.cp-logo-sub {
    font-size: 0.62rem;
    font-weight: 600;
    color: var(--orange) !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.cp-nav-pills {
    display: flex;
    gap: 4px;
    flex: 1;
    flex-wrap: wrap;
}
.cp-live-badge {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--red-lt);
    border: 1px solid rgba(247,79,79,0.3);
    border-radius: 99px;
    padding: 5px 14px;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--red) !important;
    letter-spacing: 0.06em;
    flex-shrink: 0;
}
.cp-live-dot {
    width: 7px;
    height: 7px;
    background: var(--red);
    border-radius: 50%;
    animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.2; }
}

/* ── SEARCH BAR ───────────────────────────────────────────────── */
.cp-search-row {
    display: flex;
    gap: 10px;
    align-items: center;
    background: var(--bg2);
    border: 1px solid var(--border2);
    border-radius: var(--r-md);
    padding: 10px 16px;
    margin-bottom: 1.2rem;
}
.cp-pin-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--orange) !important;
    white-space: nowrap;
    letter-spacing: 0.04em;
}
.cp-pin-label span {
    color: var(--orange) !important;
}

/* ── CONSTITUENCY CARD ─────────────────────────────────────────── */
.cp-constituency-card {
    background: var(--card);
    border: 1px solid var(--border2);
    border-radius: var(--r-xl);
    padding: 20px;
    height: 100%;
}
.cp-const-badge {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--orange) !important;
    margin-bottom: 6px;
}
.cp-const-name {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--text) !important;
    line-height: 1.1;
    margin-bottom: 4px;
    font-family: var(--font-body);
}
.cp-const-sub {
    font-size: 0.78rem;
    color: var(--text3) !important;
    margin-bottom: 16px;
}
.cp-party-chips {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 16px;
}
.cp-chip {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 99px;
    letter-spacing: 0.04em;
}
.cp-chip-aitc { background: rgba(39,201,110,0.18); color: #27C96E !important; border: 1px solid rgba(39,201,110,0.3); }
.cp-chip-bjp  { background: rgba(255,107,26,0.18); color: #FF8C44 !important; border: 1px solid rgba(255,107,26,0.3); }
.cp-chip-oth  { background: rgba(155,163,188,0.18); color: #9BA3BC !important; border: 1px solid rgba(155,163,188,0.3); }
.cp-menu-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border-radius: var(--r-sm);
    cursor: pointer;
    transition: background 0.15s;
    margin-bottom: 2px;
}
.cp-menu-item:hover { background: var(--bg3); }
.cp-menu-icon {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    flex-shrink: 0;
}
.cp-menu-text {
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text2) !important;
}

/* ── STAT TILES ───────────────────────────────────────────────── */
.cp-stat-tile {
    background: var(--card);
    border: 1px solid var(--border2);
    border-radius: var(--r-lg);
    padding: 18px 16px 14px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    min-height: 130px;
    position: relative;
    overflow: hidden;
}
.cp-stat-tile::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: var(--r-lg) var(--r-lg) 0 0;
}
.cp-tile-green::before  { background: var(--green); }
.cp-tile-blue::before   { background: var(--blue); }
.cp-tile-yellow::before { background: var(--yellow); }
.cp-tile-orange::before { background: var(--orange); }
.cp-stat-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text3) !important;
    margin-bottom: 8px;
}
.cp-stat-value {
    font-size: 2.6rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 6px;
    font-family: var(--font-body);
}
.cp-tile-green  .cp-stat-value { color: var(--green)  !important; }
.cp-tile-blue   .cp-stat-value { color: var(--blue)   !important; }
.cp-tile-yellow .cp-stat-value { color: var(--yellow) !important; }
.cp-tile-orange .cp-stat-value { color: var(--orange) !important; }
.cp-stat-sub {
    font-size: 0.7rem;
    color: var(--text3) !important;
}

/* ── PARTY STRENGTH SECTION ───────────────────────────────────── */
.cp-section-card {
    background: var(--card);
    border: 1px solid var(--border2);
    border-radius: var(--r-xl);
    padding: 20px 22px;
}
.cp-section-title {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text3) !important;
    margin-bottom: 16px;
}
.cp-party-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
}
.cp-party-name {
    width: 52px;
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text) !important;
    flex-shrink: 0;
}
.cp-bar-wrap {
    flex: 1;
    height: 10px;
    background: var(--bg3);
    border-radius: 99px;
    overflow: visible;
    position: relative;
}
.cp-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.6s ease;
}
.cp-bar-seats {
    font-size: 0.78rem;
    font-weight: 700;
    width: 72px;
    text-align: right;
    flex-shrink: 0;
}
.cp-majority-line {
    text-align: center;
    font-size: 0.68rem;
    color: var(--red) !important;
    font-weight: 700;
    letter-spacing: 0.06em;
    margin-top: 4px;
    padding: 5px;
    border: 1px dashed rgba(247,79,79,0.4);
    border-radius: var(--r-sm);
}

/* ── EXIT POLL TABLE ──────────────────────────────────────────── */
.cp-poll-table {
    width: 100%;
    border-collapse: collapse;
}
.cp-poll-table th {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text3) !important;
    padding: 6px 10px;
    text-align: right;
    border-bottom: 1px solid var(--border);
}
.cp-poll-table th:first-child { text-align: left; }
.cp-poll-table td {
    padding: 8px 10px;
    font-size: 0.85rem;
    border-bottom: 1px solid var(--border);
    text-align: right;
}
.cp-poll-table td:first-child { text-align: left; color: var(--text2) !important; }
.cp-poll-table .val-aitc  { color: var(--green)  !important; font-weight: 700; }
.cp-poll-table .val-bjp   { color: var(--orange) !important; font-weight: 700; }
.cp-poll-table .val-other { color: var(--text3)  !important; font-weight: 600; }
.cp-poll-avg-row td {
    background: var(--bg3) !important;
    font-weight: 700;
    border-radius: 0;
}

/* ── ECI FOOTER STRIP ────────────────────────────────────────── */
.cp-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    font-size: 0.7rem;
    color: var(--text3) !important;
    border-top: 1px solid var(--border);
    margin-top: 1rem;
}
.cp-footer a { color: var(--orange) !important; text-decoration: none; }
</style>
"""

# ── ACCESSIBILITY ADDITIONS ────────────────────────────────────────────────────
ACCESSIBILITY_CSS = """
<style>
/* Skip-to-main-content link — always visible at top */
.cp-skip-link {
    display: block;
    position: fixed;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    background: #FF6B1A;
    color: #fff !important;
    padding: 6px 20px;
    border-radius: 0 0 8px 8px;
    font-weight: 700;
    font-size: 0.82rem;
    text-decoration: none;
    letter-spacing: 0.03em;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}
.cp-skip-link:focus {
    outline: 3px solid #fff;
    outline-offset: 2px;
}

/* High-contrast focus rings on all interactive elements */
a:focus-visible,
button:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible,
[tabindex]:focus-visible {
    outline: 3px solid #FF6B1A !important;
    outline-offset: 2px !important;
    box-shadow: none !important;
}

/* Status text labels alongside coloured indicators */
.cp-status-text {
    font-size: 0.72rem;
    font-weight: 600;
    margin-left: 6px;
    color: inherit;
}

/* Visually-hidden utility (screen readers only) */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0,0,0,0);
    white-space: nowrap;
    border: 0;
}
</style>
"""

SKIP_LINK_HTML = """
<a href="#main-content" class="cp-skip-link">Skip to main content</a>
<div id="main-content" tabindex="-1"></div>
"""
