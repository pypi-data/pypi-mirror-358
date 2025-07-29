import json
import os
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import asyncio
import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from importlib import resources
#Load the environment variables
load_dotenv()

#Initialize the MCP server
mcp = FastMCP("docs")
USER_AGENT = "docs-app/1.0"
SERPER_URL = "https://google.serper.dev/search"

# Environment variables (removing API key exposure)
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Simple in-memory cache with TTL
class SimpleCache:
    def __init__(self, ttl_hours: int = 24, max_entries: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_hours = ttl_hours
        self.max_entries = max_entries

    def _is_expired(self, timestamp: datetime) -> bool:
        return datetime.now() - timestamp > timedelta(hours=self.ttl_hours)

    def get(self, key: str) -> Optional[str]:
        if key in self.cache:
            entry = self.cache[key]
            if not self._is_expired(entry['timestamp']):
                return entry['data']
            else:
                # Remove expired entry
                del self.cache[key]
        return None

    def set(self, key: str, data: str) -> None:
        # Clean up expired entries and enforce max size
        self.clear_expired()
        
        if len(self.cache) >= self.max_entries:
            # Remove oldest entries (simple FIFO)
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }

    def clear_expired(self) -> None:
        expired_keys = [k for k, v in self.cache.items() if self._is_expired(v['timestamp'])]
        for key in expired_keys:
            del self.cache[key]

# Load configuration from external file
def load_config():
    """Load configuration with enhanced popularity data"""
    try:
        # Try to load from package resources first (for installed package)
        try:
            config_text = resources.read_text("documentation_search_enhanced", "config.json")
            config = json.loads(config_text)
        except (FileNotFoundError, ModuleNotFoundError):
            # Fallback to relative path (for development)
            config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.json")
            with open(config_path, "r") as f:
                config = json.load(f)
    except Exception:
        # Final fallback to current directory
        with open("config.json", "r") as f:
            config = json.load(f)
    return config

# Load configuration
config = load_config()
docs_urls = {}
# Handle both old simple URL format and new enhanced format
for lib_name, lib_data in config["docs_urls"].items():
    if isinstance(lib_data, dict):
        docs_urls[lib_name] = lib_data.get("url", "")
    else:
        docs_urls[lib_name] = lib_data

cache_config = config.get("cache", {"enabled": False})

# Initialize cache if enabled
cache = SimpleCache(
    ttl_hours=cache_config.get("ttl_hours", 24),
    max_entries=cache_config.get("max_entries", 1000)
) if cache_config.get("enabled", False) else None

async def search_web_with_retry(query: str, max_retries: int = 3) -> dict:
    """Search web with exponential backoff retry logic"""
    if not SERPER_API_KEY:
        print("⚠️ SERPER_API_KEY not set - web search functionality will be limited")
        return {"organic": []}
    
    payload = json.dumps({"q": query, "num": 2})
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT
    }
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    SERPER_URL, headers=headers, content=payload, 
                    timeout=httpx.Timeout(30.0, read=60.0)
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            if attempt == max_retries - 1:
                print(f"Timeout after {max_retries} attempts for query: {query}")
                return {"organic": []}
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limited
                if attempt == max_retries - 1:
                    print(f"Rate limited after {max_retries} attempts")
                    return {"organic": []}
                await asyncio.sleep(2 ** (attempt + 2))  # Longer wait for rate limits
            else:
                print(f"HTTP error {e.response.status_code}: {e}")
                return {"organic": []}
                
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Unexpected error after {max_retries} attempts: {e}")
                return {"organic": []}
            await asyncio.sleep(2 ** attempt)
    
    return {"organic": []}

