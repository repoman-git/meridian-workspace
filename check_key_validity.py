#!/usr/bin/env python3
"""
Check if API keys in .env files are real or placeholders.
BASTARD-APPROVED-PLAN Day 1 Task 1.1
"""

import os
import re
from pathlib import Path


def check_key_validity(key_name: str, key_value: str) -> tuple[bool, str]:
    """
    Check if a key looks like a real API key vs placeholder.
    Returns: (is_valid, reason)
    """
    if not key_value or not key_value.strip():
        return False, "empty"
    
    key = key_value.strip()
    
    # Check for obvious placeholders
    placeholder_patterns = [
        r'^\s*$',  # Empty/whitespace only
        r'^your-.*-key',  # "your-xxx-key"
        r'^xxx+$',  # "xxx", "xxxxxxx"
        r'^test.*key',  # "test-key", etc
        r'^example.*key',  # "example-key"
        r'^placeholder',  # "placeholder..."
        r'^replace.*with',  # "replace with..."
        r'^SK-.*$',  # Some placeholder formats use SK-
    ]
    
    for pattern in placeholder_patterns:
        if re.match(pattern, key, re.IGNORECASE):
            return False, f"matches placeholder pattern: {pattern}"
    
    # Check length (real API keys are usually 20+ chars)
    if len(key) < 20:
        return False, f"too short ({len(key)} chars - real keys usually 20+)"
    
    # Check for realistic patterns
    # Anthropic keys often start with "sk-ant-" or similar
    if key_name == "ANTHROPIC_API_KEY":
        if key.startswith("sk-ant-") or key.startswith("sk-ant-api03-"):
            return True, "valid Anthropic format"
        if len(key) >= 40:  # Anthropic keys are usually long
            return True, "reasonable length for Anthropic"
    
    # OpenAI keys start with "sk-"
    if key_name == "OPENAI_API_KEY":
        if key.startswith("sk-"):
            return True, "valid OpenAI format"
        if len(key) >= 40:
            return True, "reasonable length for OpenAI"
    
    # Google/Gemini keys are often long strings
    if key_name in ["GOOGLE_GEMINI_API_KEY", "GEMINI_API_KEY"]:
        if len(key) >= 30:
            return True, "reasonable length for Gemini"
    
    # Grok/xAI keys can vary in format
    if key_name in ["GROK_API_KEY", "XAI_API_KEY"]:
        if len(key) >= 30:
            return True, "reasonable length for Grok"
    
    # If it's long enough and doesn't match placeholders, assume valid
    if len(key) >= 30:
        return True, "long enough, likely valid"
    elif len(key) >= 20:
        return True, "medium length, possibly valid"
    
    return False, f"suspicious length ({len(key)} chars)"


def load_env_file(env_path: Path) -> dict:
    """Load .env file into dict."""
    env_vars = {}
    if not env_path.exists():
        return env_vars
    
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key:
                    env_vars[key] = value
    
    return env_vars


def main():
    """Main function."""
    workspace_root = Path(__file__).parent
    
    print("\n" + "="*60)
    print("BASTARD-APPROVED-PLAN - Day 1 Task 1.1")
    print("API Key Validity Check")
    print("="*60)
    
    # Check meridian-core .env
    core_env = workspace_root / "meridian-core" / ".env"
    research_env = workspace_root / "meridian-research" / ".env"
    
    # Load environment variables
    env_vars = {}
    if core_env.exists():
        print(f"\nChecking {core_env}...")
        env_vars.update(load_env_file(core_env))
    
    if research_env.exists():
        print(f"Checking {research_env}...")
        env_vars.update(load_env_file(research_env))
    
    # Check the 4 required providers
    providers = [
        ("claude", "ANTHROPIC_API_KEY"),
        ("chatgpt", "OPENAI_API_KEY"),
        ("gemini", "GOOGLE_GEMINI_API_KEY"),
        ("grok", "GROK_API_KEY"),
    ]
    
    # Also check alternative names
    alt_names = {
        "GOOGLE_GEMINI_API_KEY": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "GROK_API_KEY": ["XAI_API_KEY"],
    }
    
    results = {}
    
    print("\nAnalyzing keys...\n")
    
    for provider_name, key_name in providers:
        # Get primary key
        key_value = env_vars.get(key_name)
        
        # Try alternatives if primary not found
        if not key_value and key_name in alt_names:
            for alt in alt_names[key_name]:
                if alt in env_vars:
                    key_value = env_vars[alt]
                    key_name = alt  # Update to show which one was found
                    break
        
        if not key_value:
            results[provider_name] = (False, "not_found", "Key not in .env files")
            print(f"{provider_name.upper():10} ❌ NOT FOUND")
            continue
        
        # Check validity
        is_valid, reason = check_key_validity(key_name, key_value)
        
        # Show preview (first 8 chars, last 4 chars, and length)
        if len(key_value) > 12:
            preview = f"{key_value[:8]}...{key_value[-4:]} ({len(key_value)} chars)"
        else:
            preview = f"*** ({len(key_value)} chars)"
        
        status = "✅ VALID" if is_valid else "❌ PLACEHOLDER/INVALID"
        results[provider_name] = (is_valid, reason, preview)
        
        print(f"{provider_name.upper():10} {status:20} {reason:40} {preview}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    valid = [p for p, (v, _, _) in results.items() if v]
    invalid = [p for p, (v, _, _) in results.items() if not v]
    
    print(f"\nValid keys: {len(valid)}/4")
    for p in valid:
        _, reason, preview = results[p]
        print(f"  ✅ {p.upper()}: {reason} - {preview}")
    
    if invalid:
        print(f"\nInvalid/Missing keys: {len(invalid)}/4")
        for p in invalid:
            _, reason, preview = results[p]
            print(f"  ❌ {p.upper()}: {reason}")
    
    print(f"\n{'='*60}")
    if len(valid) == 4:
        print("✅ ALL KEYS APPEAR VALID")
        print("   Next: Test API connectivity")
    elif len(valid) > 0:
        print(f"⚠️  {len(valid)}/4 keys appear valid")
        print("   Replace invalid keys with real API keys")
    else:
        print("❌ NO VALID KEYS FOUND")
        print("   All keys appear to be placeholders or missing")
    print("="*60)
    
    return 0 if len(valid) == 4 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())



