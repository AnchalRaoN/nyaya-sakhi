# ⚖️ Nyaya Sakhi — AI-Powered Legal Aid for Rural Indian Women

> *न्याय सखी* — "A friend who brings justice"

**ScriptedBy{Her} 2.0 · Meesho Women's Hackathon 2026 · Team AAA · NMAM Institute of Technology**

---

## 🎯 Problem

India has a critical legal access gap — roughly 1 lawyer per 1,000 citizens vs 1 per 250 in the US. Rural women sit at the intersection of three compounding barriers:
- **Geographic**: courts are far
- **Economic**: lawyers are unaffordable  
- **Literacy**: legal documents require education

Result: **73% of affected women never file a complaint.**

---

## 💡 Solution

Nyaya Sakhi collapses all three barriers using agentic AI — delivering a compassionate, multilingual legal co-pilot directly through **WhatsApp**, available **24/7**, at **zero cost**.

**Voice note → FIR PDF in under 90 seconds.**

---

## 🏗️ Architecture

```
User (WhatsApp voice note)
        ↓
Twilio Webhook → FastAPI
        ↓
Bhashini STT (OGG → Hindi/regional text, ~300ms)
        ↓
LangGraph Orchestrator (CaseState typed dict)
        ↓
┌───────────────────────────────────────┐
│  Agent 1 — Intake (Claude)            │
│  Conversational case extraction       │
│  → structured CaseState JSON         │
└───────────────────────────────────────┘
        ↓
┌───────────────────────────────────────┐
│  Agent 2 — Law RAG                    │
│  pgvector semantic search             │
│  PWDVA, IPC/BNS, POSH, etc.          │
└───────────────────────────────────────┘
        ↓
┌───────────────────────────────────────┐
│  Agent 3 — Drafter (Claude)           │
│  FIR draft + RTI + NCW complaint      │
│  ReportLab bilingual PDF              │
└───────────────────────────────────────┘
        ↓
WhatsApp PDF delivery via Twilio
```

---

## 🔗 Live Links

- **Live Demo Dashboard**: https://nyaya-sakhi.netlify.app *(replace with your actual Netlify URL)*
- **Deployed Backend**: https://nyaya-sakhi.onrender.com *(replace with your actual Render URL)*
- **GitHub Repository**: https://github.com/your-username/nyaya-sakhi *(replace with your actual repo)*
- **WhatsApp Sandbox**: Message `+1 415 523 8886` after joining the Twilio sandbox

---

## 🚀 Quick Start (Run Locally)

### Prerequisites
- Python 3.11+
- Git

### 1. Clone the repo
```bash
git clone https://github.com/your-username/nyaya-sakhi.git
cd nyaya-sakhi
```

### 2. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
# Fill in your API keys (see below)
```

### 4. Run the server
```bash
uvicorn main:app --reload --port 8000
```

### 5. Open the dashboard
Open `frontend/index.html` in your browser — no build step needed.

---

## 🔑 Required API Keys

| Service | Where to get it | Cost |
|---|---|---|
| Anthropic | [console.anthropic.com](https://console.anthropic.com) | Pay per use |
| Twilio | [twilio.com](https://twilio.com) | Free trial |
| Bhashini | [bhashini.gov.in/ulca](https://bhashini.gov.in/ulca) | **Free** |
| Supabase | [supabase.com](https://supabase.com) | Free tier |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/webhook/whatsapp` | Twilio WhatsApp webhook |
| POST | `/api/demo` | Demo pipeline (no WhatsApp needed) |
| GET | `/api/stats` | Live session statistics |
| GET | `/health` | Health check |

---

## 🧠 Agent Details

### Agent 1 — Intake
- **Model**: claude-sonnet-4-6
- **Job**: Conversational extraction of 6 case fields
- **Languages**: Hindi, Kannada, Tamil, English, mixed
- **Output**: Structured CaseState JSON

### Agent 2 — Law RAG
- **Search**: pgvector cosine similarity (all-MiniLM-L6-v2 embeddings)
- **Corpus**: PWDVA 2005, IPC/BNS 498A, POSH Act 2013, Dowry Prohibition Act, Hindu Succession Act
- **Fallback**: Claude-powered law lookup if vector store unavailable

### Agent 3 — Drafter
- **Model**: claude-sonnet-4-6
- **Output**: Legally-structured FIR, RTI application, NCW complaint
- **PDF**: ReportLab with NotoDevanagari font for Hindi text

---

## 📦 Open-Source Attribution

| Library | Version | License | Role |
|---|---|---|---|
| FastAPI | 0.111.0 | MIT | Backend framework |
| Anthropic SDK | 0.28.0 | MIT | Claude API client |
| LangGraph | 0.2.x | MIT | Multi-agent orchestration |
| Twilio | 9.1.0 | MIT | WhatsApp integration |
| Supabase | 2.4.6 | Apache 2.0 | Database + pgvector |
| sentence-transformers | 2.7.0 | Apache 2.0 | Text embeddings |
| ReportLab | 4.1.0 | BSD | PDF generation |
| httpx | 0.27.0 | BSD | Async HTTP client |
| uvicorn | 0.29.0 | BSD | ASGI server |

---

## 🔒 Privacy & Safety

- Phone numbers hashed (SHA-256 + salt) before storage
- Sessions ephemeral by default — no data retained after 24h
- Deployed on Supabase India region (DPDP Act 2023 compliant)
- Every document includes DLSA contact and disclaimer
- Not a replacement for professional legal counsel

---

## 🆘 Emergency Contacts

- **NCW Helpline**: 7827-170-170
- **Women's Helpline**: 181  
- **Police Emergency**: 100
- **NALSA Legal Aid**: 15100

---

## 👥 Team

**Team AAA** · NMAM Institute of Technology, Karnataka  
ScriptedBy{Her} 2.0 · Meesho Women's Hackathon 2026

---

*Nyaya Sakhi is legal aid, not legal advice. Always consult your nearest District Legal Services Authority (DLSA) for free professional representation.*
