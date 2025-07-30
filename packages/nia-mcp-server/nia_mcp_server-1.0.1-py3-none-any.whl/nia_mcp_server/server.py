"""
NIA MCP Proxy Server - Lightweight server that communicates with NIA API
"""
import os
import logging
import json
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from urllib.parse import urlparse

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Resource
from .api_client import NIAApiClient, APIError
from dotenv import load_dotenv

# Load .env from parent directory (nia-app/.env)
from pathlib import Path
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

# TOOL SELECTION GUIDE FOR AI ASSISTANTS:
# 
# Use 'nia_web_search' for:
#   - "Find RAG libraries" → Simple search
#   - "What's trending in Rust?" → Quick discovery
#   - "Show me repos like LangChain" → Similarity search
#
# Use 'nia_deep_research_agent' for:
#   - "Compare RAG vs GraphRAG approaches" → Comparative analysis
#   - "What are the best vector databases for production?" → Evaluation needed
#   - "Analyze the pros and cons of different LLM frameworks" → Structured analysis
#
# The AI should assess query complexity and choose accordingly.

# Create the MCP server
mcp = FastMCP("nia-knowledge-agent")

# Global API client instance
api_client: Optional[NIAApiClient] = None

def get_api_key() -> str:
    """Get API key from environment."""
    api_key = os.getenv("NIA_API_KEY")
    if not api_key:
        raise ValueError(
            "NIA_API_KEY environment variable not set. "
            "Get your API key at https://trynia.ai/api-keys"
        )
    return api_key

async def ensure_api_client() -> NIAApiClient:
    """Ensure API client is initialized."""
    global api_client
    if not api_client:
        api_key = get_api_key()
        api_client = NIAApiClient(api_key)
        # Validate the API key
        if not await api_client.validate_api_key():
            # The validation error is already logged, just raise a generic error
            raise ValueError("Failed to validate API key. Check logs for details.")
    return api_client

# Tools

