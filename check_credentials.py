#!/usr/bin/env python3
"""
Check API credentials status - BASTARD-APPROVED-PLAN Day 1 Task 1.1

This checks credential storage without requiring connector dependencies.
"""

import os
import sys
from pathlib import Path

def check_keyring():
    """Try to import and use keyring."""
    try:
        import keyring
        return keyring
    except ImportError:
        return None

def check_credential(key_name: str, keyring_service: str = "meridian-suite") -> tuple[bool, str, str]:
    """
    Check if credential exists.
    Returns: (found, source, value_preview)
    """
    keyring = check_keyring()
    
    # Try keyring first
    if keyring:
        # Check multiple possible service names
        services = ["meridian-suite", "meridian-core", "meridian-research", "meridian-trading-system"]
        for service in services:
            try:
                value = keyring.get_password(service, key_name)
                if value and len(value.strip()) > 10:
                    preview = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                    return True, f"keyring:{service}", preview
            except Exception:
                continue
    
    # Check environment variables
    value = os.getenv(key_name)
    if value and len(value.strip()) > 10:
        preview = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
        return True, "env_var", preview
    
    # Check common alternative names
    alt_names = {
        "ANTHROPIC_API_KEY": ["CLAUDE_API_KEY"],
        "OPENAI_API_KEY": ["CHATGPT_API_KEY"],
        "GOOGLE_GEMINI_API_KEY": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "GROK_API_KEY": ["XAI_API_KEY"],
    }
    
    if key_name in alt_names:
        for alt in alt_names[key_name]:
            value = os.getenv(alt)
            if value and len(value.strip()) > 10:
                preview = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                return True, f"env_var:{alt}", preview
    
    return False, "not_found", ""

def main():
    """Main function."""
    print("\n" + "="*60)
    print("BASTARD-APPROVED-PLAN - Day 1 Task 1.1")
    print("Credential Status Check")
    print("="*60)
    
    providers = [
        ("claude", "ANTHROPIC_API_KEY"),
        ("chatgpt", "OPENAI_API_KEY"),
        ("gemini", "GOOGLE_GEMINI_API_KEY"),
        ("grok", "GROK_API_KEY"),
    ]
    
    results = {}
    
    print("\nChecking credentials...\n")
    
    for provider_name, key_name in providers:
        found, source, preview = check_credential(key_name)
        status = "✅ EXISTS" if found else "❌ MISSING"
        results[provider_name] = (found, source, preview)
        
        print(f"{provider_name.upper():10} {status:12} {source:20} {preview}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    working = [p for p, (f, _, _) in results.items() if f]
    broken = [p for p, (f, _, _) in results.items() if not f]
    
    print(f"\nFound credentials: {len(working)}/4")
    for p in working:
        _, source, preview = results[p]
        print(f"  ✅ {p.upper()}: {source} ({preview})")
    
    if broken:
        print(f"\nMissing credentials: {len(broken)}/4")
        for p in broken:
            print(f"  ❌ {p.upper()}: Not found")
        print("\nTo add credentials:")
        print("  Option 1: Use keyring (recommended):")
        print("    python3 -c \"import keyring; keyring.set_password('meridian-suite', 'ANTHROPIC_API_KEY', 'your-key')\"")
        print("  Option 2: Set environment variable:")
        print("    export ANTHROPIC_API_KEY='your-key'")
    
    print(f"\n{'='*60}")
    if len(working) == 4:
        print("✅ ALL CREDENTIALS FOUND")
        print("   Next: Test actual API connectivity with test_providers.py")
    else:
        print(f"⚠️  {len(working)}/4 credentials found")
        print("   Add missing credentials to proceed")
    print("="*60)
    
    return 0 if len(working) == 4 else 1


if __name__ == "__main__":
    sys.exit(main())

