from fastmcp import FastMCP, Context
from typing import Dict, List, Tuple
import re
import requests
from urllib.parse import unquote
import json
import os
from dotenv import load_dotenv
import logging
import argparse

# Load environment variables
load_dotenv()

# Configure logging based on DEBUG setting
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
if DEBUG:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("GitHubChat MCP")

# API Key
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable is required")

# API Key
API_URL = os.getenv('API_URL')
if not API_URL:
    raise ValueError("API_URL environment variable is required")

def get_raw_file_path(url: str) -> Dict[str, List[str] | str]:
    """Convert GitHub URL to raw content URL(s)."""
    logger.info(f"Processing URL: {url}")
    
    # Remove trailing slash if present and strip query parameters and hash fragments
    url = url.rstrip('/').split('?')[0].split('#')[0]
    logger.info(f"Cleaned URL: {url}")
    
    # Extract username and repo
    match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
    if not match:
        logger.warning(f"Failed to extract username and repo from URL: {url}")
        return {"urls": [], "type": "readme"}
    
    username, repo = match.groups()
    logger.info(f"Extracted username: {username}, repo: {repo}")

    # Handle different URL patterns
    if re.match(r'^https?://github\.com/[^/]+/[^/]+$', url):
        # Basic repo URL - try both main and master branches
        urls = [
            f"https://raw.githubusercontent.com/{username}/{repo}/main/README.md",
            f"https://raw.githubusercontent.com/{username}/{repo}/master/README.md",
            f"https://raw.githubusercontent.com/{username}/{repo}/main/readme.md",
            f"https://raw.githubusercontent.com/{username}/{repo}/master/readme.md",
            f"https://raw.githubusercontent.com/{username}/{repo}/main/ReadMe.md",
            f"https://raw.githubusercontent.com/{username}/{repo}/master/ReadMe.md",
            f"https://raw.githubusercontent.com/{username}/{repo}/main/Readme.md",
            f"https://raw.githubusercontent.com/{username}/{repo}/master/Readme.md",
        ]
        logger.info(f"Basic repo URL, generated URLs: {urls}")
        return {
            "urls": urls,
            "type": "readme"
        }

    if '/tree/' in url:
        path = url.split('/tree/')[1]
        path = unquote(path)  # URL decode the path
        logger.info(f"Tree URL, path: {path}")
        
        if '.' in path or path.endswith('LICENSE'):
            # Has file extension or is a license file
            url = f"https://raw.githubusercontent.com/{username}/{repo}/{path}"
            logger.info(f"File URL generated: {url}")
            return {
                "urls": [url],
                "type": "file"
            }
        else:
            # Directory path
            url = f"https://raw.githubusercontent.com/{username}/{repo}/{path}/README.md"
            logger.info(f"Directory URL generated: {url}")
            return {
                "urls": [
                    f"https://raw.githubusercontent.com/{username}/{repo}/{path}/README.md",
                    f"https://raw.githubusercontent.com/{username}/{repo}/{path}/readme.md",
                    f"https://raw.githubusercontent.com/{username}/{repo}/{path}/ReadMe.md",
                    f"https://raw.githubusercontent.com/{username}/{repo}/{path}/Readme.md"
                ],
                "type": "readme"
            }

    if '/blob/' in url:
        path = url.split('/blob/')[1]
        path = unquote(path)  # URL decode the path
        logger.info(f"Blob URL, path: {path}")
        
        if '.' in path or path.endswith('LICENSE'):
            # Has file extension or is a license file
            url = f"https://raw.githubusercontent.com/{username}/{repo}/{path}"
            logger.info(f"File URL generated: {url}")
            return {
                "urls": [url],
                "type": "file"
            }
        else:
            # Directory path
            url = f"https://raw.githubusercontent.com/{username}/{repo}/{path}/README.md"
            logger.info(f"Directory URL generated: {url}")
            return {
                "urls": [
                    f"https://raw.githubusercontent.com/{username}/{repo}/{path}/README.md",
                    f"https://raw.githubusercontent.com/{username}/{repo}/{path}/readme.md",
                    f"https://raw.githubusercontent.com/{username}/{repo}/{path}/ReadMe.md",
                    f"https://raw.githubusercontent.com/{username}/{repo}/{path}/Readme.md"
                ],
                "type": "readme"
            }

    if '/wiki' in url:
        if url == f"https://github.com/{username}/{repo}/wiki":
            # Wiki home
            url = f"https://raw.githubusercontent.com/wiki/{username}/{repo}/Home.md"
            logger.info(f"Wiki home URL generated: {url}")
            return {
                "urls": [url],
                "type": "wikipage"
            }

        wiki_path = url.split('/wiki/')[1] if '/wiki/' in url else ''
        wiki_path = unquote(wiki_path)  # URL decode the path
        logger.info(f"Wiki path: {wiki_path}")
        
        if wiki_path.endswith('.md'):
            # Has .md extension
            url = f"https://raw.githubusercontent.com/wiki/{username}/{repo}/{wiki_path}"
            logger.info(f"Wiki .md URL generated: {url}")
            return {
                "urls": [url],
                "type": "wikipage"
            }
        elif wiki_path:
            # No .md extension
            url = f"https://raw.githubusercontent.com/wiki/{username}/{repo}/{wiki_path}.md"
            logger.info(f"Wiki URL generated: {url}")
            return {
                "urls": [url],
                "type": "wikipage"
            }
        else:
            # Empty wiki path
            url = f"https://raw.githubusercontent.com/wiki/{username}/{repo}/Home.md"
            logger.info(f"Empty wiki path, generated URL: {url}")
            return {
                "urls": [url],
                "type": "wikipage"
            }

    logger.warning(f"No matching URL pattern found for: {url}")
    return {"urls": [], "type": "readme"}