async def fetch_url_with_cache(url: str, max_retries: int = 3) -> str:
    """Fetch URL content with caching and retry logic"""
    # Generate cache key
    cache_key = hashlib.md5(url.encode()).hexdigest()
    
    # Check cache first
    if cache:
        cached_content = cache.get(cache_key)
        if cached_content:
            return cached_content
    
    # Fetch with retry logic
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, 
                    timeout=httpx.Timeout(30.0, read=60.0),
                    headers={"User-Agent": USER_AGENT},
                    follow_redirects=True
                )
                response.raise_for_status()
                
                # Parse content
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text and clean it up
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Cache the result
                if cache and text:
                    cache.set(cache_key, text)
                
                return text
                
        except httpx.TimeoutException:
            if attempt == max_retries - 1:
                return f"Timeout error fetching {url}"
            await asyncio.sleep(2 ** attempt)
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Page not found: {url}"
            elif e.response.status_code == 403:
                return f"Access forbidden: {url}"
            elif attempt == max_retries - 1:
                return f"HTTP error {e.response.status_code} for {url}"
            await asyncio.sleep(2 ** attempt)
            
        except Exception as e:
            if attempt == max_retries - 1:
                return f"Error fetching {url}: {str(e)}"
            await asyncio.sleep(2 ** attempt)
    
    return f"Failed to fetch {url} after {max_retries} attempts"

# Backward compatibility aliases
async def search_web(query: str) -> dict:
    return await search_web_with_retry(query)

async def fetch_url(url: str) -> str:
    return await fetch_url_with_cache(url)
    
        

@mcp.tool()
async def get_docs(query: str, library: str):
    """
    Search the latest docs for a given query and library.

    Args:
        query: The query to search for (e.g. "Chroma DB")
        library: The library to search in (e.g. "langchain")

    Returns:
        Text from the docs (limited to ~50KB for readability)
    """
    
    # Check auto-approve settings
    config = load_config()
    lib_config = config.get("docs_urls", {}).get(library, {})
    auto_approve = lib_config.get("auto_approve", True)
    
    if not auto_approve:
        # For libraries marked as requiring approval (like AWS, cloud services)
        print(f"⚠️  Requesting approval to search {library} documentation...")
    
    if library not in docs_urls:
        raise ValueError(f"Library {library} not supported by this tool")
    
    # Clean expired cache entries periodically
    if cache:
        cache.clear_expired()
    
    query = f"site:{docs_urls[library]} {query}"
    results = await search_web(query)
    if len(results["organic"]) == 0:
        return "No results found"
    
    # Fetch content from multiple results concurrently
    tasks = [fetch_url(result["link"]) for result in results["organic"]]
    contents = await asyncio.gather(*tasks, return_exceptions=True)
    
    text = ""
    max_length = 50000  # Limit to ~50KB for better readability
    
    for i, content in enumerate(contents):
        if isinstance(content, Exception):
            error_msg = f"\n[Error fetching {results['organic'][i]['link']}: {str(content)}]\n"
            if len(text) + len(error_msg) > max_length:
                text += f"\n... [Results truncated at {max_length} characters for readability] ..."
                break
            text += error_msg
        else:
            # content is a string here
            content_str = str(content)  # Ensure it's a string for type safety
            source_header = f"\n--- Source: {results['organic'][i]['link']} ---\n"
            new_content = source_header + content_str + "\n"
            
            if len(text) + len(new_content) > max_length:
                # Add partial content if we have room
                remaining_space = max_length - len(text) - 100  # Leave room for truncation message
                if remaining_space > 500:  # Only add if we have meaningful space
                    text += source_header + content_str[:remaining_space] + "\n"
                text += f"\n... [Results truncated at {max_length} characters for readability] ..."
                break
            text += new_content
    
    return text.strip()

@mcp.tool()
async def suggest_libraries(partial_name: str):
    """
    Suggest libraries based on partial input for auto-completion.
    
    Args:
        partial_name: Partial library name to search for (e.g. "lang" -> ["langchain"])
    
    Returns:
        List of matching library names
    """
    if not partial_name:
        return list(sorted(docs_urls.keys()))
    
    partial_lower = partial_name.lower()
    suggestions = []
    
    # Exact matches first
    for lib in docs_urls.keys():
        if lib.lower() == partial_lower:
            suggestions.append(lib)
    
    # Starts with matches
    for lib in docs_urls.keys():
        if lib.lower().startswith(partial_lower) and lib not in suggestions:
            suggestions.append(lib)
    
    # Contains matches
    for lib in docs_urls.keys():
        if partial_lower in lib.lower() and lib not in suggestions:
            suggestions.append(lib)
    
    return sorted(suggestions[:10])  # Limit to top 10 suggestions

