from fastapi import APIRouter

router = APIRouter(tags=["HazMat"])

@router.get("/hazmat/{node_id}")
def get_hazmat_brief(node_id: str):
    """Triggers RAG agent for hazmat brief. Placeholder — agent logic in Phase 4."""
    return {
        "node_id": node_id,
        "hazard_type": "Unknown",
        "safety_instructions": "# Placeholder\n\nHazMat agent not yet implemented.",
        "regulation_citations": [],
        "reroute_required": False,
        "disposal_facility": None,
    }