def validate_github_url(url: str) -> Tuple[bool, str]:
    """Validate if the URL is a valid GitHub URL."""
    # Strip query parameters and hash fragments
    clean_url = url.split('?')[0].split('#')[0]
    logger.info(f"Validating URL: {clean_url}")
    
    # Basic GitHub URL validation
    github_url_pattern = r'^https?://github\.com/[\w-]+/[\w-]+(?:\/(?:tree|blob|wiki)(?:\/[^?#]+)?)?$'
    if not re.match(github_url_pattern, clean_url):
        logger.warning(f"Invalid GitHub URL pattern: {clean_url}")
        return False, 'Please enter a valid GitHub repository, file, wiki URL (e.g., https://github.com/username/repo)'
    
    logger.info(f"Valid GitHub URL: {clean_url}")
    return True, ''

async def fetch_raw_content(urls: List[str]) -> str:
    """Fetch raw content from the first successful URL."""
    for url in urls:
        try:
            logger.info(f"Fetching content from: {url}")
            response = requests.get(url)
            logger.info(f"Response status: {response.status_code}")
            
            if response.ok:
                # Raw content is returned as plain text
                content = response.text
                logger.info("Successfully fetched raw content")
                return content
            else:
                logger.error(f"Error fetching from {url}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error fetching from {url}: {e}")
    return ""

@mcp.tool()
async def githubchat_completion(query: str, url: str, ctx: Context) -> str:
    """GitHubChat completion endpoint that matches the HAR file behavior."""
    
    # Validate GitHub URL
    is_valid, error_message = validate_github_url(url)
    if not is_valid:
        return json.dumps({
            "status": 400,
            "code": "error",
            "message": error_message,
            "payload": None
        })
    
    # Get raw file path(s)
    result = get_raw_file_path(url)
    urls = result["urls"]
    logger.info(f"Generated URLs: {urls}")
    
    # Fetch raw content
    document = await fetch_raw_content(urls)
    if not document:
        return json.dumps({
            "status": 404,
            "code": "error",
            "message": "Could not fetch content from any of the URLs",
            "payload": None
        })
    
    # Call the completion endpoint
    try:
        response = requests.post(
            f"{API_URL}/functions/v1/githubchat-completion-mcp",
            headers={
                "apikey": API_KEY, # public key
                "authorization": f"Bearer {API_KEY}", # public key
                "content-type": "application/json",
                "x-client-info": "supabase-js-web/2.49.8"
            },
            json={
                "query": query,
                "document": document,
                "url": url
            }
        )
        
        if response.ok:
            # Return the completion response
            return response.text
        else:
            logger.error(f"Error from completion endpoint: {response.status_code} - {response.text}")
            return json.dumps({
                "status": response.status_code,
                "code": "error",
                "message": f"Error from completion service: {response.text}",
                "payload": None
            })
            
    except Exception as e:
        logger.error(f"Error calling completion endpoint: {e}")
        return json.dumps({
            "status": 500,
            "code": "error",
            "message": f"Error calling completion service: {str(e)}",
            "payload": None
        })

def main():
    """Run the MCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the GitHubChat MCP server')
    parser.add_argument('--port', type=int, default=4651, help='Port to run the server on (default: 4651)')
    args = parser.parse_args()
    
    # Run the server using streamable-http transport
    mcp.run(transport="streamable-http", host="127.0.0.1", port=args.port, path="/githubchat-mcp")

if __name__ == "__main__":
    main() 