@mcp.tool()
async def health_check():
    """
    Check the health and availability of documentation sources.
    
    Returns:
        Dictionary with health status of each library's documentation site
    """
    results = {}
    
    # Test a sample of libraries to avoid overwhelming servers
    sample_libraries = list(docs_urls.items())[:5]
    
    for library, url in sample_libraries:
        start_time = time.time()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(
                    url, 
                    timeout=httpx.Timeout(10.0),
                    headers={"User-Agent": USER_AGENT},
                    follow_redirects=True
                )
                response_time = time.time() - start_time
                results[library] = {
                    "status": "healthy",
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time * 1000, 2),
                    "url": url
                }
        except httpx.TimeoutException:
            results[library] = {
                "status": "timeout",
                "error": "Request timed out",
                "url": url
            }
        except Exception as e:
            results[library] = {
                "status": "error",
                "error": str(e),
                "url": url
            }
    
    # Add cache stats if caching is enabled
    if cache:
        results["_cache_stats"] = {
            "enabled": True,
            "entries": len(cache.cache),
            "max_entries": cache.max_entries,
            "ttl_hours": cache.ttl_hours
        }
    else:
        results["_cache_stats"] = {"enabled": False}
    
    return results

@mcp.tool()
async def clear_cache():
    """
    Clear the documentation cache to force fresh fetches.
    
    Returns:
        Status message about cache clearing
    """
    if cache:
        entries_cleared = len(cache.cache)
        cache.cache.clear()
        return f"Cache cleared. Removed {entries_cleared} cached entries."
    else:
        return "Caching is not enabled."

@mcp.tool()
async def get_cache_stats():
    """
    Get statistics about the current cache usage.
    
    Returns:
        Dictionary with cache statistics
    """
    if not cache:
        return {"enabled": False, "message": "Caching is not enabled"}
    
    # Count expired entries
    expired_count = sum(1 for entry in cache.cache.values() 
                       if cache._is_expired(entry['timestamp']))
    
    return {
        "enabled": True,
        "total_entries": len(cache.cache),
        "expired_entries": expired_count,
        "active_entries": len(cache.cache) - expired_count,
        "max_entries": cache.max_entries,
        "ttl_hours": cache.ttl_hours,
        "memory_usage_estimate": f"{len(str(cache.cache)) / 1024:.2f} KB"
    }

@mcp.tool()
async def semantic_search(query: str, library: str, context: Optional[str] = None):
    """
    Enhanced semantic search with relevance ranking and content analysis.

    Args:
        query: The search query
        library: The library to search in
        context: Optional context about your project or use case

    Returns:
        Enhanced search results with relevance scores and metadata
    """
    from .smart_search import smart_search
    
    try:
        results = await smart_search.semantic_search(query, library, context)
        
        return {
            "query": query,
            "library": library,
            "total_results": len(results),
            "results": [
                {
                    "title": result.title,
                    "url": result.url,
                    "snippet": result.snippet[:300] + "..." if len(result.snippet) > 300 else result.snippet,
                    "relevance_score": result.relevance_score,
                    "content_type": result.content_type,
                    "difficulty_level": result.difficulty_level,
                    "estimated_read_time": f"{result.estimated_read_time} min",
                    "has_code_examples": result.code_snippets_count > 0
                }
                for result in results[:5]  # Top 5 results
            ]
        }
    except Exception as e:
        return {"error": f"Search failed: {str(e)}", "results": []}


@mcp.tool()
async def filtered_search(query: str, library: str, content_type: Optional[str] = None, 
                         difficulty_level: Optional[str] = None, has_code_examples: Optional[bool] = None):
    """
    Search with advanced filtering options.

    Args:
        query: The search query
        library: The library to search in
        content_type: Filter by content type ("tutorial", "reference", "example", "guide")
        difficulty_level: Filter by difficulty ("beginner", "intermediate", "advanced")
        has_code_examples: Filter for content with code examples (true/false)

    Returns:
        Filtered search results matching specified criteria
    """
    from .smart_search import filtered_search, SearchFilters
    
    filters = SearchFilters(
        content_type=content_type,
        difficulty_level=difficulty_level,
        has_code_examples=has_code_examples
    )
    
    try:
        results = await filtered_search.search_with_filters(query, library, filters)
        
        return {
            "query": query,
            "library": library,
            "filters_applied": {
                "content_type": content_type,
                "difficulty_level": difficulty_level,
                "has_code_examples": has_code_examples
            },
            "total_results": len(results),
            "results": [
                {
                    "title": result.title,
                    "url": result.url,
                    "snippet": result.snippet[:200] + "..." if len(result.snippet) > 200 else result.snippet,
                    "relevance_score": result.relevance_score,
                    "content_type": result.content_type,
                    "difficulty_level": result.difficulty_level,
                    "estimated_read_time": f"{result.estimated_read_time} min"
                }
                for result in results[:10]
            ]
        }
    except Exception as e:
        return {"error": f"Filtered search failed: {str(e)}", "results": []}


