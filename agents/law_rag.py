import google.generativeai as genai
import os
import json

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


class LawRagAgent:
    def __init__(self):
        pass  # No ChromaDB dependency — always uses fresh Gemini lookup for accuracy

    async def search(self, case_info: dict) -> list[dict]:
        incident_type = case_info.get("incident_type", "")
        perpetrator = case_info.get("perpetrator", "")
        narrative = case_info.get("narrative_detail", "")
        return await self._gemini_law_lookup(incident_type, perpetrator, narrative)

    async def _gemini_law_lookup(self, incident_type: str, perpetrator: str, narrative: str) -> list[dict]:
        prompt = f"""You are an expert in Indian law for women's rights.

Case type: {incident_type}
Perpetrator: {perpetrator}
Details: {narrative}

List ONLY the legal provisions that DIRECTLY and SPECIFICALLY apply to THIS EXACT case.

STRICT RULES — READ CAREFULLY:
- If this is domestic violence / cruelty by husband or in-laws: ONLY include PWDVA 2005 and IPC 498A. Include IPC 304B ONLY if death or attempted murder is mentioned. Include Dowry Prohibition Act ONLY if dowry is explicitly mentioned.
- If this is workplace harassment by an employer/colleague: ONLY include POSH Act 2013.
- If this explicitly involves a minor/child victim: ONLY include POCSO 2012.
- If this is property/inheritance dispute: ONLY include Hindu Succession Act.
- NEVER include POCSO, POSH Act, or any unrelated act unless the case facts EXPLICITLY match that category. A husband hitting his wife is NEVER a POCSO or POSH case.
- Do not pad the list to reach a certain number. 2 highly relevant sections is better than 4 loosely related ones.

Return ONLY a JSON array, no markdown, no explanation:
[
  {{
    "act": "Full name of Act",
    "section": "Section number",
    "description": "One sentence describing how it applies to THIS specific case (not generic textbook wording)",
    "penalty": "Punishment for perpetrator"
  }}
]"""

        try:
            response = model.generate_content(prompt)
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw.strip())
        except Exception as e:
            print(f"Gemini law lookup failed: {e}")
            return self._default_sections(incident_type)

    def _default_sections(self, incident_type: str) -> list[dict]:
        incident_lower = (incident_type or "").lower()
        if "workplace" in incident_lower or "employer" in incident_lower or "office" in incident_lower:
            return [{
                "act": "Sexual Harassment of Women at Workplace Act (POSH), 2013",
                "section": "Section 3",
                "description": "Prohibits sexual harassment at workplace.",
                "penalty": "Disciplinary action, compensation to victim"
            }]
        return [
            {
                "act": "Protection of Women from Domestic Violence Act, 2005",
                "section": "Section 3",
                "description": "Covers physical, emotional, sexual, economic abuse by family members.",
                "penalty": "Protection orders, residence orders, monetary relief"
            },
            {
                "act": "Indian Penal Code",
                "section": "Section 498A",
                "description": "Criminalises cruelty and harassment by husband or relatives.",
                "penalty": "Imprisonment up to 3 years and fine"
            }
        ]