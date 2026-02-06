"""
Test script to verify dynamic question generation is working correctly.

This script tests:
1. Gemini service availability
2. Question generation for sample candidates
3. Uniqueness of questions between candidates
4. Metadata tracking
"""

import os
import sys

# >>> ADD THIS <<<
from dotenv import load_dotenv
load_dotenv()

import django


# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from hr_system.models import Job, Candidate, InterviewSession, Question
from hr_system.gemini_service import get_gemini_generator
from hr_system.tasks import generate_oral_questions, generate_coding_questions


def test_gemini_availability():
    """Test if Gemini API is configured and available"""
    print("\n" + "="*60)
    print("TEST 1: Gemini Service Availability")
    print("="*60)
    
    generator = get_gemini_generator()
    is_available = generator.is_available()
    
    print(f"Gemini API Key Set: {'Yes' if os.environ.get('GEMINI_API_KEY') else 'No'}")
    print(f"Gemini Service Available: {'Yes' if is_available else 'No (will use fallback)'}")
print("RAW KEY VALUE:", repr(os.environ.get("GEMINI_API_KEY")))

    
    if is_available:
        print("✅ Gemini is configured and ready for dynamic generation")
    else:
        print("⚠️  Gemini not available - will use intelligent fallback")
    
    return is_available


def test_question_generation():
    """Test question generation with sample data"""
    print("\n" + "="*60)
    print("TEST 2: Question Generation")
    print("="*60)
    
    generator = get_gemini_generator()
    
    # Sample data
    jd_text = """
    We are looking for a Senior Python Developer with experience in Django and REST APIs.
    The ideal candidate should have:
    - 5+ years of Python development experience
    - Strong knowledge of Django framework
    - Experience with PostgreSQL and Redis
    - Understanding of microservices architecture
    - Experience with AWS cloud services
    """
    
    resume_text = """
    John Doe
    Senior Software Engineer
    
    Experience:
    - Built a high-traffic e-commerce platform using Django and PostgreSQL
    - Implemented microservices architecture with Docker and Kubernetes
    - Developed REST APIs serving 1M+ requests per day
    - Optimized database queries reducing response time by 60%
    
    Skills: Python, Django, PostgreSQL, Redis, Docker, AWS, REST APIs
    """
    
    print("\nGenerating 3 oral questions...")
    oral_questions = generator.generate_oral_questions(
        jd_text=jd_text,
        resume_text=resume_text,
        candidate_name="John Doe",
        experience_level="Senior",
        required_skills="Python, Django, PostgreSQL, Redis, AWS",
        num_questions=3
    )
    
    print(f"\n✅ Generated {len(oral_questions)} oral questions:")
    for i, q in enumerate(oral_questions, 1):
        print(f"\n  Question {i}:")
        print(f"  Text: {q.get('question', 'N/A')[:100]}...")
        print(f"  Focus Area: {q.get('focus_area', 'N/A')}")
        print(f"  Difficulty: {q.get('difficulty', 'N/A')}")
        print(f"  Skills: {q.get('expected_skills', 'N/A')}")
    
    print("\nGenerating 1 coding question...")
    coding_questions = generator.generate_coding_questions(
        jd_text=jd_text,
        resume_text=resume_text,
        experience_level="Senior",
        required_skills="Python, Django, PostgreSQL, Redis, AWS",
        num_questions=1
    )
    
    print(f"\n✅ Generated {len(coding_questions)} coding question:")
    for i, q in enumerate(coding_questions, 1):
        print(f"\n  Coding Problem {i}:")
        print(f"  Problem: {q.get('problem', 'N/A')[:150]}...")
        print(f"  Focus Area: {q.get('focus_area', 'N/A')}")
        print(f"  Difficulty: {q.get('difficulty', 'N/A')}")
        print(f"  Skills: {q.get('expected_skills', 'N/A')}")