@mcp.tool()
async def get_learning_path(library: str, experience_level: str = "beginner"):
    """
    Get a structured learning path for a library based on experience level.

    Args:
        library: The library to create a learning path for
        experience_level: Your current level ("beginner", "intermediate", "advanced")

    Returns:
        Structured learning path with progressive topics and resources
    """
    learning_paths = {
        "fastapi": {
            "beginner": [
                {"topic": "Installation and Setup", "query": "fastapi installation setup", "type": "tutorial"},
                {"topic": "Your First API", "query": "fastapi hello world first api", "type": "tutorial"},
                {"topic": "Path Parameters", "query": "fastapi path parameters", "type": "example"},
                {"topic": "Request Body", "query": "fastapi request body pydantic", "type": "example"},
                {"topic": "Response Models", "query": "fastapi response models", "type": "tutorial"},
            ],
            "intermediate": [
                {"topic": "Authentication", "query": "fastapi authentication JWT OAuth", "type": "tutorial"},
                {"topic": "Database Integration", "query": "fastapi database sqlalchemy", "type": "example"},
                {"topic": "Middleware", "query": "fastapi middleware CORS", "type": "reference"},
                {"topic": "Error Handling", "query": "fastapi error handling exceptions", "type": "example"},
                {"topic": "Testing", "query": "fastapi testing pytest", "type": "tutorial"},
            ],
            "advanced": [
                {"topic": "Advanced Dependency Injection", "query": "fastapi dependency injection advanced", "type": "reference"},
                {"topic": "Background Tasks", "query": "fastapi background tasks celery", "type": "example"},
                {"topic": "Performance Optimization", "query": "fastapi performance optimization async", "type": "tutorial"},
                {"topic": "Production Deployment", "query": "fastapi production deployment docker", "type": "tutorial"},
                {"topic": "Custom Middleware", "query": "fastapi custom middleware", "type": "reference"},
            ]
        },
        "react": {
            "beginner": [
                {"topic": "React Basics", "query": "react components JSX props", "type": "tutorial"},
                {"topic": "State Management", "query": "react useState hooks", "type": "example"},
                {"topic": "Event Handling", "query": "react event handling onClick", "type": "example"},
                {"topic": "Lists and Keys", "query": "react lists keys map", "type": "tutorial"},
                {"topic": "Forms", "query": "react forms controlled components", "type": "example"},
            ],
            "intermediate": [
                {"topic": "useEffect Hook", "query": "react useEffect lifecycle", "type": "tutorial"},
                {"topic": "Context API", "query": "react context API state management", "type": "example"},
                {"topic": "React Router", "query": "react router navigation", "type": "tutorial"},
                {"topic": "Custom Hooks", "query": "react custom hooks", "type": "example"},
                {"topic": "Error Boundaries", "query": "react error boundaries", "type": "reference"},
            ],
            "advanced": [
                {"topic": "Performance Optimization", "query": "react performance memo useMemo", "type": "tutorial"},
                {"topic": "Advanced Patterns", "query": "react render props higher order components", "type": "reference"},
                {"topic": "Testing", "query": "react testing jest testing-library", "type": "tutorial"},
                {"topic": "Server-Side Rendering", "query": "react SSR Next.js", "type": "tutorial"},
                {"topic": "State Management Libraries", "query": "react redux zustand", "type": "reference"},
            ]
        }
    }
    
    if library not in learning_paths:
        return {"error": f"Learning path not available for {library}"}
    
    if experience_level not in learning_paths[library]:
        return {"error": f"Experience level {experience_level} not supported"}
    
    path = learning_paths[library][experience_level]
    
    return {
        "library": library,
        "experience_level": experience_level,
        "total_topics": len(path),
        "estimated_total_time": f"{len(path) * 2}-{len(path) * 4} hours",
        "learning_path": [
            {
                "step": i + 1,
                "topic": item["topic"],
                "content_type": item["type"],
                "search_query": item["query"],
                "estimated_time": "2-4 hours"
            }
            for i, item in enumerate(path)
        ],
        "next_level": {
            "beginner": "intermediate",
            "intermediate": "advanced", 
            "advanced": "Consider specializing in specific areas"
        }.get(experience_level, "")
    }


