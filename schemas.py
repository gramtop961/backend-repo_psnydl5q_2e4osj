"""
Database Schemas for Twist of Fate (WoW RP Community)

Each Pydantic model represents a MongoDB collection.
Collection name = lowercase class name (e.g., Character -> "character").
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

# Core domain models

class Character(BaseModel):
    name: str = Field(..., description="Character name")
    race: str = Field(..., description="Race")
    clazz: str = Field(..., description="Class")
    faction: Literal["Alliance", "Horde", "Neutral"] = "Neutral"
    level: int = Field(1, ge=1, le=70)
    owner_discord: Optional[str] = Field(None, description="Owner Discord handle")
    bio: Optional[str] = Field(None, description="Short profile blurb")
    alignment: Optional[str] = Field(None, description="Alignment or worldview")
    skills: List[str] = Field(default_factory=list, description="Known skills")
    professions: List[str] = Field(default_factory=list, description="Professions")

class Backstory(BaseModel):
    character_name: str = Field(..., description="Reference by character name")
    title: str = Field(..., description="Backstory title")
    content: str = Field(..., description="Backstory text")
    tags: List[str] = Field(default_factory=list)
    status: Literal["submitted", "approved", "revisions"] = "submitted"

class ActionReport(BaseModel):
    character_name: str = Field(..., description="Actor character name")
    title: str
    content: str
    location: Optional[str] = None
    outcomes: List[str] = Field(default_factory=list)
    rewards_requested: List[str] = Field(default_factory=list)
    session_date: Optional[datetime] = None

class Event(BaseModel):
    title: str
    description: str
    date: datetime
    location: str
    organizer: Optional[str] = None
    event_type: Literal["quest", "dnd-session", "market", "tournament", "social"] = "quest"
    capacity: Optional[int] = None

class Quest(BaseModel):
    title: str
    description: str
    difficulty: Literal["easy", "normal", "hard", "epic"] = "normal"
    status: Literal["open", "in_progress", "completed"] = "open"
    rewards: List[str] = Field(default_factory=list)

class Item(BaseModel):
    name: str
    quality: Literal["poor", "common", "uncommon", "rare", "epic", "legendary"] = "common"
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class CraftRecipe(BaseModel):
    name: str
    result_item: str
    ingredients: List[dict] = Field(default_factory=list, description="List of {item, qty}")
    skill_required: Optional[str] = None

class SkillProgress(BaseModel):
    character_name: str
    skill: str
    rank: int = Field(1, ge=1)
    xp: int = Field(0, ge=0)

# Minimal user for permissions if needed later
class Member(BaseModel):
    nickname: str
    discord_id: Optional[str] = None
    roles: List[str] = Field(default_factory=lambda: ["member"])