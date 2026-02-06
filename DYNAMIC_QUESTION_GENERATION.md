# Dynamic Interview Question Generation System

## Overview

This system generates **FULLY DYNAMIC** interview questions for each candidate using Google's Gemini AI. Every candidate receives unique, personalized questions based on:

- Their parsed resume content
- The Job Description (JD)
- Their experience level
- Required skills for the role
- Interview configuration (number of questions, time limits)

**IMPORTANT**: No static question bank is used. All questions are generated on-demand per candidate.

---

## Core Behavior

### 1. Question Generation Trigger

Questions are generated when:
- Interview session is created during candidate processing
- The `process_candidate_task` background task runs
- This happens automatically after HR uploads a candidate

### 2. Unique Questions Per Candidate

Each candidate receives:
- **Oral Questions**: Personalized based on their resume projects and JD requirements
- **Coding Questions**: Role-specific problems matching their skill level and background

### 3. No Question Reuse

- Questions are NOT pre-stored
- Questions are NOT reused between candidates
- Every candidate = new Gemini API call
- Questions are stored ONLY for that specific candidate's session

---

## Technical Architecture

### Components

1. **`gemini_service.py`** - Core AI service for question generation
   - `GeminiQuestionGenerator` class
   - Handles Gemini API interactions
   - Provides intelligent fallbacks when API is unavailable

2. **`tasks.py`** - Background task processing
   - `process_candidate_task()` - Main orchestration
   - `generate_oral_questions()` - Oral question generation
   - `generate_coding_questions()` - Coding question generation

3. **`models.py`** - Database schema
   - `Question` model with dynamic generation metadata
   - Tracks: `focus_area`, `difficulty`, `gemini_metadata`, `generated_at`, `is_dynamic`

---

## Question Generation Flow

```
1. HR uploads JD and resumes
   ↓
2. System parses resumes (NON-AI text extraction)
   ↓
3. InterviewSession is created
   ↓
4. InterviewLink is generated
   ↓
5. Background task triggers question generation:
   
   FOR EACH CANDIDATE:
   ├── Extract resume text
   ├── Get JD text
   ├── Get interview config (num questions, time limits)
   ├── Call Gemini API with:
   │   ├── Full resume text
   │   ├── Full JD text
   │   ├── Experience level
   │   ├── Required skills
   │   └── Number of questions needed
   ├── Gemini returns JSON with personalized questions
   └── Store questions in database with metadata
   
6. Candidate receives interview link
   ↓
7. Questions are displayed during interview
```

---

## Gemini Prompt Strategy

### Oral Questions Prompt

The system sends to Gemini:

**INPUT:**
- Job Description (full text)
- Resume (full text)
- Candidate name
- Experience level
- Required skills
- Number of questions

**PROMPT RULES:**
- Questions MUST reference specific resume projects
- Questions MUST test JD required skills
- NO yes/no questions
- Match candidate experience level
- Avoid generic templates
- Test depth, not just surface knowledge

**OUTPUT FORMAT:**
```json
[
  {
    "question": "Based on your work with [specific tech] in [project]...",
    "focus_area": "Technology/Skill being tested",
    "difficulty": "Easy/Medium/Hard",
    "expected_skills": ["skill1", "skill2"]
  }
]
```

### Coding Questions Prompt

