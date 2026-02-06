"""
Gemini AI Service for Dynamic Interview Question Generation

This service handles all Gemini API interactions for generating personalized
interview questions based on candidate resumes and job descriptions.
"""

import os
import json
import google.generativeai as genai
from typing import List, Dict, Any


class GeminiQuestionGenerator:
    """
    Handles dynamic question generation using Gemini API.
    Each candidate receives unique questions based on their resume and the JD.
    """
    
    def __init__(self):
     self.api_key = os.environ.get("GEMINI_API_KEY")


     
     if self.api_key:
        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # 👉 USE NEW MODEL
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    else:
        self.model = None

    def test_connection(self):
    try:
        r = self.model.generate_content("hello")
        return True, r.text
    except Exception as e:
        return False, str(e)



    def is_available(self) -> bool:
        """Check if Gemini API is configured and available"""
        return self.model is not None
    
    def generate_oral_questions(
        self,
        jd_text: str,
        resume_text: str,
        candidate_name: str,
        experience_level: str,
        required_skills: str,
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized oral interview questions.
        
        Args:
            jd_text: Full job description text
            resume_text: Full resume text of the candidate
            candidate_name: Name of the candidate
            experience_level: Expected experience level from JD
            required_skills: Required skills from JD
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries with structure:
            {
                "question": str,
                "focus_area": str,
                "difficulty": str,
                "expected_skills": List[str]
            }
        """
        if not self.is_available():
            return self._fallback_oral_questions(
                candidate_name, resume_text, required_skills, num_questions
            )
        
        prompt = f"""You are an expert technical interviewer conducting a personalized interview.

CANDIDATE INFORMATION:
Name: {candidate_name}
Experience Level Expected: {experience_level}

JOB DESCRIPTION:
{jd_text}

REQUIRED SKILLS FOR THIS ROLE:
{required_skills}

CANDIDATE'S RESUME:
{resume_text}

TASK:
Generate exactly {num_questions} personalized, open-ended oral interview questions that:

1. **Are Based on Real Resume Projects**: Reference specific projects, technologies, or achievements mentioned in the candidate's resume
2. **Test JD Required Skills**: Focus on skills listed in the job description that the candidate claims to have
3. **Match Experience Level**: Difficulty should match the expected experience level ({experience_level})
4. **Avoid Yes/No Questions**: All questions must be open-ended and require detailed explanations
5. **Are Role-Relevant**: Questions must be directly relevant to the job responsibilities
6. **Test Depth**: Go beyond surface-level knowledge to assess true understanding

RULES:
- NO generic template questions
- Each question MUST reference something specific from the resume
- Questions should progressively test deeper understanding
- Include scenario-based questions relevant to the role
- Test both technical knowledge and problem-solving ability

OUTPUT FORMAT (JSON):
Return a valid JSON array with exactly {num_questions} questions in this format:

[
  {{
    "question": "Based on your work with [specific technology from resume] in [specific project], how would you...",
    "focus_area": "Technology/Skill being tested",
    "difficulty": "Easy/Medium/Hard",
    "expected_skills": ["skill1", "skill2"]
  }}
]

Return ONLY the JSON array. No markdown, no explanations, no code blocks."""

        try:
            response = self.model.generate_content(prompt)
            questions_data = self._parse_json_response(response.text)
            
            # Validate and ensure we have the right number of questions
            if isinstance(questions_data, list) and len(questions_data) > 0:
                return questions_data[:num_questions]
            else:
                print(f"[GEMINI] Invalid response format, using fallback")
                return self._fallback_oral_questions(
                    candidate_name, resume_text, required_skills, num_questions
                )
                
        except Exception as e:
            print(f"[GEMINI] Error generating oral questions: {str(e)}")
            return self._fallback_oral_questions(
                candidate_name, resume_text, required_skills, num_questions
            )
    
    def generate_coding_questions(
        self,
        jd_text: str,
        resume_text: str,
        experience_level: str,
        required_skills: str,
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized coding questions.
        
        Args:
            jd_text: Full job description text
            resume_text: Full resume text of the candidate
            experience_level: Expected experience level from JD
            required_skills: Required skills from JD
            num_questions: Number of coding questions to generate
            
        Returns:
            List of coding question dictionaries with structure:
            {
                "problem": str,
                "expected_skills": List[str],
                "input_output_format": str,
                "difficulty": str,
                "focus_area": str
            }
        """
        if not self.is_available():
            return self._fallback_coding_questions(
                resume_text, required_skills, num_questions
            )
        
        prompt = f"""You are an expert technical interviewer creating coding challenges.

JOB DESCRIPTION:
{jd_text}

REQUIRED SKILLS:
{required_skills}

EXPERIENCE LEVEL: {experience_level}

CANDIDATE'S RESUME (for context on their background):
{resume_text}

TASK:
Generate exactly {num_questions} coding problem(s) that:

1. **Test JD Required Skills**: Focus on programming languages and technologies mentioned in the job description
2. **Are Role-Relevant**: Problems should reflect real challenges in this specific role
3. **Match Experience Level**: Difficulty appropriate for {experience_level} level
4. **Are Practical**: Problems should be solvable in 30-60 minutes
5. **Test Problem-Solving**: Not just syntax, but algorithmic thinking and design
6. **Consider Resume Background**: Leverage technologies the candidate claims to know

RULES:
- NO generic LeetCode-style problems unless highly relevant
- Problems must be directly applicable to the job responsibilities
- Include clear input/output specifications
- Provide context on why this problem matters for the role

OUTPUT FORMAT (JSON):
Return a valid JSON array with exactly {num_questions} coding problem(s):

[
  {{
    "problem": "Detailed problem statement with context...",
    "expected_skills": ["skill1", "skill2"],
    "input_output_format": "Input: ... Output: ... Example: ...",
    "difficulty": "Easy/Medium/Hard",
    "focus_area": "What this tests (e.g., 'API Design', 'Data Structures')"
  }}
]

Return ONLY the JSON array. No markdown, no explanations, no code blocks."""

        try:
            response = self.model.generate_content(prompt)
            questions_data = self._parse_json_response(response.text)
            
            if isinstance(questions_data, list) and len(questions_data) > 0:
                return questions_data[:num_questions]
            else:
                print(f"[GEMINI] Invalid response format, using fallback")
                return self._fallback_coding_questions(
                    resume_text, required_skills, num_questions
                )
                
        except Exception as e:
            print(f"[GEMINI] Error generating coding questions: {str(e)}")
            return self._fallback_coding_questions(
                resume_text, required_skills, num_questions
            )
    
    def _parse_json_response(self, response_text: str) -> Any:
        """Parse JSON from Gemini response, handling markdown code blocks"""
        cleaned = response_text.strip()
        
        # Remove markdown code blocks if present
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return json.loads(cleaned.strip())
    
    def _fallback_oral_questions(
        self,
        candidate_name: str,
        resume_text: str,
        required_skills: str,
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """
        Fallback question generation when Gemini is not available.
        Still attempts to be dynamic based on resume content.
        """
        import re
        
        # Detect skills from resume
        detected_skills = []
        keywords = [
            "Python", "Java", "JavaScript", "React", "Node", "Django", 
            "SQL", "AWS", "Docker", "Kubernetes", "Machine Learning",
            "TypeScript", "Angular", "Vue", "MongoDB", "PostgreSQL"
        ]
        
        for kw in keywords:
            if kw.lower() in resume_text.lower():
                detected_skills.append(kw)
        
        skill_str = ", ".join(detected_skills[:3]) if detected_skills else required_skills
        
        questions = []
        templates = [
            {
                "question": f"Hello {candidate_name}, I noticed you have experience with {skill_str}. Can you walk me through a challenging project where you used these technologies and the impact it had?",
                "focus_area": "Project Experience",
                "difficulty": "Medium"
            },
            {
                "question": f"Based on your resume, what was the most complex technical problem you solved using {detected_skills[0] if detected_skills else 'your core skills'}, and how did you approach it?",
                "focus_area": "Problem Solving",
                "difficulty": "Medium"
            },
            {
                "question": f"How would you design a scalable solution using {skill_str} for a high-traffic application? Walk me through your architecture decisions.",
                "focus_area": "System Design",
                "difficulty": "Hard"
            },
            {
                "question": f"Tell me about a time when you had to learn a new technology quickly. How did you approach it, and how does that relate to your experience with {skill_str}?",
                "focus_area": "Learning Agility",
                "difficulty": "Easy"
            },
            {
                "question": f"Looking at your background with {skill_str}, how would you optimize the performance of a slow-running application in a production environment?",
                "focus_area": "Performance Optimization",
                "difficulty": "Hard"
            }
        ]
        
        for i in range(min(num_questions, len(templates))):
            questions.append({
                **templates[i],
                "expected_skills": detected_skills[:3] if detected_skills else [required_skills]
            })
        
        # If we need more questions than templates, repeat with variations
        while len(questions) < num_questions:
            questions.append({
                "question": f"Can you describe how your experience with {skill_str} prepares you for the challenges in this role?",
                "focus_area": "Role Fit",
                "difficulty": "Medium",
                "expected_skills": detected_skills[:3] if detected_skills else [required_skills]
            })
        
        return questions[:num_questions]
    
    def _fallback_coding_questions(
        self,
        resume_text: str,
        required_skills: str,
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """
        Fallback coding question generation when Gemini is not available.
        """
        # Detect primary language from resume
        languages = ["Python", "Java", "JavaScript", "C++", "Go", "Ruby"]
        detected_lang = "Python"  # default
        
        for lang in languages:
            if lang.lower() in resume_text.lower():
                detected_lang = lang
                break
        
        questions = [
            {
                "problem": f"Design and implement a REST API endpoint that handles user authentication. The solution should include input validation, error handling, and return appropriate HTTP status codes. Use {detected_lang} and demonstrate best practices for API design.",
                "expected_skills": [detected_lang, "API Design", "Authentication"],
                "input_output_format": "Input: User credentials (username, password). Output: JWT token or error message. Example: POST /api/auth/login with JSON body.",
                "difficulty": "Medium",
                "focus_area": "API Development"
            },
            {
                "problem": f"Implement a function that processes a large dataset efficiently. Given a list of user transactions, find the top 10 users by total transaction amount. Optimize for both time and space complexity. Implement in {detected_lang}.",
                "expected_skills": [detected_lang, "Data Structures", "Algorithms"],
                "input_output_format": "Input: List of transactions [{user_id, amount}]. Output: List of top 10 users with total amounts. Example: [{user_id: 1, total: 5000}]",
                "difficulty": "Medium",
                "focus_area": "Data Processing"
            }
        ]
        
        return questions[:num_questions]


# Singleton instance
_gemini_generator = None

def get_gemini_generator() -> GeminiQuestionGenerator:
    """Get or create the Gemini question generator singleton"""
    global _gemini_generator
    if _gemini_generator is None:
        _gemini_generator = GeminiQuestionGenerator()
    return _gemini_generator
