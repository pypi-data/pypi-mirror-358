from django.test import TestCase

from help_rating.models import Feedback, Subject


class TestSubject(TestCase):
    def test_str(self):
        subject = Subject.objects.create()
        self.assertEqual(str(subject), "-")


class TestFeedback(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create()

    def test_str(self):
        feedback = Feedback.objects.create(
            subject=self.subject,
            remote_addr="127.0.0.1",
            browser_fingerprint="916cf806c31ceb517129d549a4d758b7947189c0e3e1577cce1877437354e0ec",
            score=10,
        )
        self.assertEqual(str(feedback), "-")
