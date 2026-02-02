from django.core.management.base import BaseCommand
from hr_system.models import CodingQuestionBank

class Command(BaseCommand):
    help = 'Seed coding questions'

    def handle(self, *args, **kwargs):
        questions = [
            {
                "text": "Write a function to reverse a string in Python without using built-in reverse functions.",
                "difficulty": "Easy",
                "skills": "Python, Logic",
                "role_type": "Software Engineer"
            },
            {
                "text": "Given a list of integers, find the two numbers that sum up to a target value. Return their indices.",
                "difficulty": "Medium",
                "skills": "Algorithms, Data Structures",
                "role_type": "Software Engineer"
            },
            {
                "text": "Explain the difference between '==' and 'is' in Python and provide a code example.",
                "difficulty": "Easy",
                "skills": "Python, Core",
                "role_type": "Python Developer"
            },
            {
                "text": "Implement a basic LRU cache with get and put operations.",
                "difficulty": "Hard",
                "skills": "System Design, Data Structures",
                "role_type": "Senior Software Engineer"
            }
        ]
        
        for q in questions:
            CodingQuestionBank.objects.get_or_create(
                text=q['text'],
                defaults={
                    'difficulty': q['difficulty'],
                    'skills': q['skills'],
                    'role_type': q['role_type']
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully seeded coding questions'))
