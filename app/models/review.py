from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ReviewMetadata(BaseModel):
    source: Optional[str] = None
    language: Optional[str] = None
    timestamp: Optional[datetime] = None

class ReviewRequest(BaseModel):
    review_id: str
    text: str
    metadata: Optional[ReviewMetadata] = None

class ReviewAnalysis(BaseModel):
    sentiment: str = Field(..., description="positive, negative, or mixed")
    key_topics: List[str]
    response_recommendation: str
    urgency_score: int = Field(..., ge=1, le=5)

class ConfidenceScores(BaseModel):
    sentiment: float = Field(..., ge=0.0, le=1.0)
    topic_accuracy: float = Field(..., ge=0.0, le=1.0)

class ReviewResponse(BaseModel):
    review_id: str
    analysis: ReviewAnalysis
    confidence_scores: ConfidenceScores 