from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from twilio.rest import Client as TwilioClient

from agents.intake import IntakeAgent
from agents.law_rag import LawRagAgent
from agents.drafter import DrafterAgent
from utils.stt import transcribe_audio
from utils.tts import text_to_speech
from utils.pdf_gen import generate_pdf
from utils.session import SessionManager
from utils.escalation import get_nearest_dlsa

app = FastAPI(title="Nyaya Sakhi")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

session_manager = SessionManager()
intake_agent    = IntakeAgent()
law_rag_agent   = LawRagAgent()
drafter_agent   = DrafterAgent()

twilio_client = TwilioClient(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# ── Language-matched message templates ─────────────────────────────────────

CONFIRM_MESSAGES = {
    "hi": lambda incident, count: (
        f"✅ Maine aapke *{incident}* case ko samajh liya hai.\n\n"
        f"Mujhe *{count} relevant kaanoon* mile hain jo aapki suraksha karte hain.\n\n"
        "Kya main abhi aapka FIR document taiyar karoon?\n"
        "Confirm karne ke liye *YES* likhein 📄"
    ),
    "kn": lambda incident, count: (
        f"✅ ನಿಮ್ಮ *{incident}* ಪ್ರಕರಣವನ್ನು ನಾನು ಅರ್ಥಮಾಡಿಕೊಂಡಿದ್ದೇನೆ.\n\n"
        f"ನಿಮ್ಮನ್ನು ರಕ್ಷಿಸುವ *{count} ಸಂಬಂಧಿತ ಕಾನೂನುಗಳನ್ನು* ನಾನು ಕಂಡುಕೊಂಡಿದ್ದೇನೆ.\n\n"
        "ಈಗ ನಾನು ನಿಮ್ಮ FIR ದಾಖಲೆಯನ್ನು ಸಿದ್ಧಪಡಿಸಲೇ?\n"
        "ದೃಢೀಕರಿಸಲು *YES* ಎಂದು ಬರೆಯಿರಿ 📄"
    ),
    "ta": lambda incident, count: (
        f"✅ உங்கள் *{incident}* வழக்கை நான் புரிந்துகொண்டேன்.\n\n"
        f"உங்களைப் பாதுகாக்கும் *{count} தொடர்புடைய சட்டங்களை* கண்டறிந்துள்ளேன்.\n\n"
        "இப்போது உங்கள் FIR ஆவணத்தை தயார் செய்யவா?\n"
        "உறுதிப்படுத்த *YES* என தட்டச்சு செய்யவும் 📄"
    ),
    "en": lambda incident, count: (
        f"✅ I have understood your case about *{incident}*.\n\n"
        f"I found *{count} relevant laws* that protect you.\n\n"
        "Shall I prepare your FIR document now?\n"
        "Reply *YES* to confirm 📄"
    ),
}

COMPLETION_MESSAGES = {
    "hi": lambda incident: (
        "✅ *Aapke documents taiyar hain!*\n\n"
        f"Maine aapka FIR draft *{incident}* ke liye taiyar kiya hai.\n\n"
        "📄 Ismein shaamil hai:\n"
        "• FIR application (kaanooni sections ke saath)\n"
        "• Aapke adhikar Indian law ke tahat\n"
        "• Helpline numbers\n\n"
        "Aapka PDF bhej raha hoon... 📎\n\n"
        "_Yeh legal aid hai, wakeel ka substitute nahi. Kripya apne nearest DLSA se bhi milein free legal help ke liye._\n\n"
        "🆘 *NCW: 7827-170-170* | *Women's Helpline: 181*"
    ),
    "kn": lambda incident: (
        "✅ *ನಿಮ್ಮ ದಾಖಲೆಗಳು ಸಿದ್ಧವಾಗಿವೆ!*\n\n"
        f"ನಾನು *{incident}* ಗಾಗಿ ನಿಮ್ಮ FIR ಕರಡನ್ನು ಸಿದ್ಧಪಡಿಸಿದ್ದೇನೆ.\n\n"
        "📄 ಒಳಗೊಂಡಿದೆ:\n"
        "• ಕಾನೂನು ವಿಭಾಗಗಳೊಂದಿಗೆ FIR ಅರ್ಜಿ\n"
        "• ಭಾರತೀಯ ಕಾನೂನಿನ ಅಡಿಯಲ್ಲಿ ನಿಮ್ಮ ಹಕ್ಕುಗಳು\n"
        "• ಸಹಾಯವಾಣಿ ಸಂಖ್ಯೆಗಳು\n\n"
        "🆘 *NCW: 7827-170-170* | *ಮಹಿಳಾ ಸಹಾಯವಾಣಿ: 181*"
    ),
    "ta": lambda incident: (
        "✅ *உங்கள் ஆவணங்கள் தயார்!*\n\n"
        f"நான் *{incident}* க்கான உங்கள் FIR வரைவை தயார் செய்துள்ளேன்.\n\n"
        "📄 உள்ளடக்கியது:\n"
        "• சட்டப் பிரிவுகளுடன் FIR விண்ணப்பம்\n"
        "• இந்திய சட்டத்தின் கீழ் உங்கள் உரிமைகள்\n"
        "• உதவி எண்கள்\n\n"
        "🆘 *NCW: 7827-170-170* | *மகளிர் உதவி எண்: 181*"
    ),
    "en": lambda incident: (
        "✅ *Your documents are ready!*\n\n"
        f"I have prepared your FIR draft for *{incident}*.\n\n"
        "📄 Includes:\n"
        "• FIR application with legal sections cited\n"
        "• Your rights under Indian law\n"
        "• Helpline numbers\n\n"
        "Sending your PDF now... 📎\n\n"
        "_This is legal aid, not a replacement for a lawyer. "
        "Please also visit your nearest DLSA for free legal representation._\n\n"
        "🆘 *NCW: 7827-170-170* | *Women's Helpline: 181*"
    ),
}

# ── Routes ───────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "Nyaya Sakhi is live 🎉"}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form  = await request.form()
    data  = dict(form)

    from_number  = data.get("From", "")
    body         = data.get("Body", "").strip()
    media_url    = data.get("MediaUrl0", "")
    media_type   = data.get("MediaContentType0", "")
    num_media    = int(data.get("NumMedia", 0))
    profile_name = data.get("ProfileName", "")
    wa_id        = data.get("WaId", "")

    print("\n========== NEW WHATSAPP REQUEST ==========")
    print("FROM:", from_number, "| BODY:", body, "| NUM MEDIA:", num_media)
    print("=========================================\n")

    session = session_manager.get_or_create(from_number)
    if not session.get("auto_name"):
        session["auto_name"] = profile_name
        session["auto_phone"] = wa_id

    danger_words = ["help me now", "he's here", "i'm scared",
                    "bachao", "bachao mujhe", "darr", "maar raha"]
    if any(w in body.lower() for w in danger_words):
        await send_message(from_number,
            "🚨 *Please call 112 immediately!*\n\n"
            "Your safety comes first.\n\n"
            "📞 *Emergency: 112*\n"
            "📞 *Women's Helpline: 181*\n"
            "📞 *NCW: 7827-170-170*"
        )
        return JSONResponse({"status": "ok"})

    if num_media > 0 and "audio" in media_type:
        await send_message(from_number, "🎙️ Got your voice note! Transcribing...")
        text = await transcribe_audio(media_url)
        if not text:
            await send_message(from_number,
                "Sorry, I couldn't hear that clearly. "
                "Could you please repeat or type what happened?"
            )
            return JSONResponse({"status": "ok"})
        user_input = text
    else:
        user_input = body

    if not user_input:
        await send_message(from_number, get_welcome_message())
        return JSONResponse({"status": "ok"})

    response, session, pdf_path = await run_pipeline(user_input, session, from_number)
    session_manager.save(from_number, session)

    await send_message(from_number, response)

    if pdf_path:
        await send_document(from_number, pdf_path)
        lang = session.get("detected_language", "hi")
        incident = session.get("extracted", {}).get("incident_type", "case")
        voice_summary_map = {
            "hi": f"Aapka {incident} ke baare mein FIR tayyar ho gaya hai. Kripya yeh document apne nearest police station le jaayein.",
            "en": f"Your FIR regarding {incident} is ready. Please take this document to your nearest police station.",
        }
        voice_summary = voice_summary_map.get(lang, voice_summary_map["hi"])
        audio_path = text_to_speech(voice_summary, lang=lang)
        if audio_path:
            await send_audio(from_number, audio_path)

    return JSONResponse({"status": "ok"})

@app.post("/api/demo")
async def demo(request: Request):
    body       = await request.json()
    user_input = body.get("message", "")
    session_id = body.get("session_id", "demo_user")

    session = session_manager.get_or_create(session_id)
    response, session, pdf_path = await run_pipeline(user_input, session, session_id)
    session_manager.save(session_id, session)

    pdf_url = f"/static/{os.path.basename(pdf_path)}" if pdf_path else None
    return {
        "response":      response,
        "stage":         session.get("stage", "intake"),
        "extracted":     session.get("extracted", {}),
        "law_sections":  session.get("law_sections", []),
        "pdf_generated": pdf_path is not None,
        "pdf_url":       pdf_url
    }

@app.get("/api/stats")
def stats():
    return session_manager.get_stats()

# ── Core pipeline ──────────────────────────────────────────────────────────

async def run_pipeline(user_input, session, user_id):
    pdf_path = None
    stage    = session.get("stage", "intake")

    if stage == "intake":
        response, session = await intake_agent.process(user_input, session)

        if session.get("intake_complete"):
            session["stage"] = "rag"
            laws = await law_rag_agent.search(session.get("extracted", {}))
            session["law_sections"] = laws
            session["stage"] = "drafting"
            session["awaiting_confirm"] = True

            incident = session.get("extracted", {}).get("incident_type", "your case")
            lang = session.get("detected_language", "en")
            template = CONFIRM_MESSAGES.get(lang, CONFIRM_MESSAGES["en"])
            response = template(incident, len(laws))

        return response, session, None

    elif stage == "drafting":
        if session.get("awaiting_confirm"):
            if "yes" in user_input.lower():
                session["awaiting_confirm"] = False
                session["extracted"]["complainant_name"] = session.get("auto_name", "")
                session["extracted"]["complainant_phone"] = session.get("auto_phone", "")

                _, session = await drafter_agent.process(session)
                pdf_path = generate_pdf(session, user_id)
                session["stage"] = "complete"

                incident = session.get("extracted", {}).get("incident_type", "your case")
                lang = session.get("detected_language", "en")
                template = COMPLETION_MESSAGES.get(lang, COMPLETION_MESSAGES["en"])
                response = template(incident)

                dlsa = get_nearest_dlsa(session.get("extracted", {}).get("incident_location", ""))
                response += (
                    f"\n\n📍 *Nearest Free Legal Aid:*\n"
                    f"{dlsa['office']}\n"
                    f"📞 {dlsa['phone']}\n"
                    f"{dlsa['address']}\n\n"
                    f"Take this document to them — they provide free lawyers."
                )
            else:
                response = "Okay, no problem. Type *new* to start again anytime."
        else:
            response = "Your documents are ready! Type *new* to start a new case."
        return response, session, pdf_path

    elif stage == "complete":
        if "new" in user_input.lower():
            session = session_manager.reset(user_id)
            response = get_welcome_message()
        else:
            response = (
                "Your case is complete! 🎉\n\n"
                "Type *new* to start a new case.\n\n"
                "🆘 *NCW: 7827-170-170* | *Helpline: 181*"
            )
        return response, session, None

    return get_welcome_message(), session, None

def get_welcome_message():
    return (
        "🙏 *Namaste! Main Nyaya Sakhi hoon.*\n\n"
        "I help Indian women understand their legal rights "
        "and create documents to protect them — free of cost, "
        "in your language.\n\n"
        "Please tell me what happened. "
        "You can type or send a voice note in Hindi, "
        "Kannada, Tamil, or English. 🕊️"
    )

async def send_message(to, message):
    try:
        twilio_client.messages.create(
            body=message,
            from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
            to=to
        )
    except Exception as e:
        print(f"Send error: {e}")

async def send_audio(to, audio_path):
    try:
        public_url = f"{os.getenv('BASE_URL')}/static/{os.path.basename(audio_path)}"
        twilio_client.messages.create(
            media_url=[public_url],
            from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
            to=to
        )
    except Exception as e:
        print(f"Audio send error: {e}")

async def send_document(to, pdf_path):
    try:
        public_url = f"{os.getenv('BASE_URL')}/static/{os.path.basename(pdf_path)}"
        twilio_client.messages.create(
            media_url=[public_url],
            from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
            to=to
        )
    except Exception as e:
        print(f"Document send error: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)