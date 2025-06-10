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
from app.models.review import SentimentAnalysisInput, RedditPost, ReviewMetadata

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

    async def process_post(self, session: aiohttp.ClientSession, post_dict: Dict) -> Dict:
        """Process a single Reddit post."""
        try:
            # Convert dictionary to RedditPost model
            post = RedditPost(**post_dict)
            
            # Combine title and text for sentiment analysis
            combined_text = f"{post.title}\n\n{post.text}" if post.text else post.title
            
            # Create metadata
            metadata = ReviewMetadata(
                source="reddit",
                subreddit=post.subreddit,
                score=post.score,
                upvote_ratio=post.upvote_ratio,
                num_comments=post.num_comments,
                created_utc=post.created_utc
            )
            
            review_data = {
                "review_id": post.id,
                "text": combined_text,
                "metadata": metadata.dict()
            }
            
            async with session.post(self.api_url, json=review_data, headers=self.headers) as response:
                result = await response.json()
                if response.status != 200:
                    logger.error(f"Error processing post {post.id}: {result}")
                    return {"review_id": post.id, "error": result}
                return result
        except Exception as e:
            post_id = post_dict.get('id', 'unknown')
            logger.error(f"Exception processing post {post_id}: {str(e)}")
            return {"review_id": post_id, "error": str(e)}

    async def process_batch(self, posts: List[Dict]) -> List[Dict]:
        """Process a batch of Reddit posts concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.process_post(session, post) for post in posts]
            return await asyncio.gather(*tasks)

    def validate_input(self, data: Dict) -> bool:
        """Validate input data structure."""
        try:
            SentimentAnalysisInput(**data)
            return True
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False

    async def process_file(self, file_path: str) -> Dict:
        """Process all posts from a JSON file."""
        try:
            # Load and validate JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not self.validate_input(data):
                raise ValueError("Invalid input data structure")

            # Extract posts from the Reddit data
            posts = data["raw_data"]["reddit"]["posts"]
            
            # Process in batches
            results = []
            for i in range(0, len(posts), self.batch_size):
                batch = posts[i:i + self.batch_size]
                batch_results = await self.process_batch(batch)
                results.extend(batch_results)
                logger.info(f"Processed batch {i//self.batch_size + 1}/{(len(posts) + self.batch_size - 1)//self.batch_size}")

            # Save results
            output_file = f"results_{Path(file_path).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "query": data["query"],
                    "timestamp": data["timestamp"],
                    "platforms": data["platforms"],
                    "results": results
                }, f, indent=2)

            return {
                "total_posts": len(posts),
                "processed_posts": len(results),
                "output_file": output_file
            }

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON file: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description="Process Reddit posts for sentiment analysis")
    parser.add_argument("file", help="JSON file containing Reddit posts")
    parser.add_argument("--batch-size", type=int, default=10, help="Number of posts to process in each batch")
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