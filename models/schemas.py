"""
Pydantic schemas for API requests and responses
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    user_name: str = Field(..., description="Name of the user")
    user_id: str = Field(..., description="Unique identifier for the user")


class UserResponse(BaseModel):
    """Schema for user response"""
    user_id: str
    user_name: str
    uuid: str
    created_at: datetime
    summary: Optional[str] = None


class SessionCreate(BaseModel):
    """Schema for creating a therapy session"""
    session_summary: str = Field(..., description="Text summary of the therapy session")
    session_date: datetime = Field(default_factory=lambda: datetime.utcnow(), description="Date/time of the session")
    session_number: Optional[int] = Field(None, description="Sequential session number (auto-generated if not provided)")


class SessionResponse(BaseModel):
    """Schema for session response"""
    session_id: str
    session_number: int
    session_date: datetime
    episode_uuid: str
    message: str


class ProfileQuery(BaseModel):
    """Schema for profile query request"""
    query: str = Field(..., description="Natural language query about the user")
    user_id: str = Field(..., description="User ID to query")


class ProfileResult(BaseModel):
    """Schema for a single profile search result"""
    uuid: str
    fact: str
    valid_at: Optional[datetime] = None
    invalid_at: Optional[datetime] = None


class ProfileQueryResponse(BaseModel):
    """Schema for profile query response"""
    query: str
    results: List[ProfileResult]
    count: int


class CenterNodeQuery(BaseModel):
    """Schema for center node query request"""
    query: str = Field(..., description="Search query")
    center_node_uuid: str = Field(..., description="UUID of the center node for reranking")
    user_id: str = Field(..., description="User ID")


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str
    detail: Optional[str] = None


class DeleteUserResponse(BaseModel):
    """Schema for user deletion response"""
    user_id: str
    deleted_nodes: int
    deleted_relationships: int
    status: str
    message: str

