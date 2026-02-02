import os
import uuid
from datetime import timedelta
from django.utils import timezone
from background_task import background
from .models import Candidate, Resume, InterviewSession, InterviewLink, Question, EmailLog, CodingQuestionBank, Job
from pypdf import PdfReader
import google.generativeai as genai
from django.conf import settings
from django.core.mail import send_mail

# Configure Gemini
# genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@background(schedule=0)
def process_candidate_task(candidate_id):
    try:
        print(f"--- [TASK] Starting processing for Candidate ID: {candidate_id} ---")
        candidate = Candidate.objects.get(id=candidate_id)
        job = candidate.job

        # 1. Parse Resume (Non-AI)
        resume_text = ""
        if candidate.resume_file:
            try:
                reader = PdfReader(candidate.resume_file.path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        resume_text += text
                if not resume_text.strip():
                    resume_text = f"Warning: PDF file uploaded ({candidate.resume_file.name}) but no text could be extracted."
            except Exception as e:
                resume_text = f"Error parsing uploaded PDF ({candidate.resume_file.name}): {str(e)}"
        elif candidate.resume_url:
            try:
                import requests
                from bs4 import BeautifulSoup
                
                # Normalize Google Sheets URLs
                final_url = candidate.resume_url
                if "docs.google.com/spreadsheets" in final_url and "pubhtml" in final_url:
                    # Convert pubhtml to pub?output=csv
                    import re
                    # Remove /u/1/ or similar if present
                    final_url = re.sub(r'/u/\d+/', '/', final_url)
                    final_url = final_url.replace("/pubhtml", "/pub?output=csv")
                    print(f"--- [TASK] Normalized Google Sheets URL to: {final_url} ---")

                # Fetch content from URL
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                print(f"--- [TASK] Fetching URL: {final_url} ---")
                response = requests.get(final_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    if 'text/csv' in content_type or final_url.endswith('csv') or 'output=csv' in final_url:
                        # Parse as CSV
                        import csv
                        from io import StringIO
                        f = StringIO(response.text)
                        reader = csv.reader(f)
                        data_rows = [", ".join(row) for row in reader if any(row)]
                        fetched_text = "\n".join(data_rows)
                        print(f"--- [TASK] Parsed as CSV: {len(data_rows)} rows ---")
                    else:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # 1. Try Meta Description (Google Sheets often puts summary here)
                        meta_desc = soup.find('meta', attrs={"property": "og:description"}) or soup.find('meta', attrs={"name": "description"})
                        meta_content = meta_desc['content'] if meta_desc and meta_desc.has_attr('content') else ""
                        
                        # 2. Try Tables (Ritz tables in Sheets)
                        rows = []
                        for row in soup.find_all('tr'):
                            cols = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                            if any(cols):
                                rows.append(" | ".join(cols))
                        
                        table_content = "\n".join(rows) if rows else ""
                        
                        # Combine or prioritize
                        fetched_text = f"{meta_content}\n\n{table_content}".strip()
                        if not fetched_text:
                            fetched_text = soup.get_text(separator=' ', strip=True)
                    
                    print(f"--- [TASK] Successfully fetched {len(fetched_text)} chars from URL ---")
                    resume_text = f"Resume Source: External Link ({candidate.resume_url})\n\n--- FETCHED CONTENT ---\n{fetched_text}"
                else:
                    print(f"--- [TASK] URL Fetch FAILED with Status: {response.status_code} ---")
                    resume_text = f"Resume Source: External Link ({candidate.resume_url})\n\n[ERROR]: Could not fetch content (Status: {response.status_code})"
            except Exception as e:
                resume_text = f"Resume Source: External Link ({candidate.resume_url})\n\n[ERROR]: Failed to fetch/parse URL content: {str(e)}"
        else:
            resume_text = "No resume provided. Questions generated based on Job Description only."
        
        # 2. Extract Metadata (AI)
        metadata = extract_resume_metadata(resume_text, candidate)
        
        # Avoid creating duplicates if task is retried
        Resume.objects.update_or_create(
            candidate=candidate, 
            defaults={
                'raw_text': resume_text,
                'extracted_metadata': metadata
            }
        )

        # 3. Create Interview Session with Snapshot
        session, created = InterviewSession.objects.get_or_create(
            candidate=candidate,
            defaults={
                'oral_question_count': job.oral_question_count,
                'coding_question_count': job.coding_question_count,
                'thinking_time': job.thinking_time,
                'recording_time': job.recording_time,
                'coding_time': job.coding_time
            }
        )

        # 3. Generate Interview Link
        expiry_date = timezone.now() + timedelta(days=7)
        link, created = InterviewLink.objects.get_or_create(
            session=session,
            defaults={
                'token': str(uuid.uuid4()),
                'expires_at': expiry_date
            }
        )

        # 4. Generate Oral Questions (Gemini)
        if not session.questions.filter(question_type='ORAL').exists():
            generate_oral_questions(session, job.description, resume_text)

        # 5. Select Coding Questions (From Bank)
        if not session.questions.filter(question_type='CODING').exists():
            select_coding_questions(session, job)

        # 6. Email Link
        send_interview_email_task(candidate.id, link.token)

    except Exception as e:
        print(f"Error processing candidate {candidate_id}: {str(e)}")

def generate_oral_questions(session, jd_text, resume_text):
    """
    Uses Gemini to generate oral questions based on JD and Resume.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("--- [TASK] No Gemini API Key found. Using Smart Fallback for questions. ---")
        # Try to get skills from resume_text
        detected_skills = []
        keywords = ["Python", "Java", "JavaScript", "React", "Node", "Django", "SQL", "AWS", "Docker", "Machine Learning"]
        for kw in keywords:
            if kw.lower() in resume_text.lower():
                detected_skills.append(kw)
        
        skill_str = ", ".join(detected_skills) if detected_skills else "your technical background"
        
        for i in range(session.oral_question_count):
            if i == 0:
                q_text = f"Hello {session.candidate.name}, can you describe your experience with {skill_str} as it relates to this role?"
            elif i == 1:
                q_text = f"Based on your resume, what was the most challenging project you worked on using {detected_skills[0] if detected_skills else 'your core skills'}?"
            else:
                q_text = f"How would you apply your knowledge of {skill_str} to solve complex problems in a fast-paced environment?"

            Question.objects.create(
                session=session,
                text=q_text,
                question_type='ORAL',
                expected_skills=skill_str,
                time_limit=session.thinking_time * 60,
                order=i
            )
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    You are an expert technical interviewer. I will provide you with a Job Description (JD) and a Candidate's Resume (Raw Text).
    Your goal is to generate {session.oral_question_count} high-quality, open-ended interview questions that:
    1.  **Validate Experience**: Ask specifically about projects or achievements mentioned in the resume as they relate to the JD.
    2.  **Test Technical Depth**: Explore the candidate's understanding of key technologies listed in the JD that are also present in their resume.
    3.  **Scenario Based**: Present a challenge likely to be encountered in this specific role and ask how they would solve it.

    Job Description:
    {jd_text}
    
    Candidate Resume (Raw Text):
    {resume_text}
    
    Output format:
    Provide only the questions, one per line. No introduction or labels.
    """
    
    try:
        response = model.generate_content(prompt)
        questions = response.text.strip().split('\n')
        # Filter out empty lines or labels
        questions = [q.strip() for q in questions if q.strip() and not q.strip().lower().startswith('question')]
        
        for i, q_text in enumerate(questions[:session.oral_question_count]):
            # If AI returns fewer questions, we might need a fallback or just accept it
            Question.objects.create(
                session=session,
                text=q_text,
                question_type='ORAL',
                expected_skills=f"Tailored to {session.candidate.job.title}",
                time_limit=session.thinking_time * 60,
                order=i
            )
    except Exception as e:
        print(f"Gemini Error: {str(e)}")
        # Fallback to smart logic if AI fails even with key
        for i in range(session.oral_question_count):
            Question.objects.create(
                session=session,
                text=f"Regarding the {session.candidate.job.title} role, how do your previous experiences prepare you for its key responsibilities?",
                question_type='ORAL',
                expected_skills="Core Competencies",
                time_limit=session.thinking_time * 60,
                order=i
            )

def select_coding_questions(session, job):
    """
    Selects coding questions from the predefined bank.
    """
    # Simple selection logic: filter by role type or difficulty if available
    bank_questions = CodingQuestionBank.objects.filter(role_type=job.title).order_by('?')[:session.coding_question_count]
    if not bank_questions.exists():
        bank_questions = CodingQuestionBank.objects.all().order_by('?')[:session.coding_question_count]
        
    for i, bq in enumerate(bank_questions):
        Question.objects.create(
            session=session,
            text=bq.text,
            question_type='CODING',
            expected_skills=bq.skills,
            time_limit=session.coding_time,
            order=session.oral_question_count + i
        )

def extract_resume_metadata(resume_text, candidate):
    """
    Uses Gemini to extract structured metadata from the resume text.
    If no API key, uses a smart regex-based fallback to avoid "static" data.
    """
    import re
    
    def smart_fallback(text, candidate):
        metadata = {
            "full_name": candidate.name or "Unknown",
            "email": candidate.email or "Unknown",
            "top_skills": [],
            "experience_years": 0,
            "summary": "Auto-generated summary from raw text.",
            "education": "Not Provided",
            "parsing_status": "Dynamic Fallback (Gemini API Key Missing)"
        }
        
        # 1. Refine Email if unknown
        if metadata["email"] == "Unknown":
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
            if emails:
                metadata["email"] = emails[0]
            
        # 2. Skill Detection
        keywords = ["Python", "Java", "JavaScript", "React", "Node", "Django", "SQL", "AWS", "Docker", "Machine Learning", "CSV", "Excel"]
        for kw in keywords:
            if kw.lower() in text.lower():
                metadata["top_skills"].append(kw)
        
        # 3. Experience Detection
        exp_match = re.search(r'(\d+)\+?\s*(years|yrs)\s*(exp|experience)', text, re.I)
        if exp_match:
            try:
                metadata["experience_years"] = int(exp_match.group(1))
            except:
                metadata["experience_years"] = 1
        
        return metadata

    api_key = os.environ.get("GEMINI_API_KEY")
    # Pass candidate object to fallback
    if not api_key:
        return smart_fallback(resume_text, candidate)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Act as a professional HR Data Parser. I will provide you with raw text extracted from a candidate's resume (which may be from a PDF or a CSV table). 

    Your task:
    1. Extract the following information into a valid JSON object.
    2. If a field is missing, use "Not Provided".
    3. For 'top_skills', create a list of the 5 most relevant technical skills.
    4. For 'experience_years', provide a single integer (e.g., 5). If it's a range, take the highest number.

    JSON Schema:
    {{
      "full_name": "string",
      "email": "string",
      "top_skills": ["skill1", "skill2"],
      "experience_years": integer,
      "summary": "A 2-sentence professional overview",
      "education": "Highest degree and institution"
    }}

    Raw Resume Text:
    ---
    {resume_text}
    ---

    Return ONLY the JSON object. Do not include any introductory text or markdown code blocks.
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip()
        # Remove markdown code blocks if present
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
            
        import json
        return json.loads(cleaned_response.strip())
    except Exception as e:
        print(f"Metadata Extraction Error: {str(e)}")
        return smart_fallback(resume_text, candidate)

@background(schedule=0)
def send_interview_email_task(candidate_id, token):
    try:
        candidate = Candidate.objects.get(id=candidate_id)
        email_log = EmailLog.objects.create(candidate=candidate)
        
        interview_url = f"{settings.FRONTEND_URL}/interview/{token}"
        
        subject = f"Interview Invitation for {candidate.job.title}"
        message = f"Hello {candidate.name},\n\nYou have been invited for an initial screening interview.\n\nPlease use the following link to start your interview: {interview_url}\n\nThis link is for single-use and will expire in 7 days."
        
        try:
            # send_mail(subject, message, settings.EMAIL_HOST_USER, [candidate.email])
            print(f"MOCK EMAIL SENT TO {candidate.email}: {interview_url}")
            email_log.status = 'SENT'
            email_log.sent_at = timezone.now()
            email_log.save()
        except Exception as e:
            email_log.status = 'FAILED'
            email_log.last_error = str(e)
            email_log.save()
            # Retry logic could be added here or via background task retry settings
            
    except Exception as e:
        print(f"Error sending email: {str(e)}")
