from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import players, ml
app = FastAPI(title="TradeValue API", version="0.1.0")

# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# uvicorn app.main:app --reload

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "TradeValue API", "version": "0.1.0"}

app.include_router(players.router, prefix="/api/players", tags=["players"])
app.include_router(ml.router, prefix="/api/ml", tags=["ml"])