@mcp.tool()
async def index_repository(
    repo_url: str,
    branch: Optional[str] = None
) -> List[TextContent]:
    """
    Index a GitHub repository for intelligent code search.
    
    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/owner/repo)
        branch: Branch to index (optional, defaults to main branch)
        
    Returns:
        Status of the indexing operation
    """
    try:
        client = await ensure_api_client()
        
        # Start indexing
        logger.info(f"Starting to index repository: {repo_url}")
        result = await client.index_repository(repo_url, branch)
        
        repository = result.get("repository", repo_url)
        status = result.get("status", "unknown")
        
        if status == "completed":
            return [TextContent(
                type="text",
                text=f"✅ Repository already indexed: {repository}\n"
                     f"Branch: {result.get('branch', 'main')}\n"
                     f"You can now search this codebase!"
            )]
        else:
            # Wait for indexing to complete
            return [TextContent(
                type="text",
                text=f"⏳ Indexing started for: {repository}\n"
                     f"Branch: {branch or 'default'}\n"
                     f"Status: {status}\n\n"
                     f"Use `check_repository_status` to monitor progress."
            )]
            
    except APIError as e:
        logger.error(f"API Error indexing repository: {e} (status_code={e.status_code}, detail={e.detail})")
        if e.status_code == 403 or "free tier limit" in str(e).lower() or "free api requests" in str(e).lower():
            if e.detail and "25 free API requests" in e.detail:
                return [TextContent(
                    type="text", 
                    text=f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited API access."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ {str(e)}\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for unlimited access."
                )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error indexing repository: {e}")
        error_msg = str(e)
        if "free api requests" in error_msg.lower() or "lifetime limit" in error_msg.lower():
            return [TextContent(
                type="text",
                text=f"❌ {error_msg}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited API access."
            )]
        return [TextContent(
            type="text",
            text=f"❌ Error indexing repository: {error_msg}"
        )]

@mcp.tool()
async def search_codebase(
    query: str,
    repositories: Optional[List[str]] = None,
    include_sources: bool = True
) -> List[TextContent]:
    """
    Search indexed repositories using natural language.
    
    Args:
        query: Natural language search query
        repositories: List of repositories to search (owner/repo format). If not specified, searches all indexed repos.
        include_sources: Whether to include source code in results
        
    Returns:
        Search results with relevant code snippets and explanations
    """
    try:
        client = await ensure_api_client()
        
        # Get all indexed repositories if not specified
        if not repositories:
            all_repos = await client.list_repositories()
            repositories = [repo["repository"] for repo in all_repos if repo.get("status") == "completed"]
            if not repositories:
                return [TextContent(
                    type="text",
                    text="❌ No indexed repositories found. Use `index_repository` to index a codebase first."
                )]
        
        # Build messages for the query
        messages = [
            {"role": "user", "content": query}
        ]
        
        logger.info(f"Searching {len(repositories)} repositories")
        
        # Stream the response using unified query
        response_parts = []
        sources_parts = []
        
        async for chunk in client.query_unified(
            messages=messages,
            repositories=repositories,
            data_sources=[],  # No documentation sources
            search_mode="repositories",  # Use repositories mode to exclude external sources
            stream=True,
            include_sources=include_sources
        ):
            try:
                data = json.loads(chunk)
                
                if "content" in data and data["content"] and data["content"] != "[DONE]":
                    response_parts.append(data["content"])
                
                if "sources" in data and data["sources"]:
                    sources_parts.extend(data["sources"])
                    
            except json.JSONDecodeError:
                continue
        
        # Format the response
        response_text = "".join(response_parts)
        
        if sources_parts and include_sources:
            response_text += "\n\n## Sources\n\n"
            for i, source in enumerate(sources_parts[:5], 1):  # Limit to 5 sources
                response_text += f"### Source {i}\n"
                if "repository" in source:
                    response_text += f"**Repository:** {source['repository']}\n"
                if "file" in source:
                    response_text += f"**File:** `{source['file']}`\n"
                if "preview" in source:
                    response_text += f"```\n{source['preview']}\n```\n\n"
        
        return [TextContent(type="text", text=response_text)]
        
    except APIError as e:
        logger.error(f"API Error searching codebase: {e} (status_code={e.status_code}, detail={e.detail})")
        if e.status_code == 403 or "free tier limit" in str(e).lower() or "free api requests" in str(e).lower():
            if e.detail and "25 free API requests" in e.detail:
                return [TextContent(
                    type="text", 
                    text=f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited API access."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ {str(e)}\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for unlimited access."
                )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error searching codebase: {e}")
        error_msg = str(e)
        if "free api requests" in error_msg.lower() or "lifetime limit" in error_msg.lower():
            return [TextContent(
                type="text",
                text=f"❌ {error_msg}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited API access."
            )]
        return [TextContent(
            type="text",
            text=f"❌ Error searching codebase: {error_msg}"
        )]

@mcp.tool()
async def search_documentation(
    query: str,
    sources: Optional[List[str]] = None,
    include_sources: bool = True
) -> List[TextContent]:
    """
    Search indexed documentation using natural language.
    
    Args:
        query: Natural language search query
        sources: List of documentation source IDs to search. If not specified, searches all indexed documentation.
        include_sources: Whether to include source references in results
        
    Returns:
        Search results with relevant documentation excerpts
    """
    try:
        client = await ensure_api_client()
        
        # Get all indexed documentation sources if not specified
        if not sources:
            all_sources = await client.list_data_sources()
            sources = [source["id"] for source in all_sources if source.get("status") == "completed"]
            if not sources:
                return [TextContent(
                    type="text",
                    text="❌ No indexed documentation found. Use `index_documentation` to index documentation first."
                )]
        
        # Build messages for the query
        messages = [
            {"role": "user", "content": query}
        ]
        
        logger.info(f"Searching {len(sources)} documentation sources")
        
        # Stream the response using unified query
        response_parts = []
        sources_parts = []
        
        async for chunk in client.query_unified(
            messages=messages,
            repositories=[],  # No repositories
            data_sources=sources,
            search_mode="unified",  # Use unified for full answers with documentation
            stream=True,
            include_sources=include_sources
        ):
            try:
                data = json.loads(chunk)
                
                if "content" in data and data["content"] and data["content"] != "[DONE]":
                    response_parts.append(data["content"])
                
                if "sources" in data and data["sources"]:
                    sources_parts.extend(data["sources"])
                    
            except json.JSONDecodeError:
                continue
        
        # Format the response
        response_text = "".join(response_parts)
        
        if sources_parts and include_sources:
            response_text += "\n\n## Sources\n\n"
            for i, source in enumerate(sources_parts[:5], 1):  # Limit to 5 sources
                response_text += f"### Source {i}\n"
                if "url" in source:
                    response_text += f"**URL:** {source['url']}\n"
                elif "file" in source:
                    response_text += f"**Page:** {source['file']}\n"
                if "preview" in source:
                    response_text += f"```\n{source['preview']}\n```\n\n"
        
        return [TextContent(type="text", text=response_text)]
        
    except APIError as e:
        logger.error(f"API Error searching documentation: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 25 API requests. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error searching documentation: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error searching documentation: {str(e)}"
        )]

@mcp.tool()
async def list_repositories() -> List[TextContent]:
    """
    List all indexed repositories.
    
    Returns:
        List of indexed repositories with their status
    """
    try:
        client = await ensure_api_client()
        repositories = await client.list_repositories()
        
        if not repositories:
            return [TextContent(
                type="text",
                text="No indexed repositories found.\n\n"
                     "Get started by indexing a repository:\n"
                     "Use `index_repository` with a GitHub URL."
            )]
        
        # Format repository list
        lines = ["# Indexed Repositories\n"]
        
        for repo in repositories:
            status_icon = "✅" if repo.get("status") == "completed" else "⏳"
            lines.append(f"\n## {status_icon} {repo['repository']}")
            lines.append(f"- **Branch:** {repo.get('branch', 'main')}")
            lines.append(f"- **Status:** {repo.get('status', 'unknown')}")
            if repo.get("indexed_at"):
                lines.append(f"- **Indexed:** {repo['indexed_at']}")
            if repo.get("error"):
                lines.append(f"- **Error:** {repo['error']}")
        
        return [TextContent(type="text", text="\n".join(lines))]
        
    except APIError as e:
        logger.error(f"API Error listing repositories: {e} (status_code={e.status_code}, detail={e.detail})")
        # Check for free tier limit errors
        if e.status_code == 403 or "free tier limit" in str(e).lower() or "free api requests" in str(e).lower():
            # Extract the specific limit message
            if e.detail and "25 free API requests" in e.detail:
                return [TextContent(
                    type="text", 
                    text=f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited API access."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ {str(e)}\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for unlimited access."
                )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error listing repositories (type={type(e).__name__}): {e}")
        # Check if this looks like an API limit error that wasn't caught properly
        error_msg = str(e)
        if "free api requests" in error_msg.lower() or "lifetime limit" in error_msg.lower():
            return [TextContent(
                type="text",
                text=f"❌ {error_msg}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited API access."
            )]
        return [TextContent(
            type="text",
            text=f"❌ Error listing repositories: {error_msg}"
        )]

@mcp.tool()
async def check_repository_status(repository: str) -> List[TextContent]:
    """
    Check the indexing status of a repository.
    
    Args:
        repository: Repository in owner/repo format
        
    Returns:
        Current status of the repository
    """
    try:
        client = await ensure_api_client()
        status = await client.get_repository_status(repository)
        
        if not status:
            return [TextContent(
                type="text",
                text=f"❌ Repository '{repository}' not found."
            )]
        
        # Format status
        status_icon = {
            "completed": "✅",
            "indexing": "⏳",
            "failed": "❌",
            "pending": "🔄"
        }.get(status["status"], "❓")
        
        lines = [
            f"# Repository Status: {repository}\n",
            f"{status_icon} **Status:** {status['status']}",
            f"**Branch:** {status.get('branch', 'main')}"
        ]
        
        if status.get("progress"):
            progress = status["progress"]
            if isinstance(progress, dict):
                lines.append(f"**Progress:** {progress.get('percentage', 0)}%")
                if progress.get("stage"):
                    lines.append(f"**Stage:** {progress['stage']}")
        
        if status.get("indexed_at"):
            lines.append(f"**Indexed:** {status['indexed_at']}")
        
        if status.get("error"):
            lines.append(f"**Error:** {status['error']}")
        
        return [TextContent(type="text", text="\n".join(lines))]
        
    except APIError as e:
        logger.error(f"API Error checking repository status: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 25 API requests. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error checking repository status: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error checking repository status: {str(e)}"
        )]

@mcp.tool()
async def index_documentation(
    url: str,
    url_patterns: Optional[List[str]] = None,
    max_age: Optional[int] = None,
    only_main_content: Optional[bool] = True
) -> List[TextContent]:
    """
    Index documentation or website for intelligent search.
    
    Args:
        url: URL of the documentation site to index
        url_patterns: Optional list of URL patterns to include in crawling (e.g., ["/docs/*", "/guide/*"])
        max_age: Maximum age of cached content in seconds (for fast scraping mode)
        only_main_content: Extract only main content (removes navigation, ads, etc.)
        
    Returns:
        Status of the indexing operation
    """
    try:
        client = await ensure_api_client()
        
        # Create and start indexing
        logger.info(f"Starting to index documentation: {url}")
        result = await client.create_data_source(
            url=url, 
            url_patterns=url_patterns,
            max_age=max_age,
            only_main_content=only_main_content
        )
        
        source_id = result.get("id")
        status = result.get("status", "unknown")
        
        if status == "completed":
            return [TextContent(
                type="text",
                text=f"✅ Documentation already indexed: {url}\n"
                     f"Source ID: {source_id}\n"
                     f"You can now search this documentation!"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"⏳ Documentation indexing started: {url}\n"
                     f"Source ID: {source_id}\n"
                     f"Status: {status}\n\n"
                     f"Use `check_documentation_status` to monitor progress."
            )]
            
    except APIError as e:
        logger.error(f"API Error indexing documentation: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 25 API requests. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error indexing documentation: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error indexing documentation: {str(e)}"
        )]

