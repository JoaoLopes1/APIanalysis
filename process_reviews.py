import json
import requests
import argparse
from pathlib import Path
from typing import List, Dict
from app.auth.auth_handler import create_token
import asyncio
import aiohttp
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'review_processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ReviewProcessor:
    def __init__(self, api_url: str, batch_size: int = 10, max_concurrent: int = 5):
        self.api_url = api_url
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.token = create_token({"test": True})
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def process_review(self, session: aiohttp.ClientSession, review: Dict) -> Dict:
        """Process a single review."""
        try:
            async with session.post(self.api_url, json=review, headers=self.headers) as response:
                result = await response.json()
                if response.status != 200:
                    logger.error(f"Error processing review {review.get('review_id')}: {result}")
                    return {"review_id": review.get("review_id"), "error": result}
                return result
        except Exception as e:
            logger.error(f"Exception processing review {review.get('review_id')}: {str(e)}")
            return {"review_id": review.get("review_id"), "error": str(e)}

    async def process_batch(self, reviews: List[Dict]) -> List[Dict]:
        """Process a batch of reviews concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.process_review(session, review) for review in reviews]
            return await asyncio.gather(*tasks)

    def validate_review(self, review: Dict) -> bool:
        """Validate review data structure."""
        required_fields = {"review_id", "text"}
        return all(field in review for field in required_fields)

    async def process_file(self, file_path: str) -> Dict:
        """Process all reviews from a JSON file."""
        try:
            # Load and validate JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                reviews = json.load(f)

            if not isinstance(reviews, list):
                reviews = [reviews]

            # Validate reviews
            valid_reviews = []
            for review in reviews:
                if self.validate_review(review):
                    valid_reviews.append(review)
                else:
                    logger.warning(f"Invalid review structure: {review}")

            # Process in batches
            results = []
            for i in range(0, len(valid_reviews), self.batch_size):
                batch = valid_reviews[i:i + self.batch_size]
                batch_results = await self.process_batch(batch)
                results.extend(batch_results)
                logger.info(f"Processed batch {i//self.batch_size + 1}/{(len(valid_reviews) + self.batch_size - 1)//self.batch_size}")

            # Save results
            output_file = f"results_{Path(file_path).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)

            return {
                "total_reviews": len(reviews),
                "processed_reviews": len(results),
                "output_file": output_file
            }

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON file: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description="Process reviews from JSON files")
    parser.add_argument("file", help="JSON file containing reviews")
    parser.add_argument("--batch-size", type=int, default=10, help="Number of reviews to process in each batch")
    parser.add_argument("--max-concurrent", type=int, default=5, help="Maximum number of concurrent requests")
    parser.add_argument("--api-url", default="http://localhost:8000/analyze-review", help="API endpoint URL")
    
    args = parser.parse_args()
    
    processor = ReviewProcessor(
        api_url=args.api_url,
        batch_size=args.batch_size,
        max_concurrent=args.max_concurrent
    )
    
    try:
        result = asyncio.run(processor.process_file(args.file))
        logger.info(f"Processing completed: {result}")
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 