#!/usr/bin/env python3
"""
Test script for unified search functionality
"""
import os
import asyncio
from src.nia_mcp_server.api_client import NIAApiClient

async def test_unified_search():
    """Test the unified search functionality."""
    api_key = os.getenv("NIA_API_KEY")
    if not api_key:
        print("❌ NIA_API_KEY environment variable not set")
        print("   Set it with: export NIA_API_KEY=your-api-key-here")
        return
    
    api_url = os.getenv("NIA_API_URL", "https://api.trynia.ai")
    print(f"🔄 Testing unified search at {api_url}...")
    
    try:
        client = NIAApiClient(api_key, base_url=api_url)
        
        # First, list repositories and data sources
        print("\n📚 Listing repositories...")
        repos = await client.list_repositories()
        print(f"Found {len(repos)} repositories")
        for repo in repos[:3]:
            print(f"  - {repo['repository']} ({repo.get('status', 'unknown')})")
        
        print("\n📄 Listing documentation sources...")
        sources = await client.list_data_sources()
        print(f"Found {len(sources)} documentation sources")
        for source in sources[:3]:
            print(f"  - {source.get('url', 'Unknown')} ({source.get('status', 'unknown')})")
        
        # Test unified search
        if repos or sources:
            print("\n🔍 Testing unified search...")
            query = "authentication"
            messages = [{"role": "user", "content": query}]
            
            # Get first completed repo and source
            repo_list = [r["repository"] for r in repos if r.get("status") == "completed"][:1]
            source_list = [s["id"] for s in sources if s.get("status") == "completed"][:1]
            
            if repo_list or source_list:
                print(f"Searching for '{query}' across:")
                if repo_list:
                    print(f"  - Repository: {repo_list[0]}")
                if source_list:
                    print(f"  - Documentation: {sources[0].get('url', 'Unknown')}")
                
                # Perform unified search
                response_text = ""
                source_count = 0
                
                async for chunk in client.query_unified(
                    messages=messages,
                    repositories=repo_list,
                    data_sources=source_list,
                    search_mode="unified",
                    stream=True,
                    include_sources=True
                ):
                    try:
                        import json
                        data = json.loads(chunk)
                        if "content" in data:
                            response_text += data["content"]
                        if "sources" in data:
                            source_count += len(data["sources"])
                    except:
                        continue
                
                print(f"\n✅ Unified search successful!")
                print(f"Response preview: {response_text[:200]}...")
                print(f"Found {source_count} source references")
            else:
                print("⚠️  No completed repositories or documentation sources to search")
        else:
            print("\n⚠️  No repositories or documentation sources found")
            print("   Index some content first using the MCP tools")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_unified_search())