@mcp.tool()
async def list_documentation() -> List[TextContent]:
    """
    List all indexed documentation sources.
    
    Returns:
        List of indexed documentation with their status
    """
    try:
        client = await ensure_api_client()
        sources = await client.list_data_sources()
        
        if not sources:
            return [TextContent(
                type="text",
                text="No indexed documentation found.\n\n"
                     "Get started by indexing documentation:\n"
                     "Use `index_documentation` with a URL."
            )]
        
        # Format source list
        lines = ["# Indexed Documentation\n"]
        
        for source in sources:
            status_icon = "✅" if source.get("status") == "completed" else "⏳"
            lines.append(f"\n## {status_icon} {source.get('url', 'Unknown URL')}")
            lines.append(f"- **ID:** {source['id']}")
            lines.append(f"- **Status:** {source.get('status', 'unknown')}")
            lines.append(f"- **Type:** {source.get('source_type', 'web')}")
            if source.get("page_count", 0) > 0:
                lines.append(f"- **Pages:** {source['page_count']}")
            if source.get("created_at"):
                lines.append(f"- **Created:** {source['created_at']}")
        
        return [TextContent(type="text", text="\n".join(lines))]
        
    except APIError as e:
        logger.error(f"API Error listing documentation: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 25 API requests. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error listing documentation: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error listing documentation: {str(e)}"
        )]

