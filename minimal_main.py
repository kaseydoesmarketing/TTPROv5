"""
Minimal FastAPI app to test Railway deployment
This will help identify what's causing the 502 errors
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TitleTesterPro API - Minimal Test",
    description="Minimal version to test Railway deployment",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.titletesterpro.com", "https://titletesterpro.com", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"message": "TitleTesterPro API - Minimal Test", "status": "working"}

@app.get("/healthz")
def health():
    logger.info("Health endpoint called")
    return {"status": "ok", "test": "minimal"}

@app.get("/api/test")
def test_api():
    logger.info("Test API endpoint called")
    return {"message": "API working", "cors": "enabled"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)