from django.test import TestCase
from django.urls import reverse


class BaseTest(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.user = {
            'email': 'test@email.com',
            'username': 'username',
            'password': 'password',
            'password2': 'password2',
            'fullname': 'fullname'
        }

        return super().setUp()


class RegisterTest(BaseTest):
    def test_can_view_page_correctly(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/registration.html')

    # def test_can_register_user(self):
    #     response = self.post(self.register_url, self.user, format='text/html')
    #     self.assertEqual(response.status_code, 201)
    #     self.assertTemplateUsed(response, 'auth/login.html')


# from django.test import Client
# csrf_client = Client(enforce_csrf_checks=True)