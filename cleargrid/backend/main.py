from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import bins, route, hazmat

app = FastAPI(title="ClearGrid API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bins.router, prefix="/api/v1")
app.include_router(route.router, prefix="/api/v1")
app.include_router(hazmat.router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok", "service": "ClearGrid API"}
