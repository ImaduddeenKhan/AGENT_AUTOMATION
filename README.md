<p align="center">
  <h1 align="center">Raptor Event Scout</h1>
  <p align="center">Autonomous AI agents that discover, rank, and register for high‑value tech events in Japan.</p>
  <p align="center"><strong>Built for fast business development in Osaka, Kobe, and Kyoto.</strong></p>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.8%2B-blue.svg" />
  <img alt="Build" src="https://img.shields.io/badge/Build-Manual-lightgrey.svg" />
  <img alt="Groq" src="https://img.shields.io/badge/LLM-Groq-green.svg" />
  <img alt="Supabase" src="https://img.shields.io/badge/Database-Supabase-orange.svg" />
  <img alt="Status" src="https://img.shields.io/badge/Status-Active-success.svg" />
  <img alt="License" src="https://img.shields.io/badge/License-All%20Rights%20Reserved-lightgrey.svg" />
</p>

---

## 🚀 Project Overview
Raptor Event Scout is a multi‑agent system that automatically discovers local tech/business events, scores their relevance using LLM‑powered analysis, and auto‑registers for the best free opportunities. Results are saved to Supabase and optionally delivered via Telegram or email.


**Flow:** Discover → Rank → Register → Notify → Store

**At a glance:**
- **Target cities:** Osaka, Kobe, Kyoto
- **Platforms:** Connpass + mock Peatix/Meetup sources
- **Auto‑registration:** Defaults to free events with relevance ≥ 0.8 (max 3 per run)
- **Outputs:** Supabase records + optional Telegram/email digest

---

## 🧠 Problem & Solution
**Problem:** Business development teams lose time manually scanning multiple event platforms, missing high‑value opportunities in key markets.

**Solution:** An AI‑driven pipeline that continuously discovers events, ranks them by relevance, and automatically registers for the most promising free events—then shares a clean weekly digest.

---

## ✨ Features
- **Multi‑agent architecture** for discovery, ranking, registration, and notification.
- **LLM‑based relevance scoring** using Groq for semantic analysis.
- **Auto‑registration** for high‑scoring, free events (rate‑limited and capped per run).
- **Supabase persistence** for events and registrations.
- **Telegram and email digests** when credentials are configured.
- **Extensible platform support** (current: Connpass + mock Peatix/Meetup).

---

## 🛠 Tech Stack
- **Language:** Python 3.8+
- **AI/LLM:** Groq (Llama 3.3 70B)
- **Data Models:** Pydantic
- **Database:** Supabase (PostgreSQL)
- **HTTP:** httpx
- **Scheduling:** Cron (recommended) or external scheduler
- **Notifications:** Telegram Bot API, SMTP email

---

## 📸 Screenshots / Demo
**Sample run (excerpt):**
```text
🚀 Starting Raptor Event Scout...
🔍 Phase 1: Discovering events...
🎯 Phase 2: Ranking events by relevance...
🎫 Phase 3: Registering for events...
📢 Phase 4: Sending notifications...
🎉 Raptor Event Scout completed successfully!
```

---

## ⚙️ Installation & Setup
### Prerequisites
- Python 3.8+
- Groq API key
- Supabase project (URL + anon key)
- Optional: Telegram bot token and email SMTP credentials

### Install
```bash
git clone https://github.com/ImaduddeenKhan/AGENT_AUTOMATION.git
cd AGENT_AUTOMATION
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
If you're using a fork, replace the clone URL accordingly.

### Environment Variables
Create a `.env` file in the project root:
```env
# Required
GROQ_API_KEY=your_groq_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# Optional: Notifications
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
EMAIL_USERNAME=you@example.com
EMAIL_PASSWORD=your_email_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Optional: Company info
COMPANY_NAME=Your Company
CONTACT_NAME=Your Name
CONTACT_EMAIL=events@yourcompany.com
CONTACT_PHONE=+81-XXX-XXXX-XXXX
CONTACT_POSITION=Business Development
```

### Run
```bash
# Smoke test
python test_scout.py

# Run once
python main.py --now
```

### Schedule (Cron example)
```cron
0 10 * * 1 cd /path/to/AGENT_AUTOMATION && /usr/bin/python3 main.py --now
```

---

## 📂 Project Structure
```text
AGENT_AUTOMATION/
├── agents/                 # Core AI agents
│   ├── event_finder.py      # Event discovery (Connpass + mocks)
│   ├── event_ranker.py      # Relevance scoring with Groq
│   ├── event_registrar.py   # Auto-registration logic
│   └── notifier.py          # Telegram/email notifications
├── models/                 # Pydantic data models
├── storage/                # Supabase integration
├── main.py                 # Orchestrator
├── test_scout.py           # Smoke test runner
├── requirements.txt        # Dependencies
└── raptor_scout.log         # Runtime logs
```

---

## 🔮 Future Improvements
- Add real integrations for Peatix/Meetup/Eventbrite (API or compliant scraping).
- Web dashboard for event analytics and registration management.
- Configurable relevance rules per team or persona.
- Dockerized deployment with a production scheduler.

---

## 🤝 Contribution Guidelines
Contributions are welcome. Please:
1. Fork the repo and create a feature branch.
2. Keep changes focused and well‑documented.
3. Run the smoke test (`python test_scout.py`) before opening a PR.

---

## 📜 License
All rights reserved. Contact the repository owner for usage permissions.
