from fastapi import FastAPI
import os
from dotenv import load_dotenv

# Load explicitly from the project root if running locally
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from api.routers import meeting_router, briefing_router, risks_router

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

@app.get("/")
def read_root():
    return {"status": "online", "message": "Copilot Sales Agent API is running. Please test via the React frontend on localhost:3000."}

app.include_router(meeting_router.router)
app.include_router(briefing_router.router)
app.include_router(risks_router.router)
