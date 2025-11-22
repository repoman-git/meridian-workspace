#!/usr/bin/env python3
"""
Test all AI providers for BASTARD-APPROVED-PLAN Day 1 Task 1.1

REALITY CHECK: Verify all 4 providers (Claude, ChatGPT, Gemini, Grok) are authenticated.

This script:
1. Checks credential storage for each provider
2. Tests each provider individually with a simple query
3. Reports which providers work and which don't
"""

import sys
import os
from pathlib import Path

# Add meridian-core to path
workspace_root = Path(__file__).parent
meridian_core_src = workspace_root / "meridian-core" / "src"
sys.path.insert(0, str(meridian_core_src))

# Import credential store first (no heavy dependencies)
sys.path.insert(0, str(meridian_core_src / "meridian_core" / "utils"))
import credential_store

# Import connectors directly (avoid full package import)
connector_path = meridian_core_src / "meridian_core" / "connectors"
sys.path.insert(0, str(connector_path))

# Try importing connectors, skip if dependencies missing
try:
    from anthropic_connector import AnthropicConnector
except ImportError as e:
    print(f"Warning: Could not import AnthropicConnector: {e}")
    AnthropicConnector = None

try:
    from openai_connector import OpenAIConnector
except ImportError as e:
    print(f"Warning: Could not import OpenAIConnector: {e}")
    OpenAIConnector = None

try:
    from gemini_connector import GeminiConnector
except ImportError as e:
    print(f"Warning: Could not import GeminiConnector: {e}")
    GeminiConnector = None

try:
    from grok_connector import GrokConnector
except ImportError as e:
    print(f"Warning: Could not import GrokConnector: {e}")
    GrokConnector = None

def check_credential(provider_name: str, key_name: str) -> tuple[bool, str]:
    """Check if credential exists and length."""
    key = credential_store.get_secret(key_name)
    # Also check environment variables as fallback
    if not key:
        key = os.getenv(key_name)
    if not key:
        return False, "MISSING"
    
    key_len = len(key.strip())
    if key_len < 10:
        return False, f"TOO_SHORT ({key_len} chars)"
    
    # Check for placeholder values
    if any(placeholder in key.lower() for placeholder in ['placeholder', 'xxx', 'example', 'your_key']):
        return False, f"PLACEHOLDER ({key_len} chars)"
    
    return True, f"EXISTS ({key_len} chars)"


def test_provider(provider_name: str, connector_class, env_keys: list[str]) -> tuple[bool, str]:
    """Test a single provider."""
    print(f"\n{'='*60}")
    print(f"Testing {provider_name.upper()}")
    print(f"{'='*60}")
    
    # Check credentials
    print("1. Checking credentials...")
    credential_found = False
    for key_name in env_keys:
        found, status = check_credential(provider_name, key_name)
        print(f"   {key_name}: {status}")
        if found:
            credential_found = True
    
    if not credential_found:
        return False, "No valid credentials found"
    
    # Test connector
    print("2. Testing connector...")
    try:
        connector = connector_class()
        test_query = "Reply with just 'OK' if you receive this"
        
        # Use test_connection if available
        if hasattr(connector, 'test_connection'):
            result = connector.test_connection()
            if isinstance(result, dict):
                if result.get('success'):
                    response = result.get('response', 'OK')
                    return True, f"Success: {response[:50]}"
                else:
                    error = result.get('error', 'Unknown error')
                    return False, f"Failed: {error}"
        
        # Fallback to send_message
        if hasattr(connector, 'send_message'):
            response = connector.send_message(test_query, max_tokens=50)
            if response and 'content' in response:
                return True, f"Success: {response['content'][:50]}"
            return False, "No response content"
        
        return False, "No test method available"
        
    except Exception as e:
        error_msg = str(e)
        # Extract useful error info
        if "401" in error_msg or "authentication" in error_msg.lower():
            return False, f"401 Authentication Error: {error_msg[:100]}"
        elif "403" in error_msg:
            return False, f"403 Forbidden: {error_msg[:100]}"
        elif "API key" in error_msg:
            return False, f"API Key Error: {error_msg[:100]}"
        else:
            return False, f"Error: {error_msg[:100]}"


def main():
    """Main test function."""
    print("\n" + "="*60)
    print("BASTARD-APPROVED-PLAN - Day 1 Task 1.1")
    print("API Authentication Test")
    print("="*60)
    
    providers = []
    if AnthropicConnector:
        providers.append(("claude", AnthropicConnector, ["ANTHROPIC_API_KEY"]))
    if OpenAIConnector:
        providers.append(("chatgpt", OpenAIConnector, ["OPENAI_API_KEY"]))
    if GeminiConnector:
        providers.append(("gemini", GeminiConnector, ["GOOGLE_GEMINI_API_KEY", "GEMINI_API_KEY"]))
    if GrokConnector:
        providers.append(("grok", GrokConnector, ["GROK_API_KEY", "XAI_API_KEY"]))
    
    if not providers:
        print("❌ ERROR: Could not import any connector classes. Check dependencies.")
        return 1
    
    results = {}
    
    for provider_name, connector_class, env_keys in providers:
        success, message = test_provider(provider_name, connector_class, env_keys)
        results[provider_name] = (success, message)
        
        if success:
            print(f"\n✅ {provider_name.upper()}: {message}")
        else:
            print(f"\n❌ {provider_name.upper()}: {message}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    working = [p for p, (s, _) in results.items() if s]
    broken = [p for p, (s, _) in results.items() if not s]
    
    print(f"\nWorking providers: {len(working)}/4")
    for p in working:
        print(f"  ✅ {p.upper()}")
    
    if broken:
        print(f"\nBroken providers: {len(broken)}/4")
        for p in broken:
            _, msg = results[p]
            print(f"  ❌ {p.upper()}: {msg}")
    
    print(f"\n{'='*60}")
    if len(working) == 4:
        print("✅ ALL PROVIDERS AUTHENTICATED SUCCESSFULLY")
        print("="*60)
        return 0
    else:
        print(f"⚠️  {len(working)}/4 providers working. Review broken providers above.")
        print("="*60)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

