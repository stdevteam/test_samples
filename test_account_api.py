import json
import factory
import uuid

from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status

from .factories import UserFactory


class UserAuthTest(APITestCase):

    def setUp(self):
        self.user = UserFactory(role='user', is_active=True, token_creation_date=timezone.now(),
                                email='testuser@test.py', password='string')
        self.user.set_password('string')
        self.user.save()
        self.valid_email = factory.build(dict, email='testuser@test.py')
        self.invalid_email = factory.build(dict, email='testuser@test')
        self.invalid_email_1 = factory.build(dict, email='noEmail@test.no')
        self.expired_user = UserFactory(role='user', token_creation_date=timezone.datetime(1950, 12, 12))
        self.valid_login_payload = factory.build(dict, email=self.user.email, password='string')
        self.invalid_login_payload = factory.build(dict, email=self.user.email, password='strings')
        self.valid_payload = factory.build(dict, FACTORY_CLASS=UserFactory)
        self.invalid_payload = factory.build(dict, FACTORY_CLASS=UserFactory, email="Invalid email")

    def test_verify_token(self):
        response = self.client.post(reverse('accounts-api:verification'),
                                    data=json.dumps({'token': str(self.user.verification_token)}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # case 2
        response = self.client.post(reverse('accounts-api:verification'),
                                    data=json.dumps({'token': self.expired_user.verification_token}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_activate_user(self):
        # case 1
        response = self.client.post(reverse('accounts-api:activate_view'),
                                    data=json.dumps({'token': "{}".format(uuid.uuid1())}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # case 2
        response = self.client.post(reverse('accounts-api:activate_view'),
                                    data=json.dumps({'token': self.user.verification_token}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # case 3
        response = self.client.post(reverse('accounts-api:activate_view'),
                                    data=json.dumps({'token': self.expired_user.verification_token}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user(self):
        # test case 1
        response = self.client.post(reverse('accounts-api:register_view'),
                                    data=self.valid_payload,
                                    format="json"
                                    )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test case 2
        response = self.client.post(reverse('accounts-api:register_view'),
                                    data=self.invalid_payload,
                                    format="json"
                                    )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_forgotpassword(self):
        # test case 1
        response = self.client.post(reverse('accounts-api:forgotpassword_view'),
                                    data=self.valid_email, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test case 2
        response = self.client.post(reverse('accounts-api:forgotpassword_view'),
                                    data=self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # test case 3
        response = self.client.post(reverse('accounts-api:forgotpassword_view'),
                                    data=self.invalid_email_1, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reset_pass(self):
        # test case 1
        self.user.token_creation_date = timezone.now()
        self.user.save()
        response = self.client.post(reverse('accounts-api:resetpassword_view'),
                                    data=factory.build(dict, password="string", token=self.user.verification_token),
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test case 2
        self.user.token_creation_date = timezone.datetime(2000, 10, 10)
        response = self.client.post(reverse('accounts-api:resetpassword_view'),
                                    data=factory.build(dict, password="string", token=self.user.verification_token),
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resend_token(self):
        # test case 1
        response = self.client.post(reverse('accounts-api:resend_activation_token'),
                                    data=self.valid_email, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test case 2
        response = self.client.post(reverse('accounts-api:resend_activation_token'),
                                    data=self.invalid_email, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login(self):
        # test case 1
        response = self.client.post(reverse('accounts-api:login_view'),
                                    data=self.valid_login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test case 2
        response = self.client.post(reverse('accounts-api:login_view'),
                                    data=self.invalid_login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # test case 3
        self.user.is_active = False
        self.user.save()
        response = self.client.post(reverse('accounts-api:login_view'),
                                    data=self.valid_login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
