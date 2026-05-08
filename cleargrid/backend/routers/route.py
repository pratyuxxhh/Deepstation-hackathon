import copy
from fastapi import APIRouter
from data.loader import load_bins
from agents.forecaster import run_forecaster
from agents.dispatcher import build_route

router = APIRouter(tags=["Route"])


@router.get("/route")
def get_optimized_route():
    """
    Runs the full agent pipeline:
    Agent 1 (precomputed in mock data) → Agent 2 (Forecaster) → Agent 3 (Dispatcher)
    Returns TSP-optimized route for all required bins.
    """
    bins = copy.deepcopy(load_bins())
    bins = run_forecaster(bins)
    route = build_route(bins)
    return route
