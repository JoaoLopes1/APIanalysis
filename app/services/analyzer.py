from textblob import TextBlob
import numpy as np
from app.models.review import ReviewAnalysis, ConfidenceScores
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ReviewAnalyzer:
    def __init__(self):
        # No initialization needed for TextBlob
        # Load response generation templates
        self.response_templates = {
            "positive": "Thank you for your positive feedback! {}",
            "negative": "We apologize for your experience. {}",
            "mixed": "Thank you for your feedback. {}"
        }
    
    def analyze(self, text: str, source: Optional[str] = None, language: Optional[str] = None) -> Dict[str, Any]:
        try:
            # Perform sentiment analysis using TextBlob
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Map polarity to sentiment categories
            sentiment = self._map_sentiment(polarity)
            sentiment_confidence = abs(polarity)  # Use absolute polarity as confidence
            
            # Extract key topics
            topics = self._extract_topics(text)
            
            # Generate response recommendation
            response = self._generate_response(sentiment, topics)
            
            # Calculate urgency score
            urgency = self._calculate_urgency(sentiment, text)
            
            # Create analysis result
            analysis = ReviewAnalysis(
                sentiment=sentiment,
                key_topics=topics,
                response_recommendation=response,
                urgency_score=urgency
            )
            
            confidence_scores = ConfidenceScores(
                sentiment=float(sentiment_confidence),
                topic_accuracy=0.85  # This would be dynamic in a production environment
            )
            
            return {
                "analysis": analysis,
                "confidence_scores": confidence_scores
            }
            
        except Exception as e:
            logger.error(f"Error in review analysis: {str(e)}")
            raise
    
    def _map_sentiment(self, polarity: float) -> str:
        # Map TextBlob polarity to our sentiment categories
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        return "mixed"
    
    def _extract_topics(self, text: str) -> list:
        # Simple keyword-based topic extraction (would use BERTopic in production)
        keywords = {
            "payment": "payment",
            "crash": "stability",
            "bug": "stability",
            "design": "ui",
            "interface": "ui",
            "slow": "performance",
            "fast": "performance",
            "price": "pricing",
            "expensive": "pricing",
            "support": "customer_service"
        }
        
        topics = set()
        text_lower = text.lower()
        
        for keyword, topic in keywords.items():
            if keyword in text_lower:
                topics.add(topic)
        
        return list(topics) if topics else ["general"]
    
    def _generate_response(self, sentiment: str, topics: list) -> str:
        # Template-based response generation
        base_template = self.response_templates.get(sentiment, self.response_templates["mixed"])
        
        if "stability" in topics:
            detail = "Our team is investigating the stability issues and working on a fix."
        elif "performance" in topics:
            detail = "We're continuously working on improving the app's performance."
        elif "ui" in topics:
            detail = "We appreciate your feedback about the user interface."
        else:
            detail = "We value your input and are constantly working to improve our service."
        
        return base_template.format(detail)
    
    def _calculate_urgency(self, sentiment: str, text: str) -> int:
        # Simple urgency scoring logic
        base_score = 1
        
        # Increase score for negative sentiment
        if sentiment == "negative":
            base_score += 2
        elif sentiment == "mixed":
            base_score += 1
            
        # Check for urgent keywords
        urgent_keywords = ["crash", "error", "bug", "broken", "unusable", "urgent"]
        for keyword in urgent_keywords:
            if keyword in text.lower():
                base_score += 1
                break
                
        return min(base_score, 5)  # Cap at 5 