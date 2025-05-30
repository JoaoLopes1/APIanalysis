# Review Analysis API

A FastAPI-based service that analyzes customer reviews using AI models to extract sentiment, topics, and generate response recommendations.

## Features

- Sentiment analysis using DistilBERT
- Topic extraction
- AI-generated response recommendations
- Urgency scoring
- Authentication with JWT tokens
- Rate limiting
- CORS support

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```
SECRET_KEY=your-secret-key-here
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

The API uses Bearer token authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Example Usage

```python
import requests
import json

url = "http://localhost:8000/analyze-review"
headers = {
    "Authorization": "Bearer <your_token>",
    "Content-Type": "application/json"
}
data = {
    "review_id": "rev_8912",
    "text": "App crashes frequently during payment process. Love the design but this makes it unusable.",
    "metadata": {
        "source": "play_store",
        "language": "en"
    }
}

response = requests.post(url, headers=headers, json=data)
print(json.dumps(response.json(), indent=2))
```

## Rate Limiting

The API is limited to 100 requests per minute per API key.

## Error Handling

- 400: Invalid JSON structure
- 401: Invalid or expired token
- 415: Non-JSON payload
- 422: Semantic validation failure
- 429: Rate limit exceeded
- 500: Internal server error

## Production Deployment Notes

1. Replace the default secret key with a secure value
2. Set up proper rate limiting middleware
3. Configure CORS settings for your domains
4. Set up monitoring and logging
5. Consider using a production-grade ASGI server like Gunicorn with Uvicorn workers 