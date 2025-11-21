import os
from datetime import datetime
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

from database import create_document, get_documents
from schemas import Backstory, ActionReport, Event, Quest, Character

app = FastAPI(title="Twist of Fate RP Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------- Helpers ---------------------------- #

def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not doc:
        return doc
    d = dict(doc)
    _id = d.pop("_id", None)
    if _id is not None:
        d["id"] = str(_id)
    # Convert datetimes to isoformat for JSON safety
    for k, v in list(d.items()):
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


def _serialize_list(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [_serialize(x) for x in items]


# ---------------------------- Basic ----------------------------- #

@app.get("/")
def read_root():
    return {"message": "Twist of Fate API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            collections = db.list_collection_names()
            response["collections"] = collections[:10]
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


@app.get("/schema")
def get_schema():
    # Expose minimal schema info for admin tools/viewers
    from schemas import Character, Backstory, ActionReport, Event, Quest
    def model_fields(model: BaseModel) -> dict:
        return {k: str(v.annotation) for k, v in model.model_fields.items()}
    return {
        "character": model_fields(Character),
        "backstory": model_fields(Backstory),
        "actionreport": model_fields(ActionReport),
        "event": model_fields(Event),
        "quest": model_fields(Quest),
    }


# ------------------------- Characters --------------------------- #

@app.post("/characters")
def create_character(payload: Character):
    new_id = create_document("character", payload)
    return {"id": new_id}


@app.get("/characters")
def list_characters(owner_discord: Optional[str] = None):
    filt = {"owner_discord": owner_discord} if owner_discord else {}
    docs = get_documents("character", filt)
    return _serialize_list(docs)


# -------------------------- Backstories ------------------------- #

@app.post("/backstories")
def submit_backstory(payload: Backstory):
    new_id = create_document("backstory", payload)
    return {"id": new_id, "status": "received"}


@app.get("/backstories")
def list_backstories(status: Optional[str] = Query(None)):
    filt = {"status": status} if status else {}
    docs = get_documents("backstory", filt)
    return _serialize_list(docs)


# ------------------------ Action Reports ------------------------ #

@app.post("/reports")
def submit_report(payload: ActionReport):
    new_id = create_document("actionreport", payload)
    return {"id": new_id, "status": "received"}


@app.get("/reports")
def list_reports(character_name: Optional[str] = None):
    filt = {"character_name": character_name} if character_name else {}
    docs = get_documents("actionreport", filt)
    return _serialize_list(docs)


# ---------------------------- Events ---------------------------- #

@app.post("/events")
def create_event(payload: Event):
    new_id = create_document("event", payload)
    return {"id": new_id}


@app.get("/events")
def list_events(event_type: Optional[str] = None):
    filt = {"event_type": event_type} if event_type else {}
    docs = get_documents("event", filt)
    return _serialize_list(docs)


# ---------------------------- Quests ---------------------------- #

@app.post("/quests")
def create_quest(payload: Quest):
    new_id = create_document("quest", payload)
    return {"id": new_id}


@app.get("/quests")
def list_quests(status: Optional[str] = None):
    filt = {"status": status} if status else {}
    docs = get_documents("quest", filt)
    return _serialize_list(docs)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
