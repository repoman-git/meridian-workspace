# Fix API Keys - Day 1 Task 1.1

## Current Status (2/4 Working)

✅ **GEMINI** - Working  
✅ **GROK** - Working  
❌ **CLAUDE** - 401 Authentication Error (invalid x-api-key)  
❌ **CHATGPT** - 401 Unauthorized

## What to Fix

### Claude (Anthropic)
**Error:** `invalid x-api-key`

**Fix:**
1. Get your API key from: https://console.anthropic.com/
2. Update `/Users/simonerses/data-projects/meridian-core/.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-...your-actual-key...
   ```
3. Verify format: Should start with `sk-ant-` or `sk-ant-api03-`

### ChatGPT (OpenAI)
**Error:** `401 Unauthorized`

**Fix:**
1. Get your API key from: https://platform.openai.com/api-keys
2. Update `/Users/simonerses/data-projects/meridian-core/.env`:
   ```
   OPENAI_API_KEY=sk-...your-actual-key...
   ```
3. Verify format: Should start with `sk-`

## After Adding Keys

Run the test again:
```bash
cd /Users/simonerses/data-projects
python3 test_api_connectivity.py
```

Expected result: All 4 providers should return ✅

## File Location

Edit this file:
```
/Users/simonerses/data-projects/meridian-core/.env
```

The file is gitignored and secure.
