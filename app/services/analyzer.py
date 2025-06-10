from textblob import TextBlob
import numpy as np
from app.models.review import ReviewAnalysis, ConfidenceScores
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ReviewAnalyzer:
    def __init__(self):
        # Load response generation templates
        self.response_templates = {
            "positive": "Thank you for your positive feedback! {}",
            "negative": "We apologize for your experience. {}",
            "mixed": "Thank you for your feedback. {}"
        }
        
        # Reddit-specific keywords for topic extraction
        self.reddit_keywords = {
            # Content related
            "show": "content",
            "series": "content",
            "movie": "content",
            "documentary": "content",
            "season": "content",
            "episode": "content",
            "anime": "content",
            "film": "content",
            
            # Streaming experience
            "stream": "streaming",
            "buffer": "streaming",
            "quality": "streaming",
            "resolution": "streaming",
            "hdr": "streaming",
            "4k": "streaming",
            "offline": "streaming",
            "download": "streaming",
            
            # UI/UX
            "interface": "ui",
            "app": "ui",
            "design": "ui",
            "navigation": "ui",
            "menu": "ui",
            "layout": "ui",
            
            # Account/Subscription
            "price": "subscription",
            "cost": "subscription",
            "subscription": "subscription",
            "account": "subscription",
            "payment": "subscription",
            "billing": "subscription",
            "expensive": "subscription",
            "ads": "subscription",
            
            # Technical issues
            "crash": "technical",
            "bug": "technical",
            "error": "technical",
            "glitch": "technical",
            "broken": "technical",
            "loading": "technical",
            "freeze": "technical",
            
            # Customer service
            "support": "customer_service",
            "help": "customer_service",
            "service": "customer_service",
            "contact": "customer_service",
            "response": "customer_service"
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
            urgency = self._calculate_urgency(sentiment, text, source)
            
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
        # Topic extraction using Reddit-specific keywords
        topics = set()
        text_lower = text.lower()
        
        for keyword, topic in self.reddit_keywords.items():
            if keyword in text_lower:
                topics.add(topic)
        
        return list(topics) if topics else ["general"]
    
    def _generate_response(self, sentiment: str, topics: list) -> str:
        # Template-based response generation
        base_template = self.response_templates.get(sentiment, self.response_templates["mixed"])
        
        if "technical" in topics:
            detail = "Our team is investigating the technical issues and working on a fix."
        elif "streaming" in topics:
            detail = "We're continuously working on improving our streaming quality and performance."
        elif "subscription" in topics:
            detail = "We understand your concerns about our subscription service."
        elif "content" in topics:
            detail = "We appreciate your feedback about our content."
        elif "ui" in topics:
            detail = "We value your input about our user interface and design."
        elif "customer_service" in topics:
            detail = "We strive to provide the best customer service possible."
        else:
            detail = "We value your input and are constantly working to improve our service."
        
        return base_template.format(detail)
    
    def _calculate_urgency(self, sentiment: str, text: str, source: Optional[str] = None) -> int:
        # Enhanced urgency scoring logic for Reddit
        base_score = 1
        text_lower = text.lower()
        
        # Increase score for negative sentiment
        if sentiment == "negative":
            base_score += 2
        elif sentiment == "mixed":
            base_score += 1
            
        # Check for urgent keywords
        urgent_keywords = ["crash", "error", "bug", "broken", "unusable", "urgent", "not working", "down", "outage"]
        for keyword in urgent_keywords:
            if keyword in text_lower:
                base_score += 1
                break
        
        # For Reddit, consider post visibility
        if source == "reddit":
            # Check for high-visibility indicators
            visibility_keywords = ["everyone", "anyone else", "down for all", "global", "widespread"]
            for keyword in visibility_keywords:
                if keyword in text_lower:
                    base_score += 1
                    break
                
        return min(base_score, 5)  # Cap at 5 