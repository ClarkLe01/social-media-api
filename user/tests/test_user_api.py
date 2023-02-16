"""
Tests for the user API.
"""
from django.core import serializers
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import User

REGISTER_URL = reverse('user:register')
LOGIN_URL = reverse('user:login')
PROFILE_URL = reverse('user:profile')


class UnAuthenticatedUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_successful_login_for_user(self):
        """Test generates token for valid credentials."""
        payload = {
            'email': 'test@example.com',
            'password': 'test123456',
            'first_name': 'Test',
            'last_name': 'Name',
            'gender': '1',
            'birthday': '2001-02-05',
        }
        User.objects.create_user(**payload)

        res = self.client.post(LOGIN_URL, payload)

        self.assertIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_bad_password(self):
        """Test returns error if credentials invalid."""
        payload = {
            'email': 'test@example.com',
            'password': 'goodpass',
            'first_name': 'Test',
            'last_name': 'Name',
            'gender': '1',
            'birthday': '2001-02-05',
        }
        User.objects.create_user(**payload)

        payload = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_email_not_found(self):
        """Test error returned if user not found for given email."""
        payload = {'email': 'test@example.com', 'password': 'pass123'}
        res = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_profile_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Name',
            'gender': 'male',
            'birthday': '2001-02-05',
        }
        res = self.client.post(REGISTER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Name',
            'gender': 'male',
            'birthday': '2001-02-05',
        }
        User.objects.create_user(**payload)
        payload['confirm_password'] = 'testpass123'
        res = self.client.post(REGISTER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            'email': 'test@example.com',
            'password': 'ab',
            'confirm_password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Name',
            'gender': 'male',
            'birthday': '2001-02-05',
        }
        res = self.client.post(REGISTER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = User.objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_password_different(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass1234',
            'first_name': 'Test',
            'last_name': 'Name',
            'gender': 'male',
            'birthday': '2001-02-05',
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = User.objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)


class AuthenticatedUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.payload = {
            'email': 'test@example.com',
            'password': 'goodpass',
            'first_name': 'Test',
            'last_name': 'Name',
            'gender': '1',
            'birthday': '2001-02-05',
        }
        self.user = User.objects.create_user(**self.payload)
        self.client = APIClient()

    def test_retrieve_profile_success(self):
        """Test retrieving profile for authenticated user."""
        self.client.force_authenticate(user=self.user)
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_profile_failed(self):
        """Test retrieving profile for Unauthenticated user."""
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_profile_with_token_success(self):
        """Test retrieving profile using valid token"""
        payload = {
            'email': 'test@example.com',
            'password': 'goodpass',
        }
        res = self.client.post(LOGIN_URL, payload)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + res.data['access'])
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_profile_with_token_failed(self):
        """Test retrieving profile invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token abc')
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