@mcp.tool()
async def check_documentation_status(source_id: str) -> List[TextContent]:
    """
    Check the indexing status of a documentation source.
    
    Args:
        source_id: Documentation source ID
        
    Returns:
        Current status of the documentation source
    """
    try:
        client = await ensure_api_client()
        status = await client.get_data_source_status(source_id)
        
        if not status:
            return [TextContent(
                type="text",
                text=f"❌ Documentation source '{source_id}' not found."
            )]
        
        # Format status
        status_icon = {
            "completed": "✅",
            "processing": "⏳",
            "failed": "❌",
            "pending": "🔄"
        }.get(status["status"], "❓")
        
        lines = [
            f"# Documentation Status: {status.get('url', 'Unknown URL')}\n",
            f"{status_icon} **Status:** {status['status']}",
            f"**Source ID:** {source_id}"
        ]
        
        if status.get("page_count", 0) > 0:
            lines.append(f"**Pages Indexed:** {status['page_count']}")
        
        if status.get("details"):
            details = status["details"]
            if details.get("progress"):
                lines.append(f"**Progress:** {details['progress']}%")
            if details.get("stage"):
                lines.append(f"**Stage:** {details['stage']}")
        
        if status.get("created_at"):
            lines.append(f"**Created:** {status['created_at']}")
        
        if status.get("error"):
            lines.append(f"**Error:** {status['error']}")
        
        return [TextContent(type="text", text="\n".join(lines))]
        
    except APIError as e:
        logger.error(f"API Error checking documentation status: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 25 API requests. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error checking documentation status: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error checking documentation status: {str(e)}"
        )]

@mcp.tool()
async def delete_documentation(source_id: str) -> List[TextContent]:
    """
    Delete an indexed documentation source.
    
    Args:
        source_id: Documentation source ID to delete
        
    Returns:
        Confirmation of deletion
    """
    try:
        client = await ensure_api_client()
        success = await client.delete_data_source(source_id)
        
        if success:
            return [TextContent(
                type="text",
                text=f"✅ Successfully deleted documentation source: {source_id}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"❌ Failed to delete documentation source: {source_id}"
            )]
            
    except APIError as e:
        logger.error(f"API Error deleting documentation: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 25 API requests. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error deleting documentation: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error deleting documentation: {str(e)}"
        )]

@mcp.tool()
async def delete_repository(repository: str) -> List[TextContent]:
    """
    Delete an indexed repository.
    
    Args:
        repository: Repository in owner/repo format
        
    Returns:
        Confirmation of deletion
    """
    try:
        client = await ensure_api_client()
        success = await client.delete_repository(repository)
        
        if success:
            return [TextContent(
                type="text",
                text=f"✅ Successfully deleted repository: {repository}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"❌ Failed to delete repository: {repository}"
            )]
            
    except APIError as e:
        logger.error(f"API Error deleting repository: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 25 API requests. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error deleting repository: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error deleting repository: {str(e)}"
        )]

