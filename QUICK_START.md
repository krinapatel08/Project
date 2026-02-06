# Quick Start Guide - Dynamic Question Generation

## 🚀 For HR Users

### Step 1: Set Up Gemini API (Recommended)

1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Add to `backend/.env`:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```
4. Restart backend servers

**Without API Key:** System still works with intelligent fallback!

### Step 2: Create a Job

1. Login to HR Dashboard
2. Click "Create Job"
3. Fill in:
   - Title (e.g., "Senior Python Developer")
   - Description (full JD text)
   - Required Skills (e.g., "Python, Django, PostgreSQL")
   - Experience Level (e.g., "Senior")
   - Interview Config:
     - Number of oral questions (default: 5)
     - Number of coding questions (default: 2)
     - Time limits

### Step 3: Upload Candidates

**Option A: Single Upload**
1. Go to Job Details
2. Click "Add Candidate"
3. Fill in:
   - Name
   - Email
   - Upload PDF resume OR provide resume URL

**Option B: Bulk Upload (CSV)**
1. Prepare CSV file:
   ```csv
   Candidate Name,Candidate Email,Resume Link
   John Doe,john@example.com,https://example.com/resume.pdf
   Jane Smith,jane@example.com,https://docs.google.com/spreadsheets/.../pubhtml
   ```
2. Upload CSV file
3. System processes all candidates automatically

### Step 4: Wait for Processing

- Background task processes each candidate
- Resume is parsed (non-AI text extraction)
- Questions are generated (AI-powered or fallback)
- Interview link is created
- Email is sent (or logged)

**Processing time:** ~10-15 seconds per candidate

### Step 5: View Generated Questions

1. Go to Job Details
2. Click on a candidate
3. View their unique questions:
   - See question text
   - See what skill it tests (focus area)
   - See difficulty level
   - See generation metadata

### Step 6: Verify Personalization

**Check that questions are unique:**
1. View questions for Candidate A
2. View questions for Candidate B
3. Confirm questions are different
4. Confirm questions reference their specific skills

**Metadata to check:**
- `generated_at` - Different timestamps
- `focus_area` - Relevant to their background
- `gemini_metadata.candidate_id` - Different IDs

---

## 💻 For Developers

### Quick Test

```bash
cd backend
python test_dynamic_questions.py
```

Expected output:
- ✅ Gemini availability check
- ✅ Question generation test
- ✅ Uniqueness verification
- ✅ Database integration check

### API Testing

**Get candidate questions:**
```bash
curl http://localhost:8000/api/candidates/1/detail/
```

**Response includes:**
```json
{
  "questions": [
    {
      "text": "Based on your work with Django...",
      "focus_area": "Framework Knowledge",
      "difficulty": "Medium",
      "generated_at": "2026-02-03T15:30:00Z",
      "is_dynamic": true,
      "gemini_metadata": {
        "generated_by": "gemini",
        "candidate_id": 1,
        "resume_based": true,
        "jd_based": true
      }
    }
  ]
}
```

### Django Shell Testing

```python
python manage.py shell

from hr_system.gemini_service import get_gemini_generator

# Check if Gemini is available
generator = get_gemini_generator()
print(f"Gemini available: {generator.is_available()}")

# Test question generation
questions = generator.generate_oral_questions(
    jd_text="We need a Python developer...",
    resume_text="Experienced with Django and Flask...",
    candidate_name="Test User",
    experience_level="Mid-level",
    required_skills="Python, Django",
    num_questions=3
)

for q in questions:
    print(f"\nQ: {q['question']}")
    print(f"Focus: {q['focus_area']}")
    print(f"Difficulty: {q['difficulty']}")
```

### Check Database

```python
from hr_system.models import Question

# Count dynamic questions
dynamic_count = Question.objects.filter(is_dynamic=True).count()
print(f"Dynamic questions: {dynamic_count}")

# View a sample
q = Question.objects.filter(is_dynamic=True).first()
if q:
    print(f"\nQuestion: {q.text}")
    print(f"Focus: {q.focus_area}")
    print(f"Difficulty: {q.difficulty}")
    print(f"Metadata: {q.gemini_metadata}")
```

---

## 🔍 Troubleshooting

### Questions seem generic

**Problem:** Questions don't reference specific resume content

**Check:**
1. Is `GEMINI_API_KEY` set in `.env`?
2. Check logs for `[GEMINI]` errors
3. Verify `gemini_metadata.generated_by` is "gemini" not "fallback"

**Solution:**
- Set Gemini API key for AI-powered generation
- Restart backend servers after setting key

### Same questions for different candidates

**This should NEVER happen!**

**If it does:**
1. Check `gemini_metadata.candidate_id` - should be different
2. Check `generated_at` - should be different timestamps
3. Check logs for errors in question generation
4. File a bug report

### Questions not appearing

**Check:**
1. Is `process_tasks` worker running?
2. Check background task logs
3. Verify resume was parsed successfully
4. Check for errors in terminal

**Solution:**
```bash
# Restart background worker
cd backend
python manage.py process_tasks
```

### Gemini API errors

**Common issues:**
- Invalid API key
- Rate limit exceeded
- Network connectivity

**Solution:**
- Verify API key is correct
- Check Gemini API quota
- System will use fallback automatically

---

## 📊 Verification Checklist

### After Uploading a Candidate

- [ ] Resume parsed successfully
- [ ] Interview session created
- [ ] Interview link generated
- [ ] Questions generated (check count)
- [ ] Questions have metadata
- [ ] `is_dynamic = true`
- [ ] Email sent/logged

### After Uploading Multiple Candidates

- [ ] Each has different questions
- [ ] Questions reference their specific skills
- [ ] Different `candidate_id` in metadata
- [ ] Different `generated_at` timestamps
- [ ] Focus areas match their background

### API Response Check

- [ ] Questions array populated
- [ ] Each question has `focus_area`
- [ ] Each question has `difficulty`
- [ ] Each question has `gemini_metadata`
- [ ] Each question has `generated_at`
- [ ] `is_dynamic` is true

---

## 🎯 Success Indicators

**You know it's working when:**

✅ Different candidates get different questions
✅ Questions mention specific technologies from resume
✅ Questions reference JD requirements
✅ Metadata shows `generated_by: "gemini"` (if API key set)
✅ Each question has unique `generated_at` timestamp
✅ Focus areas match candidate's background
✅ Difficulty matches experience level

---

## 📚 Documentation Links

- **Full Documentation:** `DYNAMIC_QUESTION_GENERATION.md`
- **Implementation Details:** `IMPLEMENTATION_SUMMARY.md`
- **Main README:** `README.md`
- **Test Suite:** `backend/test_dynamic_questions.py`

---

## 🆘 Need Help?

1. **Check logs:**
   - Backend: Terminal running `python manage.py runserver`
   - Worker: Terminal running `python manage.py process_tasks`

2. **Run tests:**
   ```bash
   python test_dynamic_questions.py
   ```

3. **Check documentation:**
   - See `DYNAMIC_QUESTION_GENERATION.md` for detailed info

4. **Common commands:**
   ```bash
   # Restart backend
   python manage.py runserver
   
   # Restart worker
   python manage.py process_tasks
   
   # Check migrations
   python manage.py showmigrations
   
   # Django shell
   python manage.py shell
   ```

---

**Last Updated:** February 3, 2026
**System Status:** ✅ Production Ready
