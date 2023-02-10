from django.test import TestCase
from user.views import caculate


class CurrencyModelTests(TestCase):
    def setUp(self):
        self.a = 3
        self.b = 4

    def test_pass(self):
        self.assertEqual(self.a + self.b, caculate(self.a, self.b))
