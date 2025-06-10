from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ReviewMetadata(BaseModel):
    source: str
    subreddit: Optional[str] = None
    score: Optional[int] = None
    upvote_ratio: Optional[float] = None
    num_comments: Optional[int] = None
    created_utc: Optional[float] = None

class RedditPost(BaseModel):
    id: str
    title: str
    text: str
    score: int
    upvote_ratio: float
    num_comments: int
    created_utc: float
    subreddit: str
    author: str
    url: str
    permalink: str
    platform: str = "reddit"

class RedditData(BaseModel):
    posts: List[RedditPost]

class RawData(BaseModel):
    reddit: RedditData

class SentimentAnalysisInput(BaseModel):
    query: str
    timestamp: datetime
    platforms: List[str]
    raw_data: RawData

class ReviewAnalysis(BaseModel):
    sentiment: str = Field(..., description="positive, negative, or mixed")
    key_topics: List[str]
    response_recommendation: str
    urgency_score: int = Field(..., ge=1, le=5)

class ConfidenceScores(BaseModel):
    sentiment: float = Field(..., ge=0.0, le=1.0)
    topic_accuracy: float = Field(..., ge=0.0, le=1.0)

class ReviewRequest(BaseModel):
    review_id: str
    text: str
    metadata: ReviewMetadata

class ReviewResponse(BaseModel):
    review_id: str
    analysis: ReviewAnalysis
    confidence_scores: ConfidenceScores 