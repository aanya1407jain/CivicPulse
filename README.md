# 🗳️ CivicPulse — Global Election Intelligence Assistant

> *Empowering citizens worldwide to participate in democracy — one election at a time.*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.35+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Google APIs](https://img.shields.io/badge/Google%20APIs-Civic%20%7C%20Maps%20%7C%20Calendar-4285F4.svg)](https://console.cloud.google.com)

---

## 🎯 Chosen Vertical

**Civic Engagement & Education**

CivicPulse is a production-grade, multi-country election intelligence assistant that guides citizens through the full voter journey — from checking eligibility to casting their ballot — with real-time data, personalised checklists, and smart Google integrations.

---

## 🌍 Supported Countries & Regions

| Country | Flag | Election Body | Voting System |
|---------|------|---------------|---------------|
| United States | 🇺🇸 | FEC + State Boards | FPTP (Congressional) |
| United Kingdom | 🇬🇧 | Electoral Commission | FPTP / AMS / STV |
| India | 🇮🇳 | Election Commission of India | FPTP (EVM + VVPAT) |
| Canada | 🇨🇦 | Elections Canada | FPTP |
| Australia | 🇦🇺 | AEC | Preferential / STV |
| Germany | 🇩🇪 | Bundeswahlleiter | Mixed Member Proportional |
| Japan | 🇯🇵 | Ministry of Internal Affairs | Parallel Voting |
| Brazil | 🇧🇷 | TSE (Superior Electoral Court) | Two-Round Majority |
| Nigeria | 🇳🇬 | INEC | FPTP / Two-Round (President) |
| European Union | 🇪🇺 | European Parliament | Proportional Representation |

---

## 🧠 Approach and Logic

### Context-First Architecture

CivicPulse uses a **State-Modular Logic** design where the country and jurisdiction determine the entire workflow:

```
User Input (Country + Location)
        │
        ▼
┌───────────────────┐
│  Region Handler   │  ← Country-specific rules, dates, requirements
│  Factory Pattern  │
└───────────────────┘
        │
        ▼
┌────────────────────────────────────────────────┐
│               Election Data Layer               │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ Checklist│  │ Timeline │  │ Requirements │ │
│  └──────────┘  └──────────┘  └──────────────┘ │
└────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────┐
│              Google Services Layer              │
│  ┌────────┐  ┌────────┐  ┌────────────────┐  │
│  │ Civic  │  │  Maps  │  │    Calendar    │  │
│  │  API   │  │  API   │  │      API       │  │
│  └────────┘  └────────┘  └────────────────┘  │
└────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Abstract Base Handler** — `BaseRegionHandler` defines the contract every country must implement, ensuring consistent data structure across all 10+ regions.

2. **Factory Pattern** — `get_region_handler(country_code)` resolves the correct handler at runtime, making it trivial to add new countries.

3. **Graceful Degradation** — All Google API calls have fallback mechanisms. If an API key is missing or a rate limit is hit, the app displays informative demo data instead of crashing.

4. **Separation of Concerns** — UI components (Streamlit), election logic (region handlers), and API services (Google) are completely decoupled.

5. **Security-First** — API keys are loaded from environment variables. OAuth2 tokens are stored in Streamlit session state (not localStorage or cookies). No secrets are committed to version control.

---

## 🗂️ Project Structure

```
civicpulse/
├── app.py                          # Main Streamlit application entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── .streamlit/
│   └── config.toml                 # Streamlit theme configuration
│
├── config/
│   ├── __init__.py
│   └── settings.py                 # App config, API keys, country registry
│
├── regions/                        # Country-specific election logic
│   ├── __init__.py                 # Factory: get_region_handler()
│   ├── base.py                     # Abstract base handler + data classes
│   ├── generic.py                  # Fallback handler for unlisted countries
│   ├── us/
│   │   ├── __init__.py
│   │   ├── workflow.py             # US election handler (50 states)
│   │   └── states.py              # State-by-state election data
│   ├── uk/
│   │   ├── __init__.py
│   │   └── workflow.py             # UK handler (England, Scotland, Wales, NI)
│   ├── india/
│   │   ├── __init__.py
│   │   └── workflow.py             # India handler (ECI, EVM, VVPAT)
│   ├── canada/
│   │   ├── __init__.py
│   │   └── workflow.py             # Canada federal election handler
│   ├── australia/
│   │   ├── __init__.py
│   │   └── workflow.py             # Australia handler (compulsory voting)
│   ├── germany/
│   │   ├── __init__.py
│   │   └── workflow.py             # Germany MMP handler
│   ├── japan/
│   │   ├── __init__.py
│   │   └── workflow.py             # Japan parallel voting handler
│   ├── brazil/
│   │   ├── __init__.py
│   │   └── workflow.py             # Brazil handler (compulsory, two-round)
│   ├── nigeria/
│   │   ├── __init__.py
│   │   └── workflow.py             # Nigeria INEC + PVC handler
│   └── eu/
│       ├── __init__.py
│       └── workflow.py             # EU Parliament election handler
│
├── services/                       # Google API integrations
│   ├── __init__.py
│   ├── civic_api.py                # Google Civic Information API v2
│   ├── calendar_api.py             # Google Calendar API (reminders)
│   ├── maps_api.py                 # Google Maps Platform (routing)
│   └── google_auth.py              # OAuth2 authentication service
│
├── components/                     # Streamlit UI components
│   ├── __init__.py
│   ├── checklist.py                # Interactive voter checklist
│   ├── timeline.py                 # Election countdown timeline
│   ├── map_view.py                 # Polling station map view
│   └── notification.py             # Calendar & reminder panel
│
├── utils/                          # Shared utilities
│   ├── __init__.py
│   ├── date_utils.py               # Date parsing, countdown calculations
│   ├── location_utils.py           # Location detection & parsing
│   └── validators.py               # Input validation
│
├── data/
│   ├── elections/
│   │   └── global_elections_2025_2030.json
│   └── regions/
│       └── voting_requirements.json
│
├── tests/
│   ├── __init__.py
│   ├── test_region_handlers.py     # Region handler unit tests
│   └── test_services.py            # API service unit tests
│
└── docs/
    ├── ARCHITECTURE.md
    └── CONTRIBUTING.md
```

---

## 🚀 How to Run

### Prerequisites
- Python 3.11+
- Git
- Google Cloud account (for live API features)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/civicpulse.git
cd civicpulse
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your Google API keys
```

### 5. Run the application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 🔑 Google Services Integration

### APIs Used

| API | Purpose | Documentation |
|-----|---------|---------------|
| **Google Civic Information API** | Real-time polling places, candidates, election data | [docs](https://developers.google.com/civic-information) |
| **Google Calendar API** | Create election deadline reminders | [docs](https://developers.google.com/calendar) |
| **Google Maps Platform** | Polling station routing, geocoding, map embeds | [docs](https://developers.google.com/maps) |
| **Google Translate API** | Multi-language interface support | [docs](https://cloud.google.com/translate) |
| **Google OAuth2** | Secure calendar write access | [docs](https://developers.google.com/identity/protocols/oauth2) |

### Enabling APIs in Google Cloud Console
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create or select a project
3. Navigate to **APIs & Services → Library**
4. Enable: Civic Information API, Maps JavaScript API, Geocoding API, Calendar API, Cloud Translation API
5. Create credentials (API Key for public APIs, OAuth2 for Calendar)

---

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test files
python -m pytest tests/test_region_handlers.py -v
python -m pytest tests/test_services.py -v
```

---

## ♿ Accessibility

CivicPulse is designed with accessibility in mind:
- **WCAG 2.1 AA** colour contrast ratios throughout
- **Screen reader friendly** — semantic HTML structure
- **Keyboard navigable** — all interactive elements reachable via Tab
- **Multi-language support** — 7 languages via the sidebar selector
- **PwD voting information** — dedicated steps for voters with disabilities in each country handler

---

## 🔒 Security

- API keys loaded from environment variables (never hardcoded)
- OAuth2 tokens stored in Streamlit session state only
- No voter personal data is stored or transmitted
- All external API calls use HTTPS
- Input validation on all user-submitted location strings
- XSRF protection enabled in Streamlit config

---

## 📋 Assumptions Made

1. **Date accuracy**: Election dates for 2026–2029 are estimates based on constitutional schedules. Final dates depend on official government announcements.
2. **Polling station data**: Demo polling station data is used when Google Civic API keys are not configured. Live data requires a valid API key and is only available for US addresses.
3. **Language support**: Interface language selection is implemented in the UI — full translation requires Google Translate API integration.
4. **Calendar write access**: Adding events directly to Google Calendar requires the user to authenticate via OAuth2. The fallback (Google Calendar link) works without any sign-in.
5. **Compulsory voting**: Australia and Brazil are flagged as compulsory; fines and legal consequences are informational only.

---

## 🤝 Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ for democracy. CivicPulse v2.0 — Powered by Google Cloud.*