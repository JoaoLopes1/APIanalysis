# Netflix Reddit Sentiment Analysis

This project analyzes sentiment from Reddit posts about Netflix using a FastAPI backend service. It processes Reddit data to extract sentiment, topics, and generates response recommendations.

## Features

- Reddit post sentiment analysis
- Topic extraction specific to Netflix-related content
- Response recommendation generation
- Batch processing of Reddit posts
- Asynchronous processing for better performance
- Detailed logging and error handling

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Create a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```bash
# .env
SECRET_KEY=your-secret-key-here  # Used for JWT token generation
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── auth/               
│   │   └── auth_handler.py  # Authentication utilities
│   ├── models/
│   │   └── review.py       # Pydantic models
│   └── services/
│       └── analyzer.py     # Sentiment analysis logic
├── process_reviews.py       # Script to process Reddit posts
├── requirements.txt
└── README.md
```

## Usage

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. In a separate terminal, process Reddit posts:
```bash
python process_reviews.py <path-to-json-file>
```

The JSON file should have the following structure:
```json
{
  "query": "Netflix",
  "timestamp": "2025-05-29T23:47:43.351747",
  "platforms": ["reddit"],
  "raw_data": {
    "reddit": {
      "posts": [
        {
          "id": "post_id",
          "title": "Post Title",
          "text": "Post Content",
          "score": 100,
          "upvote_ratio": 0.95,
          "num_comments": 50,
          "created_utc": 1234567890,
          "subreddit": "subreddit_name",
          "author": "username",
          "url": "post_url",
          "permalink": "reddit_permalink",
          "platform": "reddit"
        }
      ]
    }
  }
}
```

## Output

The script will generate two types of files:

1. Log file: `review_processing_YYYYMMDD_HHMMSS.log`
2. Results file: `results_<input-filename>_YYYYMMDD_HHMMSS.json`

The results file contains:
- Original query information
- Sentiment analysis for each post
- Topic extraction results
- Response recommendations
- Confidence scores

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

The application includes comprehensive error handling:
- Input validation
- API connection errors
- Processing errors
- Authentication errors

All errors are logged to both console and log files.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)

## Support

For support, please open an issue in the GitHub repository. 