@mcp.tool()
async def get_code_examples(library: str, topic: str, language: str = "python"):
    """
    Get curated code examples for a specific topic and library.

    Args:
        library: The library to search for examples
        topic: The specific topic or feature
        language: Programming language for examples

    Returns:
        Curated code examples with explanations
    """
    
    # Enhanced query for code-specific search
    code_query = f"{library} {topic} example code {language}"
    
    try:
        # Use filtered search to find examples with code
        from .smart_search import filtered_search, SearchFilters
        
        filters = SearchFilters(
            content_type="example",
            has_code_examples=True
        )
        
        results = await filtered_search.search_with_filters(code_query, library, filters)
        
        if not results:
            # Fallback to regular search
            config = load_config()
            if library not in docs_urls:
                return {"error": f"Library {library} not supported"}
            
            query = f"site:{docs_urls[library]} {code_query}"
            search_results = await search_web(query)
            
            if not search_results.get("organic"):
                return {"error": "No code examples found"}
            
            # Process first result for code extraction
            first_result = search_results["organic"][0]
            content = await fetch_url(first_result["link"])
            
            # Extract code snippets (simplified)
            code_blocks = []
            import re
            code_pattern = r'```(?:python|javascript|typescript|js)?\n(.*?)```'
            matches = re.finditer(code_pattern, content, re.DOTALL)
            
            for i, match in enumerate(matches):
                if i >= 3:  # Limit to 3 examples
                    break
                code_blocks.append({
                    "example": i + 1,
                    "code": match.group(1).strip(),
                    "language": language,
                    "source_url": first_result["link"]
                })
            
            return {
                "library": library,
                "topic": topic,
                "language": language,
                "total_examples": len(code_blocks),
                "examples": code_blocks
            }
        
        else:
            # Process enhanced results
            examples = []
            for i, result in enumerate(results[:3]):
                examples.append({
                    "example": i + 1,
                    "title": result.title,
                    "description": result.snippet[:200] + "..." if len(result.snippet) > 200 else result.snippet,
                    "url": result.url,
                    "difficulty": result.difficulty_level,
                    "estimated_read_time": f"{result.estimated_read_time} min"
                })
            
            return {
                "library": library,
                "topic": topic,
                "language": language,
                "total_examples": len(examples),
                "examples": examples
            }
    
    except Exception as e:
        return {"error": f"Failed to get code examples: {str(e)}"}


@mcp.tool()
async def get_environment_config():
    """
    Get current environment configuration and settings.

    Returns:
        Current environment configuration details
    """
    from .config_manager import config_manager
    
    config = config_manager.get_config()
    
    return {
        "environment": config_manager.environment,
        "server_config": {
            "logging_level": config["server_config"]["logging_level"],
            "max_concurrent_requests": config["server_config"]["max_concurrent_requests"],
            "request_timeout_seconds": config["server_config"]["request_timeout_seconds"],
        },
        "cache_config": {
            "enabled": config["cache"]["enabled"],
            "ttl_hours": config["cache"]["ttl_hours"],
            "max_entries": config["cache"]["max_entries"],
        },
        "rate_limiting": {
            "enabled": config["rate_limiting"]["enabled"],
            "requests_per_minute": config["rate_limiting"]["requests_per_minute"],
        },
        "features": config["server_config"]["features"],
        "total_libraries": len(config_manager.get_docs_urls()),
        "available_libraries": list(config_manager.get_docs_urls().keys())[:10]  # Show first 10
    }