@mcp.tool()
async def nia_web_search(
    query: str,
    num_results: int = 5,
    category: Optional[str] = None,
    days_back: Optional[int] = None,
    find_similar_to: Optional[str] = None
) -> List[TextContent]:
    """
    Search repositories, documentation, and other content using AI-powered search.
    Returns results formatted to guide next actions.
    
    USE THIS TOOL WHEN:
    - Finding specific repos/docs/content ("find X library", "trending Y frameworks")
    - Looking for examples or implementations
    - Searching for what's available on a topic
    - Simple, direct searches that need quick results
    - Finding similar content to a known URL
    
    DON'T USE THIS FOR:
    - Comparative analysis (use nia_deep_research_agent instead)
    - Complex multi-faceted questions (use nia_deep_research_agent instead)
    - Questions requiring synthesis of multiple sources (use nia_deep_research_agent instead)
    
    Args:
        query: Natural language search query (e.g., "best RAG implementations", "trending rust web frameworks")
        num_results: Number of results to return (default: 5, max: 10)
        category: Filter by category: "github", "company", "research paper", "news", "tweet", "pdf"
        days_back: Only show results from the last N days (for trending content)
        find_similar_to: URL to find similar content to
        
    Returns:
        Search results with actionable next steps
    """
    try:
        # Check for API key
        api_key = os.getenv("EXA_API_KEY")
        if not api_key:
            return [TextContent(
                type="text",
                text="❌ NIA Web Search unavailable.\n\n"
                     "This feature requires additional configuration. "
                     "Please contact support for access to advanced search features."
            )]
        
        # Import client
        try:
            from exa_py import Exa
        except ImportError:
            return [TextContent(
                type="text",
                text="❌ NIA Web Search unavailable. Please update the NIA MCP server."
            )]
        
        # Initialize client
        client = Exa(api_key)
        
        # Limit results to reasonable number
        num_results = min(num_results, 10)
        
        logger.info(f"Searching content for query: {query}")
        
        # Build search parameters
        search_params = {
            "num_results": num_results * 2,  # Get more to filter
            "type": "auto",  # Automatically choose best search type
            "text": True,
            "highlights": True
        }
        
        # Add category filter if specified
        if category:
            # Map user-friendly categories to Exa categories
            category_map = {
                "github": "github",
                "company": "company", 
                "research": "research paper",
                "news": "news",
                "tweet": "tweet",
                "pdf": "pdf",
                "blog": "personal site"
            }
            if category.lower() in category_map:
                search_params["category"] = category_map[category.lower()]
        
        # Add date filter for trending content
        if days_back:
            from datetime import datetime, timedelta
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            search_params["start_published_date"] = start_date
        
        # Use similarity search if URL provided
        if find_similar_to:
            results = client.find_similar_and_contents(
                find_similar_to,
                **search_params
            )
        else:
            results = client.search_and_contents(
                query,
                **search_params
            )
        
        # Separate results by type
        github_repos = []
        documentation = []
        other_content = []
        
        for result in results.results:
            url = result.url
            
            # Categorize based on URL patterns
            if "github.com" in url and "/tree/" not in url and "/blob/" not in url:
                # It's a GitHub repo (not a specific file)
                # Extract owner/repo from URL
                try:
                    parsed = urlparse(url)
                    # Ensure we have a valid GitHub URL
                    if parsed.hostname == "github.com":
                        # Remove leading/trailing slashes and split the path
                        path_parts = parsed.path.strip("/").split("/")
                        # Verify we have at least owner and repo in the path
                        if len(path_parts) >= 2 and path_parts[0] and path_parts[1]:
                            # Extract only the owner and repo, ignoring any additional path components
                            owner_repo = f"{path_parts[0]}/{path_parts[1]}"
                            github_repos.append({
                                "url": url,
                                "owner_repo": owner_repo,
                                "title": result.title or owner_repo,
                                "summary": result.text[:200] if result.text else "",
                                "highlights": result.highlights[:2] if result.highlights else [],
                                "published_date": getattr(result, 'published_date', None)
                            })
                except:
                    pass
            elif any(doc_pattern in url for doc_pattern in ["docs.", "documentation", ".readthedocs.", "/docs/"]):
                # It's documentation
                documentation.append({
                    "url": url,
                    "title": result.title or "Documentation",
                    "summary": result.text[:200] if result.text else "",
                    "highlights": result.highlights[:2] if result.highlights else []
                })
            else:
                # Other content
                other_content.append({
                    "url": url,
                    "title": result.title or "Content",
                    "summary": result.text[:200] if result.text else ""
                })
        
        # Format response to naturally guide next actions
        response = f"## 🔍 NIA Web Search Results for: \"{query}\"\n\n"
        
        if days_back:
            response += f"*Showing results from the last {days_back} days*\n\n"
        
        if find_similar_to:
            response += f"*Finding content similar to: {find_similar_to}*\n\n"
        
        # GitHub Repositories Section
        if github_repos:
            response += f"### 📦 GitHub Repositories ({len(github_repos)} found)\n\n"
            
            for i, repo in enumerate(github_repos[:num_results], 1):
                response += f"**{i}. {repo['title']}**\n"
                response += f"   📍 `{repo['url']}`\n"
                if repo.get('published_date'):
                    response += f"   📅 Updated: {repo['published_date']}\n"
                if repo['summary']:
                    response += f"   📝 {repo['summary']}...\n"
                if repo['highlights']:
                    response += f"   ✨ Key features: {', '.join(repo['highlights'])}\n"
                response += "\n"
            
            # Be more aggressive based on query specificity
            if len(github_repos) == 1 or any(specific_word in query.lower() for specific_word in ["specific", "exact", "particular", "find me", "looking for"]):
                response += "**🚀 RECOMMENDED ACTION - Index this repository with NIA:**\n"
                response += f"```\nIndex {github_repos[0]['owner_repo']}\n```\n"
                response += "✨ This will enable AI-powered code search, understanding, and analysis!\n\n"
            else:
                response += "**🚀 Make these repositories searchable with NIA's AI:**\n"
                response += f"- **Quick start:** Say \"Index {github_repos[0]['owner_repo']}\"\n"
                response += "- **Index multiple:** Say \"Index all repositories\"\n"
                response += "- **Benefits:** AI-powered code search, architecture understanding, implementation details\n\n"
        
        # Documentation Section
        if documentation:
            response += f"### 📚 Documentation ({len(documentation)} found)\n\n"
            
            for i, doc in enumerate(documentation[:num_results], 1):
                response += f"**{i}. {doc['title']}**\n"
                response += f"   📍 `{doc['url']}`\n"
                if doc['summary']:
                    response += f"   📝 {doc['summary']}...\n"
                if doc.get('highlights'):
                    response += f"   ✨ Key topics: {', '.join(doc['highlights'])}\n"
                response += "\n"
            
            # Be more aggressive for documentation too
            if len(documentation) == 1 or any(specific_word in query.lower() for specific_word in ["docs", "documentation", "guide", "tutorial", "reference"]):
                response += "**📖 RECOMMENDED ACTION - Index this documentation with NIA:**\n"
                response += f"```\nIndex documentation {documentation[0]['url']}\n```\n"
                response += "✨ NIA will make this fully searchable with AI-powered Q&A!\n\n"
            else:
                response += "**📖 Make this documentation AI-searchable with NIA:**\n"
                response += f"- **Quick start:** Say \"Index documentation {documentation[0]['url']}\"\n"
                response += "- **Index all:** Say \"Index all documentation\"\n"
                response += "- **Benefits:** Instant answers, smart search, code examples extraction\n\n"
        
        # Other Content Section
        if other_content and not github_repos and not documentation:
            response += f"### 🌐 Other Content ({len(other_content)} found)\n\n"
            
            for i, content in enumerate(other_content[:num_results], 1):
                response += f"**{i}. {content['title']}**\n"
                response += f"   📍 `{content['url']}`\n"
                if content['summary']:
                    response += f"   📝 {content['summary']}...\n"
                response += "\n"
        
        # No results found
        if not github_repos and not documentation and not other_content:
            response = f"No results found for '{query}'. Try:\n"
            response += "- Using different keywords\n"
            response += "- Being more specific (e.g., 'Python RAG implementation')\n"
            response += "- Including technology names (e.g., 'LangChain', 'TypeScript')\n"
        
        # Add prominent call-to-action if we found indexable content
        if github_repos or documentation:
            response += "\n## 🎯 **Ready to unlock NIA's AI capabilities?**\n"
            response += "The repositories and documentation above can be indexed for:\n"
            response += "- 🤖 AI-powered code understanding and search\n"
            response += "- 💡 Instant answers to technical questions\n"
            response += "- 🔍 Deep architectural insights\n"
            response += "- 📚 Smart documentation Q&A\n\n"
            response += "**Just copy and paste the index commands above!**\n"
        
        # Add search metadata
        response += f"\n---\n"
        response += f"*Searched {len(results.results)} sources using NIA Web Search*"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Error in NIA web search: {str(e)}")
        return [TextContent(
            type="text",
            text=f"❌ NIA Web Search error: {str(e)}\n\n"
                 "This might be due to:\n"
                 "- Network connectivity issues\n"
                 "- Service temporarily unavailable"
        )]

