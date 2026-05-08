# PRD 03 — Agent 4: HazMat Protocol Officer (RAG)
**File:** `backend/agents/hazmat_agent.py` + `backend/routers/hazmat.py` + `backend/data/regulations/`

---

## Objective

Implement the RAG-powered HazMat safety agent. When the driver selects a PURPLE bin, this agent queries a curated knowledge base of Indian waste management regulations and generates a localized, context-aware safety brief in real-time using the Anthropic Claude API.

---

## Regulatory Knowledge Base

**Directory:** `backend/data/regulations/`

Create three text files containing the key excerpts relevant to hazardous waste handling. The RAG agent injects these as context into the LLM prompt.

### File: `osh_code_2020.txt`

```
OCCUPATIONAL SAFETY, HEALTH AND WORKING CONDITIONS CODE, 2020
Relevant Sections for Hazardous Waste Handling

Section 15 - Duties of Employers re: Hazardous Processes:
- Employers must maintain health records for workers handling hazardous substances.
- Every worker handling hazardous materials must be provided appropriate PPE at no cost.
- Mandatory training on safe handling procedures before assignment to hazardous tasks.

Section 22 - Personal Protective Equipment:
- Class-D fire gloves (leather, heat-resistant to 300°C) required for lithium battery handling.
- N95 or P100 respirators required for dust-generating hazardous waste operations.
- Full-face shields required when handling chemical drums with unknown contents.
- Chemical-resistant aprons and boot covers for liquid chemical spill scenarios.

Section 31 - Emergency Procedures:
- All hazardous waste vehicles must carry a Hazchem emergency response kit.
- Driver must not attempt to move a lithium battery showing visible damage or thermal event.
- Emergency contact: National Chemical Emergency Centre (NCEC): 0120-2588081.
- Lithium fires: NEVER use water. Use Class-D extinguisher (dry sand or copper powder).
```

### File: `solid_waste_management_rules_2016.txt`

```
SOLID WASTE MANAGEMENT RULES, 2016
Ministry of Environment, Forest and Climate Change

Rule 4 - Segregation at Source:
- Hazardous waste (batteries, e-waste, chemicals) must never be mixed with general municipal solid waste.
- Generators of hazardous waste are responsible for proper segregation before handover.
- Color coding: Black bag = general waste, Green bag = wet waste, Red bag = hazardous/biomedical.

Rule 16 - Transportation of Hazardous Waste:
- Hazardous waste must be transported in sealed, leak-proof containers with hazard labels.
- Transport vehicles must display HAZCHEM placards appropriate to the waste class.
- Lithium-ion batteries fall under Class 9 (Miscellaneous Dangerous Goods) per ADG code.
- Medical waste (syringes) falls under Class 6.2 (Infectious Substances).

Rule 22 - Treatment and Disposal Facilities:
- Class 9 (Lithium batteries): Must be sent to authorized e-waste dismantler/recycler.
- Class 6.2 (Biomedical): Must go to Common Biomedical Waste Treatment Facility (CBWTF).
- Chemical drums (unlabeled): Must go to TSDF (Treatment, Storage, and Disposal Facility).
- No hazardous waste to be landfilled without prior treatment authorization from SPCB.

Rule 24 - Swachh Bharat Mission 2.0 Compliance:
- All ULBs must achieve 100% scientific disposal of hazardous waste by 2026.
- Door-to-door hazardous waste collection to be integrated into regular SWM schedule.
```

### File: `cpcb_guidelines.txt`

```
CENTRAL POLLUTION CONTROL BOARD (CPCB) — HAZARDOUS WASTE GUIDELINES

Authorized Disposal Facilities (Bengaluru):
- KSPCB TSDF (Class 9 / Chemical): Dobaspet Industrial Area, Bengaluru — 560090
  Contact: +91-80-23440985
- Saahas Zero Waste (E-Waste / Lithium): Whitefield, Bengaluru — 560066
  Contact: +91-80-41134585
- Parikrama CBWTF (Biomedical): Bommasandra, Bengaluru — 560099
  Contact: +91-80-27834500

Lithium Battery Specific Protocol (CPCB Circular 2022):
- Do not stack damaged lithium batteries. Transport individually in sand-filled containers.
- Minimum 1m separation from other flammable materials during transport.
- If battery is hot or swollen: do not handle. Call NCEC immediately: 0120-2588081.

Medical Waste (Syringes) Protocol:
- Use puncture-resistant containers only (yellow rigid sharps box).
- Never recap needles. Place directly into sharps container.
- Double-bag the sharps container in red biohazard bags before loading into vehicle.
- Driver must wear nitrile gloves (minimum 5 mil thickness) + face shield.

Chemical Drum (Unknown Contents) Protocol:
- Do not open. Do not tip. Keep upright at all times.
- Full-face respirator required (SCBA if confined space).
- Photograph label remnants and report to KSPCB hazmat team before transport.
- Transport only after KSPCB hazmat team verbal clearance.
```

