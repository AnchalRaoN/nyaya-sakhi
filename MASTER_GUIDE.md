# 🎯 NYAYA SAKHI — MASTER BUILD GUIDE
Follow this top to bottom, in order. Everything you need is here.

---

## ✅ PHASE 1 — LOCAL SETUP (30 min)

1. Get 2 API keys:
   - **Gemini**: aistudio.google.com → Get API Key → copy `AIzaSy...`
   - **Twilio**: twilio.com → sign up → verify phone → Console → copy Account SID + Auth Token → Messaging → Try it out → WhatsApp sandbox → join it from your phone
2. Install **ngrok**: ngrok.com → sign up → download → unzip to Desktop
3. Open CMD:
```
cd Desktop
mkdir nyaya-sakhi
cd nyaya-sakhi
python -m venv venv
venv\Scripts\activate
```
4. Copy all project files (main.py, agents/, utils/, requirements.txt, .env.example) into this folder
5. Rename `.env.example` to `.env` and fill in your real keys
6. Install everything:
```
pip install -r requirements.txt
```
(Whisper takes a few minutes — be patient)

---

## ✅ PHASE 2 — RUN & TEST LOCALLY (20 min)

1. Load the legal corpus (ONE TIME only):
```
python agents/law_rag.py
```
Expect: `✅ Loaded 8 legal sections into ChromaDB`

2. Open **Terminal 1** — run the server:
```
uvicorn main:app --reload --port 8000
```

3. Open **Terminal 2** — run ngrok:
```
cd Desktop
ngrok http 8000
```
Copy the `https://....ngrok-free.app` URL it gives you.

4. Paste that URL into `.env` as:
```
BASE_URL=https://your-ngrok-url.ngrok-free.app
```
Then **restart Terminal 1** (Ctrl+C, run uvicorn command again).

5. Go to Twilio Console → Messaging → Try it out → WhatsApp Sandbox →
paste in "When a message comes in": `https://your-ngrok-url.ngrok-free.app/webhook/whatsapp`

6. **Test on WhatsApp** — send these in order to the sandbox number:
   - `hi` → expect welcome message
   - `Mera pati mujhe roz maarte hain dahej ke liye, Bangalore mein` → expect follow-up question
   - Answer the follow-up → expect "Reply YES to confirm"
   - `yes` → expect: text confirmation → PDF file → voice note (all within ~20 sec)
   - New session, send: `he's here help me now` → expect instant 112 message

7. If anything breaks, check Terminal 1 for the error message — common fixes:
   - `GEMINI_API_KEY not found` → check `.env` spacing, restart server
   - PDF/audio never arrives → `BASE_URL` doesn't match current ngrok URL
   - `chromadb collection empty` → re-run `python agents/law_rag.py`

---

## ✅ PHASE 3 — PUSH TO GITHUB (15 min)

1. github.com → New repository → name it `nyaya-sakhi` → **Public** → Create
2. In your project folder:
```
git init
git add .
git commit -m "Initial Nyaya Sakhi prototype"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/nyaya-sakhi.git
git push -u origin main
```
3. Check your repo online — confirm `.env` is **NOT** visible (only `.env.example` should be there)

---

## ✅ PHASE 4 — DEPLOY BACKEND ON RENDER (20 min)

1. render.com → sign up with GitHub
2. New + → Web Service → select your `nyaya-sakhi` repo → Connect
3. Settings:
   - Region: Singapore
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: Free
4. Add Environment Variables (copy from your `.env`):
   `GEMINI_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER`
   Leave `BASE_URL` blank for now.
5. Click **Create Web Service** → wait 3-5 min for first build
6. Copy your live URL (e.g. `https://nyaya-sakhi.onrender.com`)
7. Go back to Environment tab → add `BASE_URL` = that URL → Save (auto-redeploys)
8. Update Twilio webhook to: `https://nyaya-sakhi.onrender.com/webhook/whatsapp`
9. ⚠️ Free tier sleeps after 15 min idle — first message after sleep takes ~50 sec. Send a test "hi" a minute before demoing to warm it up.

---

## ✅ PHASE 5 — DEPLOY DASHBOARD ON NETLIFY (10 min)

1. Open `frontend/index.html` in a text editor
2. Find this line (~line 608):
```js
: 'https://nyaya-sakhi.onrender.com';
```
Replace with **your actual** Render URL from Phase 4.
3. netlify.com → sign up with GitHub
4. Drag your whole `frontend` folder into the deploy box
5. Copy the URL Netlify gives you (e.g. `https://random-name.netlify.app`)
6. Optional: Site settings → Change site name → make it `nyaya-sakhi`

---

## ✅ PHASE 6 — FINAL GITHUB PUSH (5 min)

1. Update `README.md` — replace all placeholder URLs with your real:
   - Render backend URL
   - Netlify frontend URL
   - GitHub repo URL
2. Push everything:
```
git add .
git commit -m "Add live deployment links"
git push
```

---

## ✅ PHASE 7 — FULL END-TO-END TEST (do this before recording video)

Test on the LIVE Render URL (not localhost/ngrok anymore):
- [ ] Send "hi" on WhatsApp → wait for wake-up if sleeping → get welcome message
- [ ] Send full case in one message → check it extracts multiple fields at once
- [ ] Answer follow-up → get "Reply YES" prompt
- [ ] Send "yes" → PDF arrives → voice note arrives
- [ ] Open Netlify dashboard URL → type same case in chat box → watch pipeline light up
- [ ] Test safety trigger with "help me now" in a new session

---

## ✅ PHASE 8 — RECORD DEMO VIDEO (2 min video)

- 0:00–0:10 — Intro: "Nyaya Sakhi is a free AI legal assistant for rural Indian women on WhatsApp"
- 0:10–0:40 — Show WhatsApp conversation (voice note if possible, in Hindi)
- 0:40–1:10 — Switch to Netlify dashboard, send same message, show pipeline animate
- 1:10–1:40 — Show PDF arriving on WhatsApp, open it, show FIR + IPC sections cited
- 1:40–2:00 — Closing line + helpline numbers shown

Keep it under 3 minutes. Add subtitles if you can.

---

## ✅ PHASE 9 — SUBMISSION CHECKLIST (final review)

- [ ] Public GitHub repo with all code
- [ ] README with clear run-locally steps ✅ (already written)
- [ ] Open-source attribution table with licenses ✅ (already in README)
- [ ] Live demo URL (Netlify) working
- [ ] Deployed backend URL (Render) working
- [ ] Demo video recorded and uploaded
- [ ] `.env` confirmed NOT pushed to GitHub
- [ ] Team name, college, track filled in submission form

---

## 🆘 TROUBLESHOOTING QUICK REFERENCE

| Problem | Likely cause | Fix |
|---|---|---|
| WhatsApp doesn't reply at all | Webhook URL wrong/outdated | Recheck Twilio webhook matches current Render/ngrok URL |
| PDF/audio never arrives | `BASE_URL` env var wrong | Must exactly match your live backend URL, no trailing slash |
| Dashboard shows nothing when typing | API URL in index.html wrong | Recheck line ~608 has your real Render URL |
| Laws panel never fills in | Field name mismatch | Already fixed in latest `index.html` and `main.py` |
| Render app sleeping / slow first reply | Free tier auto-sleep | Send a warm-up "hi" 1 min before demoing |
| ChromaDB empty after redeploy | Render wipes disk on restart | Already auto-fixed in `agents/law_rag.py` (self-reloads on startup) |
| `git push` asks for password and fails | GitHub needs token, not password | Generate a Personal Access Token on GitHub, use that instead |
