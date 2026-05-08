from fastapi import APIRouter
from data.loader import load_bins

router = APIRouter(tags=["Bins"])

@router.get("/bins")
def get_bins():
    """Returns all bin nodes with precomputed status_color."""
    return load_bins()