@mcp.tool()
async def nia_deep_research_agent(
    query: str,
    output_format: Optional[str] = None
) -> List[TextContent]:
    """
    Perform deep, multi-step research on a topic using advanced AI research capabilities.
    Best for complex questions that need comprehensive analysis.
    
    USE THIS TOOL WHEN:
    - Comparing multiple options ("compare X vs Y vs Z")
    - Analyzing pros and cons
    - Questions with "best", "top", "which is better"
    - Needing structured analysis or synthesis
    - Complex questions requiring multiple sources
    - Questions about trends, patterns, or developments
    - Requests for comprehensive overviews
    
    DON'T USE THIS FOR:
    - Simple lookups (use nia_web_search instead)
    - Finding a specific known item (use nia_web_search instead)
    - Quick searches for repos/docs (use nia_web_search instead)
    
    COMPLEXITY INDICATORS:
    - Words like: compare, analyze, evaluate, pros/cons, trade-offs
    - Multiple criteria mentioned
    - Asking for recommendations based on context
    - Needing structured output (tables, lists, comparisons)
    
    Args:
        query: Research question (e.g., "Compare top 3 RAG frameworks with pros/cons")
        output_format: Optional structure hint (e.g., "comparison table", "pros and cons list")
        
    Returns:
        Comprehensive research results with citations
    """
    try:
        # Check for API key
        api_key = os.getenv("EXA_API_KEY")
        if not api_key:
            return [TextContent(
                type="text",
                text="❌ Deep research unavailable. This advanced feature requires additional configuration."
            )]
        
        # Import client
        try:
            from exa_py import Exa
            import json
        except ImportError:
            return [TextContent(
                type="text",
                text="❌ Research service unavailable. Please update the NIA MCP server."
            )]
        
        # Initialize client
        client = Exa(api_key)
        
        logger.info(f"Starting deep research for: {query}")
        
        # Create a research task
        try:
            # Let the AI infer the schema based on the query
            task = client.research.create_task(
                instructions=query,
                infer_schema=True,
                model="exa-research-pro"  # Use the pro model
            )
            
            logger.info(f"Research task created: {task.id}")
            
            # Poll for completion (max 2 minutes)
            result = client.research.poll_task(
                task.id,
                poll_interval=3,
                max_wait_time=120
            )
            
            if result.status == "failed":
                return [TextContent(
                    type="text",
                    text=f"❌ Research failed. Please try rephrasing your question."
                )]
            
            # Format the research results
            response = f"## 🔬 NIA Deep Research Agent Results\n\n"
            response += f"**Query:** {query}\n\n"
            
            if result.data:
                response += "### 📊 Research Findings:\n\n"
                
                # Pretty print the JSON data
                formatted_data = json.dumps(result.data, indent=2)
                response += f"```json\n{formatted_data}\n```\n\n"
                
                # Add citations if available
                if result.citations:
                    response += "### 📚 Sources & Citations:\n\n"
                    citation_num = 1
                    for field, citations in result.citations.items():
                        if citations:
                            response += f"**{field}:**\n"
                            for citation in citations[:3]:  # Limit to 3 citations per field
                                response += f"{citation_num}. [{citation.get('title', 'Source')}]({citation.get('url', '#')})\n"
                                if citation.get('snippet'):
                                    response += f"   > {citation['snippet'][:150]}...\n"
                                citation_num += 1
                            response += "\n"
                
                response += "### 💡 RECOMMENDED NEXT ACTIONS WITH NIA:\n\n"
                
                # Extract potential repos and docs from the research data
                repos_found = []
                docs_found = []
                
                # Helper function to extract URLs from nested data structures
                def extract_urls_from_data(data, urls_list=None):
                    if urls_list is None:
                        urls_list = []
                    
                    if isinstance(data, dict):
                        for value in data.values():
                            extract_urls_from_data(value, urls_list)
                    elif isinstance(data, list):
                        for item in data:
                            extract_urls_from_data(item, urls_list)
                    elif isinstance(data, str):
                        # Check if this string is a URL
                        if data.startswith(('http://', 'https://')):
                            urls_list.append(data)
                    
                    return urls_list
                
                # Extract all URLs from the data
                all_urls = extract_urls_from_data(result.data)
                
                # Filter for GitHub repos and documentation
                import re
                github_pattern = r'github\.com/([a-zA-Z0-9-]+/[a-zA-Z0-9-_.]+)'
                
                for url in all_urls:
                    # Check for GitHub repos
                    github_match = re.search(github_pattern, url)
                    if github_match and '/tree/' not in url and '/blob/' not in url:
                        repos_found.append(github_match.group(1))
                    # Check for documentation URLs
                    elif any(doc_indicator in url.lower() for doc_indicator in ['docs', 'documentation', '.readthedocs.', '/guide', '/tutorial']):
                        docs_found.append(url)
                
                # Remove duplicates and limit results
                repos_found = list(set(repos_found))[:3]
                docs_found = list(set(docs_found))[:3]
                
                if repos_found:
                    response += "**🚀 DISCOVERED REPOSITORIES - Index with NIA for deep analysis:**\n"
                    for repo in repos_found:
                        response += f"```\nIndex {repo}\n```\n"
                    response += "✨ Enable AI-powered code search and architecture understanding!\n\n"
                
                if docs_found:
                    response += "**📖 DISCOVERED DOCUMENTATION - Index with NIA for smart search:**\n"
                    for doc in docs_found[:2]:  # Limit to 2 for readability
                        response += f"```\nIndex documentation {doc}\n```\n"
                    response += "✨ Make documentation instantly searchable with AI Q&A!\n\n"
                
                if not repos_found and not docs_found:
                    response += "**🔍 Manual indexing options:**\n"
                    response += "- If you see any GitHub repos mentioned: Say \"Index [owner/repo]\"\n"
                    response += "- If you see any documentation sites: Say \"Index documentation [url]\"\n"
                    response += "- These will unlock NIA's powerful AI search capabilities!\n\n"
                
                response += "**📊 Other actions:**\n"
                response += "- Ask follow-up questions about the research\n"
                response += "- Request a different analysis format\n"
                response += "- Search for more specific information\n"
            else:
                response += "No structured data returned. The research may need a more specific query."
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            # Fallback to regular search if research API fails
            logger.warning(f"Research API failed, falling back to search: {e}")
            return await nia_web_search(query, num_results=10)
            
    except Exception as e:
        logger.error(f"Error in deep research: {str(e)}")
        return [TextContent(
            type="text",
            text=f"❌ Research error: {str(e)}\n\n"
                 "Try simplifying your question or using the regular nia_web_search tool."
        )]

