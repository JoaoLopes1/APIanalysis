import requests
from app.auth.auth_handler import create_token

# Create a test token
token = create_token({"test": True})

# API endpoint
url = "http://localhost:8000/analyze-review"

# Request headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Example review data
data = {
    "review_id": "rev_test_001",
    "text": "The app is great but crashes sometimes during payment. Love the design though!",
    "metadata": {
        "source": "app_store",
        "language": "en"
    }
}

# Make the request
response = requests.post(url, json=data, headers=headers)

# Print the response
print("Status Code:", response.status_code)
print("Response:", response.json())