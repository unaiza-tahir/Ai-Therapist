# SafeSpace AI Therapist 🧠💬

An AI-powered mental health support agent that talks to users over **WhatsApp**, powered by an LLM agent (LangGraph + Groq), with built-in safety tools for emergencies and nearby therapist lookup. A **Streamlit** frontend is also included for direct web-based testing/interaction.



## ✨ Features

- **Conversational support** — responds to emotional/mental-health queries with warm, therapeutic guidance (persona: *Dr. Emily Hartman*).
- **WhatsApp integration** — via Twilio, so users can message the bot directly from WhatsApp.
- **Emergency escalation** — if the user expresses suicidal ideation or a mental health crisis, the agent can trigger an emergency phone call via Twilio.
- **Nearby therapist finder** — looks up real therapists/clinics near a given location using OpenStreetMap (Nominatim + Overpass API).
- **Streamlit dashboard** — a simple web UI for testing the agent outside of WhatsApp.



## 🏗️ Architecture


WhatsApp User
     │
     ▼
Twilio WhatsApp Sandbox / Number
     │  (POST webhook)
     ▼
FastAPI backend (backend/main.py)
     │
     ▼
LangGraph Agent (backend/ai_agent.py)
     │
     ├── ask_mental_health_specialist  → Groq LLM (therapist persona)
     ├── emergency_call_tool           → Twilio voice call
     └── find_nearby_therapists_by_location → OpenStreetMap (Nominatim + Overpass)


A separate **Streamlit app** (`frontend.py`) provides a simple chat-style interface for testing the same agent from a browser.



## 📁 Project Structure


Ai-Therapist/
├── backend/
│   ├── main.py               # FastAPI app — /ask, /whatsapp_ask, /health routes
│   ├── ai_agent.py           # LangGraph agent + tool definitions + system prompt
│   ├── tools.py              # Therapist response (Groq), emergency call, location tool helpers
│   ├── config.py             # Reads all secrets from environment variables
│   └── requirements.txt      # Python dependencies for the backend
├── frontend.py                # Streamlit web UI
├── .gitignore
└── README.md




## ⚙️ Setup (Local Development)

### 1. Clone the repo
bash
git clone https://github.com/<your-username>/Ai-Therapist.git
cd Ai-Therapist


### 2. Install dependencies
bash
cd backend
pip install -r requirements.txt


### 3. Configure environment variables
Create a `backend/.env` file (this file is git-ignored and never committed):

TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_NUMBER=+1xxxxxxxxxx
EMERGENCY_CONTACT=+92xxxxxxxxxx
GROQ_API_KEY=your_groq_api_key
GOOGLE_GEOCODING_API_KEY=your_google_key
GOOGLE_PLACES_API_KEY=your_google_key


### 4. Run the backend
bash
uvicorn main:app --reload


### 5. Run the Streamlit frontend (separate terminal)
bash
streamlit run frontend.py




## ☁️ Deployment

The backend is deployed on **Railway** (free tier):

- **Root directory:** `backend`
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- All secrets above are set as environment variables in the Railway dashboard (never committed to git).

Once deployed, Railway provides a public URL, e.g.:

https://ai-therapist-production-xxxx.up.railway.app


### Connecting WhatsApp (Twilio Sandbox)

1. Go to [Twilio Console](https://console.twilio.com) → **Messaging → Try it out → WhatsApp Sandbox Settings**
2. Set **"When a message comes in"** to:
   
   https://<your-railway-url>/whatsapp_ask
   
   Method: `POST`
3. From your phone, join the sandbox by sending the given join code to the Twilio WhatsApp number.
4. Send any message — the bot will reply.


## 🔌 API Endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/` | Basic service status check |
| GET | `/health` | Health check (for uptime monitoring) |
| POST | `/ask` | Send `{"message": "..."}` and get a JSON response — useful for testing without WhatsApp |
| POST | `/whatsapp_ask` | Twilio webhook — receives `From` and `Body` form fields, replies with TwiML |


## 🧰 Tech Stack

- **FastAPI** — backend web framework
- **LangGraph / LangChain** — agent orchestration
- **Groq (`openai/gpt-oss-120b`)** — LLM inference
- **Twilio** — WhatsApp messaging & emergency voice calls
- **Streamlit** — web frontend
- **Geopy + OpenStreetMap Overpass API** — nearby therapist lookup
- **Railway** — backend hosting
