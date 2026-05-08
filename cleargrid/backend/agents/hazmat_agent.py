"""Agent 4: HazMat Protocol Officer — RAG-powered safety brief generation via Groq."""

import os
from pathlib import Path
from openai import OpenAI

REGULATIONS_DIR = Path(__file__).parent.parent / "data" / "regulations"


def load_regulations() -> str:
    """Load all regulation text files into a single context string."""
    docs = []
    for file in sorted(REGULATIONS_DIR.glob("*.txt")):
        docs.append(f"=== {file.stem.upper()} ===\n{file.read_text()}")
    return "\n\n".join(docs)


SYSTEM_PROMPT = """You are the ClearGrid HazMat Protocol Officer, an AI safety agent for BBMP (Bruhat Bengaluru Mahanagara Palike) municipal waste collection workers.

Your role is to generate concise, actionable safety briefs for garbage truck drivers who have encountered hazardous materials in a bin. You cite Indian regulations (OSH Code 2020, Solid Waste Management Rules 2016, CPCB Guidelines) and always specify:

1. The specific PPE required BEFORE approaching the bin
2. Step-by-step handling procedure (max 4 steps)
3. Whether the standard route must be changed and where to go instead
4. Emergency contact if applicable

Format your response as structured Markdown. Keep it under 300 words. Write for a driver reading on a mobile screen — be direct, not verbose. Always cite the specific regulation clause."""


FALLBACK_BRIEF = {
    "Exposed Lithium Battery": """## HAZMAT ALERT — Exposed Lithium Battery

**Before approaching — mandatory PPE (OSH Code 2020, Section 22):**
- Class-D fire gloves (leather, heat-resistant to 300C)
- N95 respirator
- Full-face shield

**Handling procedure (SWM Rules 2016, Rule 16):**
1. Do NOT mix with general waste — segregate immediately
2. Place in sand-filled sealed container (CPCB Circular 2022)
3. Maintain minimum 1m from flammables during transport
4. If battery is hot or swollen: **do not handle** — call NCEC: 0120-2588081

**Route updated:** Proceed to Saahas Zero Waste, Whitefield after collection.
*Lithium batteries = Class 9 Dangerous Goods (ADG Code)*""",

    "Medical Waste (Syringes)": """## HAZMAT ALERT — Medical Waste (Syringes)

**Before approaching — mandatory PPE (OSH Code 2020, Section 22):**
- Nitrile gloves (minimum 5 mil thickness)
- Face shield
- Chemical-resistant apron

**Handling procedure (CPCB Guidelines):**
1. Use puncture-resistant yellow rigid sharps box ONLY
2. Never recap needles — place directly into sharps container
3. Double-bag sharps container in red biohazard bags
4. Load into vehicle in upright position only

**Route updated:** Proceed to Parikrama CBWTF, Bommasandra after collection.
*Medical waste = Class 6.2 Infectious Substances (SWM Rules 2016, Rule 16)*""",

    "Unlabeled Chemical Drum": """## HAZMAT ALERT — Unlabeled Chemical Drum

**Before approaching — mandatory PPE (OSH Code 2020, Section 22):**
- Full-face respirator (SCBA if confined space)
- Chemical-resistant aprons and boot covers
- Class-D fire gloves

**Handling procedure (CPCB Guidelines):**
1. Do NOT open. Do NOT tip. Keep upright at all times
2. Photograph label remnants and report to KSPCB hazmat team
3. Wait for KSPCB hazmat team verbal clearance before transport
4. Emergency contact: NCEC 0120-2588081

**Route updated:** Proceed to KSPCB TSDF, Dobaspet Industrial Area after collection.
*Chemical drums must go to TSDF (SWM Rules 2016, Rule 22)*""",
}


def generate_safety_brief(node_id: str, hazard_type: str) -> dict:
    """
    Agent 4: RAG-powered safety protocol generation.
    Retrieves regulation context, generates driver safety brief via Groq LLM.
    Falls back to cached brief if API is unavailable.
    """
    # Determine disposal facility based on hazard type
    facility_map = {
        "Exposed Lithium Battery": {
            "name": "Saahas Zero Waste (E-Waste)",
            "lat": 12.9698,
            "lng": 77.7499,
            "address": "Whitefield, Bengaluru — 560066"
        },
        "Medical Waste (Syringes)": {
            "name": "Parikrama CBWTF",
            "lat": 12.8399,
            "lng": 77.6826,
            "address": "Bommasandra, Bengaluru — 560099"
        },
        "Unlabeled Chemical Drum": {
            "name": "KSPCB TSDF",
            "lat": 13.1167,
            "lng": 77.3833,
            "address": "Dobaspet Industrial Area, Bengaluru — 560090"
        }
    }

    disposal_facility = facility_map.get(hazard_type)

    try:
        groq_key = os.environ.get("GROQ_API_KEY", "")
        if not groq_key:
            raise ValueError("GROQ_API_KEY not set — using fallback brief")

        client = OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1"
        )

        regulations_context = load_regulations()

        user_prompt = f"""Bin ID: {node_id}
Hazard Detected: {hazard_type}

Using ONLY the regulations provided below, generate a safety brief for the driver.

REGULATORY CONTEXT:
{regulations_context}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        safety_text = response.choices[0].message.content

        # Extract regulation citations from the response (simple heuristic)
        citations = []
        citation_triggers = [
            "OSH Code 2020", "SWM Rules 2016", "Rule ", "Section ", "CPCB"
        ]
        for line in safety_text.split("\n"):
            for trigger in citation_triggers:
                if trigger in line and line not in citations:
                    citations.append(line.strip())

        return {
            "node_id": node_id,
            "hazard_type": hazard_type,
            "safety_instructions": safety_text,
            "regulation_citations": citations[:5],
            "reroute_required": disposal_facility is not None,
            "disposal_facility": disposal_facility
        }

    except Exception:
        # Graceful fallback for demo
        return {
            "node_id": node_id,
            "hazard_type": hazard_type,
            "safety_instructions": FALLBACK_BRIEF.get(
                hazard_type, "Protocol unavailable. Contact supervisor."
            ),
            "regulation_citations": [
                "OSH Code 2020, Section 22",
                "SWM Rules 2016, Rule 16"
            ],
            "reroute_required": True,
            "disposal_facility": disposal_facility or {
                "name": "Saahas Zero Waste",
                "lat": 12.9698,
                "lng": 77.7499,
                "address": "Whitefield, Bengaluru — 560066"
            }
        }
