from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging
from app.models.review import ReviewRequest, ReviewResponse, ReviewAnalysis, ConfidenceScores
from app.services.analyzer import ReviewAnalyzer
from app.auth.auth_handler import validate_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Review Analysis API")
security = HTTPBearer()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the analyzer service
analyzer = ReviewAnalyzer()

@app.post("/analyze-review", response_model=ReviewResponse)
async def analyze_review(
    review: ReviewRequest,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    try:
        # Validate token
        validate_token(credentials.credentials)
        
        # Perform the analysis
        result = analyzer.analyze(
            text=review.text,
            source=review.metadata.source if review.metadata else None,
            language=review.metadata.language if review.metadata else None
        )
        
        # Construct the response
        response = ReviewResponse(
            review_id=review.review_id,
            analysis=result["analysis"],
            confidence_scores=result["confidence_scores"]
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 