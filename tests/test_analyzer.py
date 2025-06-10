import pytest
from app.services.analyzer import ReviewAnalyzer
from app.models.review import ReviewAnalysis, ConfidenceScores

def test_analyzer_positive_sentiment():
    analyzer = ReviewAnalyzer()
    text = "The new Netflix show is amazing! Great storyline and excellent acting."
    result = analyzer.analyze(text, source="reddit")
    
    assert isinstance(result, dict)
    assert "analysis" in result
    assert "confidence_scores" in result
    
    analysis = result["analysis"]
    assert isinstance(analysis, ReviewAnalysis)
    assert analysis.sentiment == "positive"
    assert len(analysis.key_topics) > 0
    assert analysis.urgency_score >= 1 and analysis.urgency_score <= 5

def test_analyzer_negative_sentiment():
    analyzer = ReviewAnalyzer()
    text = "Netflix's new interface is terrible. Can't find anything anymore."
    result = analyzer.analyze(text, source="reddit")
    
    analysis = result["analysis"]
    assert analysis.sentiment == "negative"
    assert "ui" in analysis.key_topics

def test_analyzer_mixed_sentiment():
    analyzer = ReviewAnalyzer()
    text = "Good content but the streaming quality is poor sometimes."
    result = analyzer.analyze(text, source="reddit")
    
    analysis = result["analysis"]
    assert analysis.sentiment == "mixed"
    assert "streaming" in analysis.key_topics

def test_confidence_scores():
    analyzer = ReviewAnalyzer()
    text = "Absolutely love the new Netflix original series!"
    result = analyzer.analyze(text, source="reddit")
    
    confidence = result["confidence_scores"]
    assert isinstance(confidence, ConfidenceScores)
    assert 0 <= confidence.sentiment <= 1
    assert 0 <= confidence.topic_accuracy <= 1 