@mcp.tool()
async def scan_library_vulnerabilities(library_name: str, ecosystem: str = "PyPI"):
    """
    Comprehensive vulnerability scan using OSINT sources (OSV, GitHub Advisories, Safety DB).

    Args:
        library_name: Name of the library to scan (e.g., "fastapi", "react")
        ecosystem: Package ecosystem ("PyPI", "npm", "Maven", "Go", etc.)

    Returns:
        Detailed security report with vulnerabilities, severity levels, and recommendations
    """
    from .vulnerability_scanner import vulnerability_scanner
    
    try:
        # Perform comprehensive scan
        security_report = await vulnerability_scanner.scan_library(library_name, ecosystem)
        
        return {
            "scan_results": security_report.to_dict(),
            "summary": {
                "library": security_report.library_name,
                "ecosystem": security_report.ecosystem,
                "security_score": security_report.security_score,
                "risk_level": (
                    "🚨 High Risk" if security_report.security_score < 50 else
                    "⚠️ Medium Risk" if security_report.security_score < 70 else
                    "✅ Low Risk" if security_report.security_score < 90 else
                    "🛡️ Excellent"
                ),
                "critical_vulnerabilities": security_report.critical_count,
                "total_vulnerabilities": security_report.total_vulnerabilities,
                "primary_recommendation": security_report.recommendations[0] if security_report.recommendations else "No specific recommendations"
            },
            "scan_timestamp": security_report.scan_date,
            "sources": ["OSV Database", "GitHub Security Advisories", "Safety DB (PyPI only)"]
        }
        
    except Exception as e:
        return {
            "error": f"Vulnerability scan failed: {str(e)}",
            "library": library_name,
            "ecosystem": ecosystem,
            "scan_timestamp": datetime.now().isoformat()
        }


@mcp.tool()
async def get_security_summary(library_name: str, ecosystem: str = "PyPI"):
    """
    Get quick security overview for a library without detailed vulnerability list.

    Args:
        library_name: Name of the library
        ecosystem: Package ecosystem (default: PyPI)

    Returns:
        Concise security summary with score and basic recommendations
    """
    from .vulnerability_scanner import security_integration
    
    try:
        summary = await security_integration.get_security_summary(library_name, ecosystem)
        
        # Add security badge
        score = summary.get("security_score", 50)
        if score >= 90:
            badge = "🛡️ EXCELLENT"
            color = "green"
        elif score >= 70:
            badge = "✅ SECURE"
            color = "green"
        elif score >= 50:
            badge = "⚠️ CAUTION"
            color = "yellow"
        else:
            badge = "🚨 HIGH RISK"
            color = "red"
        
        return {
            "library": library_name,
            "ecosystem": ecosystem,
            "security_badge": badge,
            "security_score": score,
            "status": summary.get("status", "unknown"),
            "vulnerabilities": {
                "total": summary.get("total_vulnerabilities", 0),
                "critical": summary.get("critical_vulnerabilities", 0)
            },
            "recommendation": summary.get("primary_recommendation", "No recommendations available"),
            "last_scanned": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "library": library_name,
            "ecosystem": ecosystem,
            "security_badge": "❓ UNKNOWN",
            "security_score": None,
            "status": "scan_failed",
            "error": str(e)
        }


@mcp.tool()
async def compare_library_security(libraries: List[str], ecosystem: str = "PyPI"):
    """
    Compare security scores across multiple libraries to help with selection.

    Args:
        libraries: List of library names to compare
        ecosystem: Package ecosystem for all libraries

    Returns:
        Security comparison with rankings and recommendations
    """
    from .vulnerability_scanner import security_integration
    
    if len(libraries) > 10:
        return {"error": "Maximum 10 libraries allowed for comparison"}
    
    results = []
    
    # Scan all libraries in parallel for faster comparison
    scan_tasks = [
        security_integration.get_security_summary(lib, ecosystem) 
        for lib in libraries
    ]
    
    try:
        summaries = await asyncio.gather(*scan_tasks, return_exceptions=True)
        
        for i, (library, summary) in enumerate(zip(libraries, summaries)):
            if isinstance(summary, Exception):
                results.append({
                    "library": library,
                    "security_score": 0,
                    "status": "scan_failed",
                    "error": str(summary)
                })
            else:
                # summary is a dict here, not an exception
                summary_dict = summary
                results.append({
                    "library": library,
                    "security_score": summary_dict.get("security_score", 0),
                    "status": summary_dict.get("status", "unknown"),
                    "vulnerabilities": summary_dict.get("total_vulnerabilities", 0),
                    "critical_vulnerabilities": summary_dict.get("critical_vulnerabilities", 0),
                    "recommendation": summary_dict.get("primary_recommendation", "")
                })
        
        # Sort by security score (highest first)
        results.sort(key=lambda x: x.get("security_score", 0), reverse=True)
        
        # Add rankings
        for i, result in enumerate(results):
            result["rank"] = i + 1
            score = result.get("security_score", 0)
            if score >= 90:
                result["rating"] = "🛡️ Excellent"
            elif score >= 70:
                result["rating"] = "✅ Secure"
            elif score >= 50:
                result["rating"] = "⚠️ Caution"
            else:
                result["rating"] = "🚨 High Risk"
        
        # Generate overall recommendation
        if results:
            best_lib = results[0]
            worst_lib = results[-1]
            
            if best_lib.get("security_score", 0) >= 80:
                overall_rec = f"✅ Recommended: {best_lib['library']} has excellent security"
            elif best_lib.get("security_score", 0) >= 60:
                overall_rec = f"⚠️ Proceed with caution: {best_lib['library']} is the most secure option"
            else:
                overall_rec = "🚨 Security concerns: All libraries have significant vulnerabilities"
        else:
            overall_rec = "Unable to generate recommendation"
        
        return {
            "comparison_results": results,
            "total_libraries": len(libraries),
            "scan_timestamp": datetime.now().isoformat(),
            "overall_recommendation": overall_rec,
            "ecosystem": ecosystem
        }
        
    except Exception as e:
        return {
            "error": f"Security comparison failed: {str(e)}",
            "libraries": libraries,
            "ecosystem": ecosystem
        }


