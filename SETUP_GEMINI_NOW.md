# 🔴 URGENT: SETUP GEMINI API KEY

## The Problem
Your `.env` file exists but the GEMINI_API_KEY is set to a placeholder.
The Django settings were also not loading the .env file (NOW FIXED).

## The Solution

### Step 1: Get Your Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key (it looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)

### Step 2: Update .env File

1. Open: `backend\.env`
2. Find this line:
   ```
   GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
   ```
3. Replace `YOUR_GEMINI_API_KEY_HERE` with your actual API key:
   ```
   GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
4. Save the file

### Step 3: Restart Servers (REQUIRED!)

**You MUST restart both servers for the .env changes to take effect:**

1. **Stop the backend server:**
   - Go to terminal running `python manage.py runserver`
   - Press `Ctrl+C`

2. **Stop the background worker:**
   - Go to terminal running `python manage.py process_tasks`
   - Press `Ctrl+C`

3. **Restart backend server:**
   ```bash
   cd backend
   python manage.py runserver
   ```

4. **Restart background worker:**
   ```bash
   cd backend
   python manage.py process_tasks
   ```

### Step 4: Verify It's Working

Run the test script:
```bash
cd backend
python test_dynamic_questions.py
```

**Look for this line in the output:**
```
Gemini API Key Set: Yes
Gemini Service Available: Yes
✅ Gemini is configured and ready for dynamic generation
```

If you see "No" instead of "Yes", the API key is not loaded correctly.

---

## What I Fixed

✅ Added `python-dotenv` import to settings.py
✅ Added `load_dotenv()` call to load .env file
✅ Updated SECRET_KEY to use environment variable
✅ Updated DEBUG to use environment variable
✅ Updated FRONTEND_URL to use environment variable
✅ Created .env file with proper structure

## What YOU Need to Do

🔴 **Replace `YOUR_GEMINI_API_KEY_HERE` with your real API key**
🔴 **Restart both servers**
🔴 **Run test script to verify**

---

## Quick Test After Setup

Once you've done the above, test with a real candidate:

1. Create a job in the UI
2. Upload a candidate with a resume
3. Wait 10-15 seconds for processing
4. Check the candidate details
5. Look at the questions - they should reference specific things from the resume

**Questions should look like:**
```
"I noticed in your resume you built a real-time chat application 
using WebSockets and Redis. Can you walk me through..."
```

**NOT like:**
```
"Can you describe your experience with your technical background..."
```

The first one = Gemini working ✅
The second one = Fallback mode ⚠️

---

## Still Not Working?

If after doing all the above, it's still not working:

1. Check the .env file is in the correct location: `backend\.env`
2. Make sure there are no spaces around the = sign
3. Make sure the API key has no quotes around it
4. Check the terminal output for errors when starting the server
5. Run: `python manage.py shell -c "import os; print(os.getenv('GEMINI_API_KEY'))"`
   - Should print your API key, not None

---

**Last Updated:** February 3, 2026
**Status:** Settings fixed, waiting for you to add your API key
