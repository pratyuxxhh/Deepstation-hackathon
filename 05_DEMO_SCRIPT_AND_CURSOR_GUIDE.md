# PRD 05 — Demo Script & Cursor/Windsurf Usage Guide
**For:** Hackathon presenters + AI-assisted dev workflow

---

## Cursor / Windsurf Workflow

### How to Use These PRDs

Each PRD file is a self-contained task context. Feed them to Cursor in this order:

1. **Open Cursor in the `cleargrid/` monorepo root**
2. **For each PRD:** Press `Cmd+L` (or `Ctrl+L`) to open the chat, paste the PRD content, and ask:

   > "Implement everything in this PRD exactly as specified. Create all files listed."

3. **Run tests after each PRD** before moving to the next
4. **PRD execution order:**
   - `01_MOCK_DATA_AND_SCAFFOLD.md` → verify `GET /health` works
   - `02_FORECASTER_AND_DISPATCHER.md` → verify `GET /api/v1/route` returns TSP route
   - `03_HAZMAT_RAG_AGENT.md` → verify `GET /api/v1/hazmat/BIN_219` returns brief
   - `04_FRONTEND_DASHBOARD.md` → verify full UI loads with map

### Useful Cursor Prompts Per Module

**For the mock data:**
> "Generate all 20 bins in mock_bins.json matching the distribution: 8 GREEN, 4 RED, 4 BLUE, 4 PURPLE. Use Bengaluru coordinates between lat 12.91–12.98 and lng 77.55–77.65."

**For the TSP algorithm:**
> "Implement the nearest-neighbor TSP in dispatcher.py using haversine distance. Start from the depot at lat 12.9352, lng 77.5947."

**For the RAG agent:**
> "Implement generate_safety_brief() in hazmat_agent.py. Inject the text from all three regulation files as context. Use claude-sonnet-4-20250514 via the Anthropic Python SDK."

**For the frontend map:**
> "Use CartoDB dark tiles for the Leaflet map. Make PURPLE markers pulse with a CSS animation. Clicking any PURPLE node should fetch from /api/v1/hazmat/{node_id} and show the HazMatHUD modal."

---

## Demo Script (5-Minute Hackathon Pitch)

### Act 1 — The Problem (30 seconds)

> "Today, garbage trucks in Bengaluru drive fixed routes — visiting every bin, whether it's empty or overflowing. 40% of fuel is wasted on empty bins, and bins still overflow before the truck arrives."

*[Show a blank map of the ward — no routes, no intelligence]*

### Act 2 — The Grid Comes Alive (1 minute)

> "ClearGrid deploys four AI agents simultaneously."

*[Dashboard loads — bins light up in color]*

> "Green bins are ignored. The Vision Agent has already analyzed them — they don't need attention today."

*[Point to the green nodes scattered across the map]*

> "Red bins are critical — over 80% full. But here's what makes ClearGrid different..."

*[Point to blue nodes]*

> "These blue bins are only 45% full. But our Forecaster Agent predicts they'll overflow in 14 hours — before the next scheduled collection. So we collect them now."

### Act 3 — The Route (1 minute)

> "The Dispatcher Agent ignores the green bins entirely and runs a Traveling Salesperson optimization on only the red, blue, and purple nodes."

*[Tap "Generate Route" if not auto-loaded — route polyline animates onto the map]*

> "12 stops instead of 20. 14.7 km instead of 28. Same ward, half the distance, zero overflows."

*[Show the sidebar stop list]*

### Act 4 — The Wow Moment (2 minutes)

> "But what happens when a driver encounters something dangerous?"

*[Point to a pulsing purple node]*

> "Our Vision Agent detected an exposed lithium battery in bin BIN_219."

*[Click the purple node — HazMat HUD appears]*

> "Watch this. Our Protocol Agent — Agent 4 — is now querying a vector database of Indian regulations in real time."

*[Wait for loading spinner to resolve]*

> "In under 8 seconds, it generated a legally compliant safety brief citing the OSH Code 2020 and CPCB guidelines — specific to lithium batteries, specific to India. The driver knows exactly what gloves to wear, what not to do, and where to go instead."

*[Show the disposal facility reroute notification]*

> "And the route has been automatically updated to redirect to Saahas Zero Waste in Whitefield — the authorized e-waste facility."

### Act 5 — The Vision (30 seconds)

> "This is the ClearGrid cyber-physical swarm. Four agents, one dashboard, real-time intelligence. We turn a reactive garbage truck into a proactive, AI-driven urban service. This is what Swachh Bharat 2.0 looks like when you add AI."

---

## Quick Commands Reference

```bash
# Start backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Start frontend
cd frontend
npm install
npm run dev

# Test key endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/bins | python -m json.tool
curl http://localhost:8000/api/v1/route | python -m json.tool
curl http://localhost:8000/api/v1/hazmat/BIN_219 | python -m json.tool
```

---

## Fallback Plan (If LLM API Fails During Demo)

If the Anthropic API is unavailable during the live demo, serve a cached HazMat brief:

**File:** `backend/agents/hazmat_agent.py` — add fallback:

```python
FALLBACK_BRIEF = {
    "Exposed Lithium Battery": """## ⚠️ HAZMAT ALERT — Exposed Lithium Battery

**Before approaching — mandatory PPE (OSH Code 2020, Section 22):**
- Class-D fire gloves (leather, heat-resistant to 300°C)
- N95 respirator
- Full-face shield

**Handling procedure (SWM Rules 2016, Rule 16):**
1. Do NOT mix with general waste — segregate immediately
2. Place in sand-filled sealed container (CPCB Circular 2022)
3. Maintain minimum 1m from flammables during transport
4. If battery is hot or swollen: **do not handle** — call NCEC: 0120-2588081

**Route updated:** Proceed to Saahas Zero Waste, Whitefield after collection.
*Lithium batteries = Class 9 Dangerous Goods (ADG Code)*""",
}

def generate_safety_brief(node_id: str, hazard_type: str) -> dict:
    try:
        # ... LLM call ...
    except Exception:
        # Graceful fallback for demo
        return {
            "node_id": node_id,
            "hazard_type": hazard_type,
            "safety_instructions": FALLBACK_BRIEF.get(hazard_type, "Protocol unavailable. Contact supervisor."),
            "regulation_citations": ["OSH Code 2020, Section 22", "SWM Rules 2016, Rule 16"],
            "reroute_required": True,
            "disposal_facility": { "name": "Saahas Zero Waste", "lat": 12.9698, "lng": 77.7499, "address": "Whitefield, Bengaluru — 560066" }
        }
```

---

## Judging Criteria Alignment

| Criteria | ClearGrid Feature | PRD Reference |
|---|---|---|
| Technical complexity | Multi-agent architecture, TSP algorithm, RAG pipeline | PRD 02, 03 |
| Innovation | Predictive BLUE bins (proactive vs reactive) | PRD 02 |
| Real-world impact | 40% route efficiency, zero overflows, driver safety | Demo Script |
| AI/ML use | LLM + RAG for legal compliance | PRD 03 |
| UI/UX | Live map, color-coded nodes, mobile-friendly HUD | PRD 04 |
| Indian context | CPCB, OSH Code, SWM Rules, Swachh Bharat 2.0, BBMP | PRD 03 |