@mcp.tool()
async def suggest_secure_libraries(partial_name: str, include_security_score: bool = True):
    """
    Enhanced library suggestions that include security scores for informed decisions.

    Args:
        partial_name: Partial library name to search for
        include_security_score: Whether to include security scores (slower but more informative)

    Returns:
        Library suggestions with optional security information
    """
    # Get basic suggestions first
    basic_suggestions = await suggest_libraries(partial_name)
    
    if not include_security_score or not basic_suggestions:
        return {
            "suggestions": basic_suggestions,
            "partial_name": partial_name,
            "security_info_included": False
        }
    
    # Add security information for top 5 suggestions
    from .vulnerability_scanner import security_integration
    
    enhanced_suggestions = []
    top_suggestions = basic_suggestions[:5]  # Limit to avoid too many API calls
    
    # Get security scores in parallel
    security_tasks = [
        security_integration.get_security_summary(lib, "PyPI") 
        for lib in top_suggestions
    ]
    
    try:
        security_results = await asyncio.gather(*security_tasks, return_exceptions=True)
        
        for lib, security_result in zip(top_suggestions, security_results):
            suggestion = {"library": lib}
            
            if isinstance(security_result, Exception):
                suggestion.update({
                    "security_score": None,
                    "security_status": "unknown",
                    "security_badge": "❓"
                })
            else:
                # security_result is a dict here, not an exception
                result_dict = security_result
                score = result_dict.get("security_score", 50)
                suggestion.update({
                    "security_score": score,
                    "security_status": result_dict.get("status", "unknown"),
                    "security_badge": (
                        "🛡️" if score >= 90 else
                        "✅" if score >= 70 else
                        "⚠️" if score >= 50 else
                        "🚨"
                    ),
                    "vulnerabilities": result_dict.get("total_vulnerabilities", 0)
                })
            
            enhanced_suggestions.append(suggestion)
        
        # Add remaining suggestions without security info
        for lib in basic_suggestions[5:]:
            enhanced_suggestions.append({
                "library": lib,
                "security_score": None,
                "security_status": "not_scanned",
                "note": "Use scan_library_vulnerabilities for security details"
            })
        
        # Sort by security score for enhanced suggestions
        enhanced_suggestions.sort(
            key=lambda x: x.get("security_score") or 0, 
            reverse=True
        )
        
        return {
            "suggestions": enhanced_suggestions,
            "partial_name": partial_name,
            "security_info_included": True,
            "total_suggestions": len(enhanced_suggestions),
            "note": "Libraries with security scores are sorted by security rating"
        }
        
    except Exception as e:
        return {
            "suggestions": [{"library": lib} for lib in basic_suggestions],
            "partial_name": partial_name,
            "security_info_included": False,
            "error": f"Security enhancement failed: {str(e)}"
        }


def main():
    """Main entry point for the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
    