**INPUT:**
- Job Description
- Resume (for context on candidate's background)
- Experience level
- Required skills
- Number of coding problems

**PROMPT RULES:**
- Problems MUST be role-relevant
- Test JD required programming languages
- Match experience level difficulty
- Solvable in 30-60 minutes
- Practical, not generic LeetCode problems
- Consider candidate's claimed technologies

**OUTPUT FORMAT:**
```json
[
  {
    "problem": "Detailed problem statement...",
    "expected_skills": ["skill1", "skill2"],
    "input_output_format": "Input: ... Output: ... Example: ...",
    "difficulty": "Easy/Medium/Hard",
    "focus_area": "What this tests (e.g., 'API Design')"
  }
]
```

---

## Database Schema Changes

### Question Model (Updated)

```python
class Question(models.Model):
    # Existing fields
    session = ForeignKey(InterviewSession)
    text = TextField()
    question_type = CharField()  # 'ORAL' or 'CODING'
    expected_skills = TextField()
    time_limit = IntegerField()
    order = IntegerField()
    
    # NEW: Dynamic Generation Metadata
    focus_area = CharField()           # What skill/area this tests
    difficulty = CharField()           # Easy/Medium/Hard
    gemini_metadata = JSONField()      # Full generation context
    generated_at = DateTimeField()     # When generated
    is_dynamic = BooleanField()        # True for all new questions
```

### Gemini Metadata Structure

```json
{
  "generated_by": "gemini" | "fallback",
  "candidate_id": 123,
  "job_id": 456,
  "generation_timestamp": "2026-02-03T15:30:00",
  "resume_based": true,
  "jd_based": true,
  "problem_type": "coding_challenge"  // for coding questions
}
```

---

## HR Dashboard Impact

### What HR Can See

1. **Questions Generated for Each Candidate**
   - View exact questions asked to that candidate
   - See question metadata (focus area, difficulty)
   - Verify questions are JD + resume specific

2. **Proof of Personalization**
   - `gemini_metadata` shows generation context
   - `generated_at` timestamp proves uniqueness
   - `focus_area` shows what was being tested

3. **Evaluation Tied to Questions**
   - Each answer is linked to its specific question
   - Evaluation considers the exact questions asked
   - No confusion from question reuse

### API Response Example

```json
{
  "candidate": {
    "name": "John Doe",
    "email": "john@example.com"
  },
  "questions": [
    {
      "id": 1,
      "text": "I noticed in your resume you built a real-time chat application using WebSockets and Redis. Can you walk me through the architecture decisions you made for handling 10,000+ concurrent connections?",
      "question_type": "ORAL",
      "focus_area": "System Architecture",
      "difficulty": "Hard",
      "expected_skills": "WebSockets, Redis, Scalability",
      "generated_at": "2026-02-03T15:30:45Z",
      "is_dynamic": true,
      "gemini_metadata": {
        "generated_by": "gemini",
        "candidate_id": 123,
        "job_id": 456,
        "resume_based": true,
        "jd_based": true
      }
    }
  ]
}
```

---

## Fallback Behavior

### When Gemini API is Unavailable

If `GEMINI_API_KEY` is not set or API fails:

1. **Intelligent Fallback** (NOT static templates)
   - Scans resume for mentioned technologies
   - Detects skills from resume text
   - Generates questions referencing detected skills
   - Still personalized, just not AI-powered

2. **Fallback Oral Questions**
   - Reference candidate's name
   - Mention detected skills from resume
   - Ask about specific technologies found in resume
   - Progressive difficulty

3. **Fallback Coding Questions**
   - Detect primary programming language from resume
   - Generate role-relevant problems
   - Use candidate's claimed tech stack

**Metadata marks fallback:**
```json
{
  "generated_by": "fallback",
  "candidate_id": 123,
  ...
}
```

---

## Configuration

### Environment Variables

```env
# Required for AI-powered generation
GEMINI_API_KEY=your-gemini-api-key

# Optional: System will use intelligent fallback if not set
```

### Getting Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` file in backend directory

---

## Important Constraints

### What This System Does NOT Do

❌ Use static question bank  
❌ Generate questions before resume parsing  
❌ Reuse questions between candidates  
❌ Store pre-generated questions  
❌ Use generic template questions (when Gemini is available)

### What This System DOES

✅ Generate unique questions per candidate  
✅ Base questions on actual resume content  
✅ Test JD required skills specifically  
✅ Match candidate experience level  
✅ Provide full generation metadata  
✅ Work with or without Gemini API key  

---

## Testing the System

### Verify Dynamic Generation

1. **Upload two candidates with different resumes**
   ```
   Candidate A: Python, Django, PostgreSQL
   Candidate B: Java, Spring Boot, MySQL
   ```

2. **Check their questions via API**
   ```bash
   GET /api/candidates/{candidate_a_id}/detail/
   GET /api/candidates/{candidate_b_id}/detail/
   ```

3. **Verify:**
   - Questions are different
   - Questions reference their specific skills
   - `gemini_metadata.candidate_id` is different
   - `generated_at` timestamps are different

### Check Gemini Integration

```python
# In Django shell
from hr_system.gemini_service import get_gemini_generator

generator = get_gemini_generator()
print(f"Gemini available: {generator.is_available()}")

# Test generation
questions = generator.generate_oral_questions(
    jd_text="Looking for a Python developer...",
    resume_text="Experienced with Django, Flask...",
    candidate_name="Test User",
    experience_level="Mid-level",
    required_skills="Python, Django, REST APIs",
    num_questions=3
)

print(questions)
```

---

## Monitoring & Debugging

### Check Question Generation Logs

```bash
# In terminal running process_tasks
# Look for:
[DYNAMIC GENERATION] Generating 5 oral questions for John Doe
[DYNAMIC GENERATION] Successfully created 5 oral questions
[DYNAMIC GENERATION] Generating 2 coding questions for John Doe
[DYNAMIC GENERATION] Successfully created 2 coding questions
```

### Database Queries

```python
# Check if questions are dynamic
from hr_system.models import Question

dynamic_questions = Question.objects.filter(is_dynamic=True)
print(f"Dynamic questions: {dynamic_questions.count()}")

# Check generation metadata
for q in Question.objects.filter(session__candidate__name="John Doe"):
    print(f"Q: {q.text[:50]}...")
    print(f"Focus: {q.focus_area}")
    print(f"Difficulty: {q.difficulty}")
    print(f"Generated: {q.generated_at}")
    print(f"Metadata: {q.gemini_metadata}")
    print("---")
```

---

## API Endpoints

### Get Candidate Questions

```
GET /api/candidates/{id}/detail/
```

**Response:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "resume_text": "Full resume text...",
  "questions": [
    {
      "id": 1,
      "text": "Question text...",
      "question_type": "ORAL",
      "focus_area": "System Design",
      "difficulty": "Medium",
      "expected_skills": "Python, Django",
      "generated_at": "2026-02-03T15:30:00Z",
      "is_dynamic": true,
      "gemini_metadata": {...}
    }
  ],
  "evaluation": {...},
  "cheating_logs": [...]
}
```

---

## Migration Guide

### From Old System to New System

1. **Existing questions remain unchanged**
   - Old questions have `is_dynamic=False` (default for existing rows)
   - New questions have `is_dynamic=True`

2. **CodingQuestionBank is now unused**
   - Model still exists for backward compatibility
   - No longer queried for new interviews
   - Can be removed in future cleanup

3. **All new candidates get dynamic questions**
   - Automatic from the moment system is deployed
   - No manual intervention needed

---

## Troubleshooting

### Issue: Questions are generic/not personalized

**Check:**
1. Is `GEMINI_API_KEY` set in `.env`?
2. Check logs for `[GEMINI]` errors
3. Verify `gemini_metadata.generated_by` is "gemini" not "fallback"

**Solution:**
- Set valid Gemini API key
- Check API quota/limits
- Verify internet connectivity

### Issue: Questions not appearing

**Check:**
1. Is `process_tasks` worker running?
2. Check background task logs
3. Verify resume was parsed successfully

**Solution:**
```bash
# Restart background worker
python manage.py process_tasks
```

### Issue: Same questions for different candidates

**This should NEVER happen with this system.**

**If it does:**
1. Check `gemini_metadata.candidate_id` - should be different
2. Check `generated_at` timestamps - should be different
3. File a bug report - this indicates a serious issue

---

## Performance Considerations

### API Call Timing

- **Oral Questions**: ~3-5 seconds per candidate
- **Coding Questions**: ~3-5 seconds per candidate
- **Total**: ~6-10 seconds per candidate for question generation

### Optimization

- Questions generated in background task (non-blocking)
- Candidate receives email only after questions are ready
- HR sees "Processing..." status during generation

### Rate Limits

- Gemini API has rate limits
- For bulk uploads, questions generate sequentially
- Consider implementing rate limiting for very large batches

---

## Future Enhancements

### Potential Improvements

1. **Question Difficulty Adjustment**
   - Adjust difficulty based on candidate's resume strength
   - More experienced = harder questions

2. **Multi-Language Support**
   - Generate questions in candidate's preferred language
   - Detect language from resume

3. **Question Versioning**
   - Track if questions are regenerated
   - Allow HR to manually trigger regeneration

4. **Analytics**
   - Track which focus areas are most common
   - Analyze question difficulty distribution
   - Measure candidate performance by question type

---

## Security & Privacy

### Data Handling

- Resume text sent to Gemini API for question generation
- Gemini does NOT store data (per Google's policy)
- Questions stored in local database
- No PII sent except what's in resume

### Compliance

- Ensure GDPR compliance for resume data
- Candidate consent for AI processing
- Data retention policies apply to questions

---

## Summary

This system ensures:

✅ **Every candidate gets unique questions**  
✅ **Questions are based on their actual resume**  
✅ **Questions test JD-specific requirements**  
✅ **Full transparency via metadata**  
✅ **Works with or without AI (fallback)**  
✅ **No static question bank dependency**  

The system is production-ready and fully implements the dynamic question generation requirement.
