#!/usr/bin/env python3
"""
Test script to verify NIA MCP Server connection
"""
import os
import asyncio
from src.nia_mcp_server.api_client import NIAApiClient, APIError

async def test_connection():
    """Test the connection to NIA API."""
    api_key = os.getenv("NIA_API_KEY")
    if not api_key:
        print("❌ NIA_API_KEY environment variable not set")
        print("   Set it with: export NIA_API_KEY=your-api-key-here")
        return
    
    api_url = os.getenv("NIA_API_URL", "https://api.trynia.ai")
    print(f"🔄 Testing connection to NIA API at {api_url}...")
    
    try:
        client = NIAApiClient(api_key, base_url=api_url)
        
        # Test API key validation
        if await client.validate_api_key():
            print("✅ API key is valid!")
            
            # Try to list repositories
            try:
                repos = await client.list_repositories()
                print(f"\n📚 You have {len(repos)} indexed repositories")
                
                for repo in repos[:3]:  # Show first 3
                    print(f"   - {repo['repository']} ({repo.get('status', 'unknown')})")
                
                if len(repos) > 3:
                    print(f"   ... and {len(repos) - 3} more")
                    
            except APIError as e:
                print(f"\n❌ {str(e)}")
                if e.status_code == 403 and "lifetime limit" in str(e).lower():
                    print("\n💡 You've reached the free tier limit of 25 API requests.")
                    print("   Upgrade to Pro at https://trynia.ai/billing for unlimited access.")
                
        else:
            print("❌ API key validation failed")
            print("   This could be due to:")
            print("   - Invalid API key")
            print("   - Exceeded usage limits (free tier: 25 lifetime requests)")
            print("   Check your API key at: https://trynia.ai/api-keys")
            
        await client.close()
        
    except APIError as e:
        print(f"❌ {str(e)}")
        if e.status_code == 403:
            print("\n💡 Access forbidden. This usually means:")
            print("   - You've exceeded your usage limits")
            print("   - Your subscription has expired")
            print("   Visit https://trynia.ai/billing to check your account")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())