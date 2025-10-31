#  Event Finder , Register , Notifier Agent

**Automated AI Agent System for Tech Event Discovery & Registration**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-API-green.svg)](https://groq.com)
[![Supabase](https://img.shields.io/badge/Supabase-Database-orange.svg)](https://supabase.com)

An autonomous AI agent system that automatically discovers, filters, and registers for relevant business and tech events in **Osaka, Kobe, and Kyoto**. Helps companies grow partnerships and acquire clients through strategic event participation.

##  Features

- ** Multi-Agent Architecture** - Modular AI agents for discovery, ranking, registration, and notifications
- ** Smart Event Discovery** - Searches multiple Japanese event platforms (Connpass, Peatix, Meetup, Eventbrite)
- ** AI-Powered Ranking** - Uses Groq's fast LLM to analyze event relevance with semantic understanding
- ** Auto-Registration** - Automatically registers for free events that meet business criteria
- ** Database Storage** - Saves all events and registrations to Supabase PostgreSQL
- ** Multi-Channel Notifications** - Sends weekly digests via Telegram and Email
- ** Scheduled Execution** - Runs automatically every Monday at 10 AM JST

##  System Architecture
Event Discovery → AI Ranking → Auto-Registration → Notifications → Database
↓ ↓ ↓ ↓ ↓
EventFinder EventRanker EventRegistrar Notifier Supabase
Agent Agent Agent Agent Storage

text

## 🛠️ Quick Start
### Prerequisites
- Python 3.8+
- [Groq API Key](https://console.groq.com) (Free)
- [Supabase Account](https://supabase.com) (Free)
- (Optional) Telegram Bot Token

### Installation
1. **Clone & Setup**
```bash
git clone https://github.com/yourusername/raptor-event-scout.git
cd raptor-event-scout
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
Install Dependencies

bash
pip install -r requirements.txt
Environment Configuration

bash
cp .env.example .env
# Edit .env with your API keys
Database Setup

Create Supabase project

Run the SQL schema from database/schema.sql

Add credentials to .env

Configuration
Edit .env file:

env
# Groq API (Free)
GROQ_API_KEY=gsk_your_key_here

# Supabase Database (Free)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here

# Company Information
COMPANY_NAME=Your Company
CONTACT_EMAIL=events@yourcompany.com
CONTACT_PHONE=+81-XXX-XXXX-XXXX


Usage
Test the System

bash
python test_scout.py
Run Immediately

bash
python main.py --now
Run with Scheduler

bash
python main.py

📊 Viewing Results
Database (Supabase)
Go to your Supabase Dashboard → Select your project → Open Table Editor to see:

events - All discovered events with relevance scores
event_registrations - Successful registrations
weekly_digests - Sent notifications

Local Files
raptor_scout.log - Detailed execution logs
Console output - Real-time progress updates

Sample Output
text
 Raptor Event Scout completed successfully!
 Summary:
   - Discovered: 12 events
   - Relevant: 8 events (score > 0.6)
   - Registered: 3 events automatically
   - Notifications: Sent to Telegram & Email



## How It Works
1. Event Discovery
Searches multiple Japanese event platforms
Focuses on Osaka, Kobe, Kyoto regions
Uses both APIs and web scraping (with rate limiting)


2. AI Relevance Ranking
Keyword Matching: startup, AI, HR tech, business, innovation
Semantic Analysis: Groq LLM evaluates business relevance
Location Scoring: Priority for target cities
Final Score: Weighted combination (0.0 to 1.0)


3. Auto-Registration
Registers for events with score > 0.8
Only free events (no payment required)
Uses company information from .env
Saves confirmation data and QR codes


4. Notifications
Weekly Digest: Top 10 events with details
Registration Confirmations: Success/failure status
Multi-channel: Telegram + Email support

🤖 Agent System
Agent	              Responsibility	          Key Features
EventFinderAgent	    Discover events from multiple sources    	Platform APIs, web scraping, error handling
EventRankerAgent	    Filter and rank by relevance      	Groq AI analysis, keyword matching, scoring
EventRegistrarAgent   	Auto-register for events	      Form filling, confirmation capture, limits
NotifierAgent	          Send notifications        Telegram/Email, formatted digests, confirmations


🗂️ Project Structure
text
raptor-event-scout/
├── agents/                 # AI Agent implementations
│   ├── event_finder.py    # Event discovery logic
│   ├── event_ranker.py    # Relevance ranking with Groq
│   ├── event_registrar.py # Auto-registration system
│   └── notifier.py        # Telegram & Email notifications
├── models/                # Data models
│   └── event_models.py    # Pydantic models for events
├── storage/               # Database layer
│   └── supabase_client.py # Supabase integration
├── database/              # Database schemas
│   └── schema.sql         # PostgreSQL schema
├── main.py               # Main orchestrator
├── test_scout.py         # Test script
├── requirements.txt      # Dependencies
├── .env.example          # Environment template
└── .env                 # Configuration (gitignored)

⚙️ Configuration Options
Event Sources
Connpass (API)

Peatix (Web scraping)

Meetup (API)

Eventbrite (API)

JETRO/Chamber of Commerce

Relevance Keywords
python
["startup", "AI", "HR tech", "expat", "business", 
 "innovation", "hiring", "tech", "entrepreneur"]
Registration Rules
Minimum relevance score: 0.8

Must be free events

Maximum 3 auto-registrations per week

Requires registration form

## Deployment
Local Development
bash
python main.py --now  # Run once
python main.py        # Run with scheduler
Production Deployment
bash
# Set up cron job for scheduled execution
0 10 * * 1 cd /path/to/raptor-event-scout && /usr/bin/python3 main.py
