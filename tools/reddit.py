from core.tools import BaseTool
import requests
import json

class RedditTool(BaseTool):
    def __init__(self):
        super().__init__("Reddit", "Fetches news, posts, and images from Reddit subreddits. Input: JSON with 'subreddit' (e.g., 'news', 'pics', 'technology') and optional 'limit'.")

    def execute(self, subreddit=None, limit=5, payload=None):
        # Robust payload parsing
        if payload:
            if isinstance(payload, dict):
                subreddit = subreddit or payload.get('subreddit')
                limit = limit or payload.get('limit', 5)
            elif isinstance(payload, str):
                try:
                    p = json.loads(payload)
                    subreddit = subreddit or p.get('subreddit')
                    limit = limit or p.get('limit', 5)
                except:
                    subreddit = subreddit or payload # Treat as raw subreddit name
        
        if not subreddit:
            return "Error: 'subreddit' parameter is required. Examples: 'news', 'pics'."

        # Reddit's .json API (no key needed for public data, but requires User-Agent)
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        headers = {"User-Agent": "HorizonDesk/0.1 (Experimental App)"}

        try:
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                results = []
                for post in posts:
                    p = post.get('data', {})
                    title = p.get('title')
                    permalink = f"https://www.reddit.com{p.get('permalink')}"
                    image_url = p.get('url')
                    
                    # Detect if it's a direct image link
                    is_image = any(image_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])
                    # Handle imgur links that might not have extension but are images
                    if 'imgur.com' in image_url and not is_image:
                        # Simple heuristic for imgur
                        if '/a/' not in image_url and '/gallery/' not in image_url:
                            image_url += '.jpg'
                            is_image = True

                    results.append({
                        "title": title,
                        "link": permalink,
                        "image_url": image_url if is_image else None,
                        "ups": p.get('ups'),
                        "num_comments": p.get('num_comments')
                    })
                
                if not results:
                    return f"No posts found in r/{subreddit}."
                
                return json.dumps(results, indent=2)
            elif response.status_code == 404:
                return f"Error: Subreddit r/{subreddit} not found."
            elif response.status_code == 403:
                return f"Error: Access to r/{subreddit} is private or blocked."
            else:
                return f"Error: Reddit returned HTTP {response.status_code}"
        except Exception as e:
            return f"Error connecting to Reddit: {str(e)}"

def get_reddit_instruction():
    return """
[REDDIT CONTENT PROTOCOL]
When searching for viral news, niche discussions, or images from Reddit:
1. Use the 'Reddit' tool with the relevant subreddit name.
2. If the user asks for "news", 'news' or 'worldnews' are good choices. For images, try 'pics' or 'wallpapers'.
3. The tool returns JSON. You should summarize the titles and links for the user.
4. IMPORTANT: If there is an 'image_url', include it in your response using Markdown syntax: ![Image](url). The UI will render these automatically.
"""