def test_uniqueness():
    """Test that different candidates get different questions"""
    print("\n" + "="*60)
    print("TEST 3: Question Uniqueness Between Candidates")
    print("="*60)
    
    generator = get_gemini_generator()
    
    jd_text = "Looking for a Full Stack Developer with React and Node.js experience."
    
    # Candidate 1: React specialist
    resume1 = """
    Jane Smith
    Frontend Developer
    
    Built 5+ React applications with Redux and TypeScript.
    Experience with React Hooks, Context API, and performance optimization.
    Skills: React, TypeScript, Redux, CSS, HTML
    """
    
    # Candidate 2: Node.js specialist
    resume2 = """
    Bob Johnson
    Backend Developer
    
    Developed scalable Node.js APIs with Express and MongoDB.
    Experience with microservices, Docker, and AWS Lambda.
    Skills: Node.js, Express, MongoDB, Docker, AWS
    """
    
    print("\nGenerating questions for Candidate 1 (React specialist)...")
    questions1 = generator.generate_oral_questions(
        jd_text=jd_text,
        resume_text=resume1,
        candidate_name="Jane Smith",
        experience_level="Mid-level",
        required_skills="React, Node.js",
        num_questions=2
    )
    
    print("\nGenerating questions for Candidate 2 (Node.js specialist)...")
    questions2 = generator.generate_oral_questions(
        jd_text=jd_text,
        resume_text=resume2,
        candidate_name="Bob Johnson",
        experience_level="Mid-level",
        required_skills="React, Node.js",
        num_questions=2
    )
    
    print("\n📊 Comparison:")
    print("\nCandidate 1 Questions:")
    for i, q in enumerate(questions1, 1):
        print(f"  {i}. {q.get('question', 'N/A')[:80]}...")
    
    print("\nCandidate 2 Questions:")
    for i, q in enumerate(questions2, 1):
        print(f"  {i}. {q.get('question', 'N/A')[:80]}...")
    
    # Check if questions are different
    q1_texts = [q.get('question', '') for q in questions1]
    q2_texts = [q.get('question', '') for q in questions2]
    
    are_different = not any(q1 == q2 for q1 in q1_texts for q2 in q2_texts)
    
    if are_different:
        print("\n✅ Questions are UNIQUE between candidates")
    else:
        print("\n⚠️  Some questions are identical (may happen with fallback)")


def test_database_integration():
    """Test that questions are properly stored in database with metadata"""
    print("\n" + "="*60)
    print("TEST 4: Database Integration & Metadata")
    print("="*60)
    
    # Check if there are any questions in the database
    total_questions = Question.objects.count()
    dynamic_questions = Question.objects.filter(is_dynamic=True).count()
    
    print(f"\nTotal questions in database: {total_questions}")
    print(f"Dynamic questions: {dynamic_questions}")
    
    if dynamic_questions > 0:
        print("\n✅ Dynamic questions found in database")
        
        # Show sample question with metadata
        sample = Question.objects.filter(is_dynamic=True).first()
        if sample:
            print(f"\nSample Dynamic Question:")
            print(f"  Text: {sample.text[:100]}...")
            print(f"  Type: {sample.question_type}")
            print(f"  Focus Area: {sample.focus_area}")
            print(f"  Difficulty: {sample.difficulty}")
            print(f"  Generated At: {sample.generated_at}")
            print(f"  Metadata: {sample.gemini_metadata}")
    else:
        print("\n⚠️  No dynamic questions in database yet")
        print("   Upload a candidate to trigger question generation")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("DYNAMIC QUESTION GENERATION - TEST SUITE")
    print("="*60)
    
    try:
        # Test 1: Check Gemini availability
        gemini_available = test_gemini_availability()
        
        # Test 2: Test question generation
        test_question_generation()
        
        # Test 3: Test uniqueness
        test_uniqueness()
        
        # Test 4: Test database integration
        test_database_integration()
        
        print("\n" + "="*60)
        print("TEST SUITE COMPLETED")
        print("="*60)
        
        if gemini_available:
            print("\n✅ All systems operational with Gemini AI")
        else:
            print("\n⚠️  Running with fallback generation (set GEMINI_API_KEY for full AI)")
        
        print("\nNext steps:")
        print("1. Upload a candidate through the UI")
        print("2. Check the generated questions via API: GET /api/candidates/{id}/detail/")
        print("3. Verify questions are unique and personalized")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
