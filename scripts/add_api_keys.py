#!/usr/bin/env python3
"""
Interactive API key configuration script.
Adds keys to keyring with proper formatting.
"""

import getpass
import keyring
import sys

def add_api_keys_to_keyring():
    """Add API keys to keyring interactively."""
    
    keys_to_add = {
        'ANTHROPIC_API_KEY': 'Claude (Anthropic)',
        'OPENAI_API_KEY': 'ChatGPT (OpenAI)',
        'GOOGLE_GEMINI_API_KEY': 'Gemini (Google)',
        'GROK_API_KEY': 'Grok (xAI)',
        'XAI_API_KEY': 'Grok alternative (xAI)'
    }
    
    print("═══════════════════════════════════════════════════════════")
    print("API Key Configuration - Keyring Method")
    print("═══════════════════════════════════════════════════════════")
    print("")
    print("This script will add API keys to your system keyring.")
    print("Keys are stored securely in macOS Keychain (or equivalent).")
    print("")
    
    added_count = 0
    skipped_count = 0
    
    for key, description in keys_to_add.items():
        # Check if already exists
        try:
            existing = keyring.get_password('meridian', key)
            if existing:
                print(f"✅ {key} ({description}): Already in keyring")
                continue
        except Exception:
            pass
        
        # Prompt for key
        print(f"\n{key} ({description})")
        value = getpass.getpass(f"  Enter API key [Enter to skip]: ")
        
        if value and value.strip():
            try:
                keyring.set_password('meridian', key, value.strip())
                print(f"  ✅ Added to keyring")
                added_count += 1
            except Exception as e:
                print(f"  ❌ Failed to add: {e}")
                skipped_count += 1
        else:
            print(f"  ⚠️  Skipped")
            skipped_count += 1
    
    print(f"\n═══════════════════════════════════════════════════════════")
    print(f"Summary: Added {added_count} keys, Skipped {skipped_count} keys")
    print(f"═══════════════════════════════════════════════════════════")
    
    # Verify
    print("\n=== Verification ===")
    all_present = True
    for key, description in keys_to_add.items():
        try:
            value = keyring.get_password('meridian', key)
            if value:
                # Mask the key (show first 4 and last 4 chars)
                masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                print(f"✅ {key}: Present ({masked})")
            else:
                print(f"❌ {key}: Not in keyring")
                all_present = False
        except Exception as e:
            print(f"⚠️  {key}: Error - {e}")
            all_present = False
    
    if all_present:
        print("\n✅ All API keys are configured!")
    else:
        print("\n⚠️  Some keys are still missing. Run this script again to add them.")
    
    return added_count

if __name__ == "__main__":
    try:
        add_api_keys_to_keyring()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)









