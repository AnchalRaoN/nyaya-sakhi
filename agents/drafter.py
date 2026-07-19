import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
CANDIDATE_MODELS = ["gemini-flash-latest", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

def _get_working_model():
    for name in CANDIDATE_MODELS:
        try:
            return genai.GenerativeModel(name), name
        except Exception:
            continue
    raise RuntimeError("No available Gemini model found")

model, ACTIVE_MODEL = _get_working_model()
print(f"Law RAG agent using model: {ACTIVE_MODEL}")


class DrafterAgent:
    async def process(self, session: dict) -> tuple[str, dict]:
        case = session.get("extracted", {})
        laws = session.get("law_sections", [])

        incident_type    = case.get("incident_type", "the incident")
        location         = case.get("incident_location", "the location")
        date             = case.get("incident_date", "the date")
        perpetrator      = case.get("perpetrator", "the person")
        evidence         = case.get("evidence", "available evidence")
        narrative        = case.get("narrative_detail", "")
        complainant_name = case.get("complainant_name", "")
        fathers_name     = case.get("fathers_name", "")
        phone            = case.get("complainant_phone", "")

        law_text = "\n".join([
            f"- {l.get('act')}, {l.get('section')}: {l.get('description')}"
            for l in laws
        ])

        known_fields = ""
        if complainant_name:
            known_fields += f"- Complainant name: {complainant_name}\n"
        if fathers_name:
            known_fields += f"- Father's name: {fathers_name}\n"
        if phone:
            known_fields += f"- Contact number: {phone}\n"

        prompt = f"""Write a formal FIR (First Information Report) application.

Case details:
- Incident type: {incident_type}
- Date: {date}
- Location: {location}
- Perpetrator: {perpetrator}
- Evidence: {evidence}
- Frequency/duration: {narrative}
{known_fields}

Applicable laws:
{law_text}

CRITICAL RULES:
- Only include a field (complainant name, father's name, contact number) if actual data is given above.
- If a field is NOT provided, DO NOT write a placeholder like "[Father's Name]" or "___________" — OMIT that line entirely.
- Use the frequency/duration detail to make the narrative specific and credible, not generic.
- ONLY cite the exact laws listed above — do not add any other acts or sections.

Format:
1. To: Station House Officer heading
2. First-person narrative of the incident (use the frequency/duration detail)
3. Cited legal sections (exactly as listed above, nothing else)
4. Prayer/request section
5. Signature block (use complainant name if provided, otherwise just "Complainant")

Keep it formal but readable English."""

        try:
            response = model.generate_content(prompt)
            fir_text = response.text.strip()
            session["fir_draft"] = fir_text
            session["stage"] = "complete"
            return "", session  # message text now built by templates in main.py

        except Exception as e:
            print(f"Drafter error: {e}")
            session["stage"] = "complete"
            session["fir_draft"] = ""
            return "", session