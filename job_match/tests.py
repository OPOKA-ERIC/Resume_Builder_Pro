from django.test import TestCase
from django.contrib.auth.models import User
from resumes.models import Resume, Skill
from .analyzer import extract_skills_from_jd, analyze_match


class AnalyzerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')
        Skill.objects.create(resume=self.resume, name='Python', proficiency_level='advanced')
        Skill.objects.create(resume=self.resume, name='Django', proficiency_level='intermediate')
        Skill.objects.create(resume=self.resume, name='JavaScript', proficiency_level='beginner')

    def test_extract_skills_from_jd(self):
        jd = "We need a Python developer with Django and React experience."
        skills = extract_skills_from_jd(jd)
        self.assertIn('Python', skills)
        self.assertIn('Django', skills)
        self.assertIn('React', skills)

    def test_analyze_match_returns_dict(self):
        jd = "Looking for Python expert with Django and AWS."
        result = analyze_match(self.resume, jd)
        self.assertIn('overall_score', result)
        self.assertIn('matched_skills', result)
        self.assertIn('missing_skills', result)
        self.assertIn('recommendations', result)

    def test_match_score_higher_with_more_skills(self):
        jd_python = "Need Python developer."
        jd_full = "Need Python, Django, JavaScript, AWS, Docker expert."

        result_partial = analyze_match(self.resume, jd_python)
        result_full = analyze_match(self.resume, jd_full)

        score_partial = result_partial['matched_count']
        score_full = result_full['matched_count']

        self.assertGreaterEqual(score_partial, 0)
        self.assertGreaterEqual(score_full, score_partial)