---

## Agent Implementation

**File:** `backend/agents/hazmat_agent.py`

```python
import os
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

REGULATIONS_DIR = Path(__file__).parent.parent / "data" / "regulations"

def load_regulations() -> str:
    """Load all regulation text files into a single context string."""
    docs = []
    for file in REGULATIONS_DIR.glob("*.txt"):
        docs.append(f"=== {file.stem.upper()} ===\n{file.read_text()}")
    return "\n\n".join(docs)


SYSTEM_PROMPT = """You are the ClearGrid HazMat Protocol Officer, an AI safety agent for BBMP (Bruhat Bengaluru Mahanagara Palike) municipal waste collection workers.

Your role is to generate concise, actionable safety briefs for garbage truck drivers who have encountered hazardous materials in a bin. You cite Indian regulations (OSH Code 2020, Solid Waste Management Rules 2016, CPCB Guidelines) and always specify:

1. The specific PPE required BEFORE approaching the bin
2. Step-by-step handling procedure (max 4 steps)
3. Whether the standard route must be changed and where to go instead
4. Emergency contact if applicable

Format your response as structured Markdown. Keep it under 300 words. Write for a driver reading on a mobile screen — be direct, not verbose. Always cite the specific regulation clause."""


def generate_safety_brief(node_id: str, hazard_type: str) -> dict:
    """
    Agent 4: RAG-powered safety protocol generation.
    Retrieves regulation context, generates driver safety brief via LLM.
    """
    regulations_context = load_regulations()
    
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
    
    user_prompt = f"""
Bin ID: {node_id}
Hazard Detected: {hazard_type}

Using ONLY the regulations provided below, generate a safety brief for the driver.

REGULATORY CONTEXT:
{regulations_context}
"""
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    safety_text = message.content[0].text
    
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
        "regulation_citations": citations[:5],  # cap at 5
        "reroute_required": disposal_facility is not None,
        "disposal_facility": disposal_facility
    }
```

---

## HazMat Router

**File:** `backend/routers/hazmat.py`

```python
from fastapi import APIRouter, HTTPException
from data.loader import load_bins
from agents.hazmat_agent import generate_safety_brief

router = APIRouter(tags=["HazMat"])

@router.get("/hazmat/{node_id}")
def get_hazmat_brief(node_id: str):
    """
    Triggers Agent 4 for a specific PURPLE bin.
    Generates real-time safety brief with Indian regulatory citations.
    """
    bins = load_bins()
    bin_data = next((b for b in bins if b["node_id"] == node_id), None)
    
    if not bin_data:
        raise HTTPException(status_code=404, detail=f"Bin {node_id} not found")
    
    if not bin_data["hazard_detected"]:
        raise HTTPException(
            status_code=400,
            detail=f"Bin {node_id} has no hazard detected. Only PURPLE bins trigger HazMat protocol."
        )
    
    brief = generate_safety_brief(
        node_id=node_id,
        hazard_type=bin_data["hazard_classification"]
    )
    
    return brief
```

---

## Expected Response Example

```json
{
  "node_id": "BIN_219",
  "hazard_type": "Exposed Lithium Battery",
  "safety_instructions": "## ⚠️ HAZMAT ALERT — Exposed Lithium Battery\n\n**Before approaching:**\n- Class-D fire gloves (OSH Code 2020, Section 22)\n- N95 respirator\n- Full-face shield\n\n**Procedure:**\n1. Do NOT place in standard bin — segregate immediately per SWM Rules 2016, Rule 4\n2. Place battery individually in sand-filled container (CPCB Circular 2022)\n3. Maintain 1m separation from flammables\n4. Do not transport if battery is hot or swollen — call NCEC: 0120-2588081\n\n**Route updated:** Proceed to Saahas Zero Waste, Whitefield after collection.",
  "regulation_citations": [
    "OSH Code 2020, Section 22 — Class-D fire gloves required",
    "SWM Rules 2016, Rule 16 — Class 9 transport requirements"
  ],
  "reroute_required": true,
  "disposal_facility": {
    "name": "Saahas Zero Waste (E-Waste)",
    "lat": 12.9698,
    "lng": 77.7499,
    "address": "Whitefield, Bengaluru — 560066"
  }
}
```

---

## Acceptance Criteria

- [ ] `GET /api/v1/hazmat/{node_id}` returns a valid brief for any PURPLE bin node_id
- [ ] `safety_instructions` contains specific Indian regulation references (not generic advice)
- [ ] `reroute_required` is `true` for all PURPLE bins
- [ ] `disposal_facility` is non-null and facility name matches hazard type
- [ ] Returns 400 for non-hazardous bins
- [ ] Returns 404 for unknown node_id
- [ ] Response arrives in under 10 seconds (LLM call + context injection)
- [ ] Regulations are injected from local text files, not hallucinated by the model