# Resources

# Note: FastMCP doesn't have list_resources or read_resource decorators
# Resources should be registered individually using @mcp.resource()
# For now, commenting out these functions as they use incorrect decorators

# @mcp.list_resources
# async def list_resources() -> List[Resource]:
#     """List available repositories as resources."""
#     try:
#         client = await ensure_api_client()
#         repositories = await client.list_repositories()
#         
#         resources = []
#         for repo in repositories:
#             if repo.get("status") == "completed":
#                 resources.append(Resource(
#                     uri=f"nia://repository/{repo['repository']}",
#                     name=repo["repository"],
#                     description=f"Indexed repository at branch {repo.get('branch', 'main')}",
#                     mimeType="application/x-nia-repository"
#                 ))
#         
#         return resources
#     except Exception as e:
#         logger.error(f"Error listing resources: {e}")
#         return []

# @mcp.read_resource
# async def read_resource(uri: str) -> TextContent:
#     """Read information about a repository resource."""
#     if not uri.startswith("nia://repository/"):
#         return TextContent(
#             type="text",
#             text=f"Unknown resource URI: {uri}"
#         )
#     
#     repository = uri.replace("nia://repository/", "")
#     
#     try:
#         client = await ensure_api_client()
#         status = await client.get_repository_status(repository)
#         
#         if not status:
#             return TextContent(
#                 type="text",
#                 text=f"Repository not found: {repository}"
#             )
#         
#         # Format repository information
#         lines = [
#             f"# Repository: {repository}",
#             "",
#             f"**Status:** {status['status']}",
#             f"**Branch:** {status.get('branch', 'main')}",
#         ]
#         
#         if status.get("indexed_at"):
#             lines.append(f"**Indexed:** {status['indexed_at']}")
#         
#         lines.extend([
#             "",
#             "## Usage",
#             f"Search this repository using the `search_codebase` tool with:",
#             f'`repositories=["{repository}"]`'
#         ])
#         
#         return TextContent(type="text", text="\n".join(lines))
#         
#     except Exception as e:
#         logger.error(f"Error reading resource: {e}")
#         return TextContent(
#             type="text",
#             text=f"Error reading resource: {str(e)}"
#         )

# Server lifecycle

async def cleanup():
    """Cleanup resources on shutdown."""
    global api_client
    if api_client:
        await api_client.close()
        api_client = None

def run():
    """Run the MCP server."""
    try:
        # Check for API key early
        get_api_key()
        
        logger.info("Starting NIA MCP Server")
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        # Run cleanup
        loop = asyncio.new_event_loop()
        loop.run_until_complete(cleanup())
        loop.close()