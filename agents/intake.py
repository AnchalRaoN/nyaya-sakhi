import google.generativeai as genai
import os
import json

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are Nyaya Sakhi — a compassionate legal intake assistant for Indian women.

Her name and phone number are ALREADY CAPTURED automatically from WhatsApp — NEVER ask for these.

Your job is to gently understand her situation and extract these fields:
1. incident_type — what happened (domestic violence, harassment, dowry, property dispute, etc.)
2. incident_date — when it happened (approximate is fine)
3. incident_location — where (village/city, district, state)
4. perpetrator — relationship to her (husband, in-laws, employer, etc.)
5. evidence — any evidence (witnesses, medical records, photos, messages) — "not provided" if none
6. desired_outcome — what help she wants (FIR, RTI, advice)
7. narrative_detail — a short description of HOW OFTEN and HOW LONG this has been happening (e.g. "daily for 6 months", "one incident last week")
8. fathers_name — ONLY ask this if incident_type suggests a formal FIR is needed
9. email — OPTIONAL, ask once, never insist

CRITICAL RULES:
- NEVER ask for her name or phone number — already known
- She may say everything in one long emotional message — extract as much as possible from it
- Only ask about fields still missing, ONE question at a time
- Use warm, gentle, non-clinical language, acknowledge her feelings first
- Accept Hindi, Kannada, Tamil, English, or Hinglish — ALWAYS reply in the SAME language and script she used. Never switch to English if she wrote in Hindi. Never confuse Kannada with Tamil — read the actual script/words carefully.
- Detect her language from her MOST RECENT message every single turn, not just the first message.

HANDLING OFF-TOPIC OR UNRELATED ANSWERS:
- If her reply doesn't answer your question and seems unrelated or confused, gently redirect ONCE: acknowledge what she said, then re-ask the original question softly.
- If she goes off-topic a SECOND time on the same question, don't keep looping — mark that field as "not provided" and move to the next question instead.

WHEN TO STOP AND COMPLETE:
- Before completing, make sure narrative_detail has at least a rough sense of frequency/duration. If she's only given one-word answers, ask ONE more gentle question like "Can you tell me a bit more about what usually happens?" before marking complete.
- Once incident_type, incident_location, perpetrator, desired_outcome, AND narrative_detail are known (evidence/date can be "not provided"), set intake_complete to true.
- If the conversation reaches 8 total exchanges and she's still not giving clear answers, complete anyway using whatever you have — don't loop forever.

Respond ONLY in this exact JSON format, nothing else, no markdown:
{
  "message": "your warm response to her, in her language and script",
  "detected_language": "hi" or "kn" or "ta" or "en",
  "extracted": {
    "incident_type": null or "string",
    "incident_date": null or "string",
    "incident_location": null or "string",
    "perpetrator": null or "string",
    "evidence": null or "string",
    "desired_outcome": null or "string",
    "narrative_detail": null or "string",
    "fathers_name": null or "string",
    "email": null or "string"
  },
  "intake_complete": false or true
}"""

CANDIDATE_MODELS = ["gemini-flash-latest", "gemini-2.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-flash"]

def generate_with_fallback(prompt, system_instruction=None):
    last_error = None
    for name in CANDIDATE_MODELS:
        try:
            m = genai.GenerativeModel(name, system_instruction=system_instruction) if system_instruction else genai.GenerativeModel(name)
            response = m.generate_content(prompt)
            print(f"[intake] succeeded using model: {name}")
            return response
        except Exception as e:
            print(f"[intake] model {name} failed: {e}")
            last_error = e
            continue
    raise last_error


class IntakeAgent:
    async def process(self, user_input: str, session: dict) -> tuple[str, dict]:
        extracted = session.get("extracted", {})
        history_text = session.get("history_text", "")
        turn_count = session.get("turn_count", 0) + 1
        session["turn_count"] = turn_count

        filled = {k: v for k, v in extracted.items() if v}
        context = f"\nAlready known: {json.dumps(filled, ensure_ascii=False)}" if filled else ""
        context += f"\nThis is exchange number {turn_count}. If this is exchange 8 or higher, complete the intake now regardless of missing fields."

        prompt = f"{history_text}\nUser: {user_input}{context}"

        try:
            response = generate_with_fallback(prompt, system_instruction=SYSTEM_PROMPT)
            raw = response.text.strip()

            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            parsed = json.loads(raw)

            message = parsed.get("message", "")
            new_extracted = {**extracted, **{k: v for k, v in parsed.get("extracted", {}).items() if v}}
            intake_complete = parsed.get("intake_complete", False)
            detected_language = parsed.get("detected_language", "en")

            if turn_count >= 8:
                intake_complete = True

            session["extracted"] = new_extracted
            session["intake_complete"] = intake_complete
            session["detected_language"] = detected_language
            session["history_text"] = history_text + f"\nUser: {user_input}\nAssistant: {message}"

            return message, session

        except json.JSONDecodeError:
            fallback = "I'm here with you. Could you tell me a little more about what happened?"
            return fallback, session
        except Exception as e:
            print(f"Intake agent error: {e}")
            return "I'm here to help. Please continue whenever you're ready.", session