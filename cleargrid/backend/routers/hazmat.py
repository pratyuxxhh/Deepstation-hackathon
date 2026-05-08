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
