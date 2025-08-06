"""
MINIMAL FastAPI test for Railway deployment
No imports, no dependencies, no database, no Firebase - just basic FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Railway Test", version="1.0.0")

# Basic CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Railway test working", "status": "ok"}

@app.get("/healthz")  
def health():
    return {"status": "ok"}

@app.get("/test")
def test():
    return {"test": "minimal", "working": True}