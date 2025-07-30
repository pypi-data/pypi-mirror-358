from decimal import Decimal
import json

from unittest.mock import Mock
from django.http import Http404
from django.conf import settings
from django.test import SimpleTestCase
from django.test import override_settings
from django.test.client import RequestFactory
from mock.mock import patch
from rest_framework import status

from multisafepay_payment.tests.mixins import MockResponseMixin

try:
    settings.configure()
except RuntimeError:
    pass


@override_settings(
    HASH_SECRET_KEY="test-hash-secret-key",
    PZ_SERVICE_CLASS="multisafepay_payment.commerce.dummy.Service",
    MULTISAFEPAY_PAYMENT_METHODS={"msext_bancontact": "MISTERCASH"}
)
class TestCheckoutService(SimpleTestCase, MockResponseMixin):
    def setUp(self):
        from multisafepay_payment.commerce.checkout import CheckoutService

        self.service = CheckoutService()
        self.request_factory = RequestFactory()

    @patch("multisafepay_payment.commerce.dummy.Service.get")
    @patch("multisafepay_payment.commerce.checkout.CheckoutService.generate_hash")
    @patch("multisafepay_payment.commerce.checkout.CheckoutService.generate_salt")
    def test_get_data(self, mock_generate_salt, mock_generate_hash, mock_get):
        mock_generate_hash.return_value = "test-hash"
        mock_generate_salt.return_value = "test-salt"
        mocked_response = self._mock_response(
            status_code=200,
            content=self._get_response("orders_checkout_response"),
            headers={"Content-Type": "application/json"},
        )
        mock_get.return_value = mocked_response

        request = self.request_factory.get("/payment-gateway/multisafepay/")
        form_data = self.service.get_form_data(request)
        form_data = json.loads(form_data)

        self.assertEqual(form_data["salt"], "test-salt")
        self.assertEqual(form_data["hash"], "test-hash")

        self.assertEqual(form_data["gateway"], "MISTERCASH")
        customer = form_data["customer"]
        self.assertEqual(set( customer.keys()), {"city", "country", "zip_code"})
        self.assertEqual(customer["city"], "İstanbul")
        self.assertEqual(customer["country"], "TR")
        self.assertEqual(customer["zip_code"], "34220")

    @patch("multisafepay_payment.commerce.dummy.Service.get")
    def test_retrieve_pre_oder(self, mock_get):
        mocked_response = self._mock_response(
            status_code=200,
            content=self._get_response("orders_checkout_response"),
            headers={"Content-Type": "application/json"},
        )
        mock_get.return_value = mocked_response

        request = self.request_factory.get("/payment-gateway/multisafepay/")
        response = self.service._retrieve_pre_order(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("pre_order", response.data)

    @patch("hashlib.sha512")
    def test_get_hash(self, mock_sha512):
        session_id = "test-session-id"
        self.service.generate_hash("test-salt", session_id)
        mock_sha512.assert_called_once_with(
            "test-salt|test-session-id|test-hash-secret-key".encode("utf-8")
        )

    @patch("secrets.token_hex")
    def test_generate_salt(self, mock_token_hex):
        self.service.generate_salt()
        mock_token_hex.assert_called_once()
    
    def test__validate_checkout_step(self):
        mock_resp = Mock()
        mock_resp.data = {}
        
        with self.assertRaises(Http404):
            self.service._validate_checkout_step(mock_resp)
        
        mock_resp.data = {"pre_order": {"shipping_option": None}}
        with self.assertRaises(Http404):
            self.service._validate_checkout_step(mock_resp)

        mock_resp.data = {
            "context_list": [{"page_name": "ShippingOptionSelectionPage"}],
            "pre_order": {
                "shipping_option": {
                    "pk": 2,
                    "name": "Yurtici Kargo",
                    "slug": "yurtici",
                    "logo": None,
                    "shipping_amount": "9.99",
                    "description": None,
                    "kwargs": {}
                        }
                }
        }
        with self.assertRaises(Http404):
            self.service._validate_checkout_step(mock_resp)
            
        mock_resp.data = {
            "context_list": [{"page_name": "PaymentOptionSelectionPage"}],
            "pre_order": {
                "shipping_option": {
                    "pk": 2,
                    "name": "Yurtici Kargo",
                    "slug": "yurtici",
                    "logo": None,
                    "shipping_amount": "9.99",
                    "description": None,
                    "kwargs": {}
                },
                 "unpaid_amount": 10,
            },
        }
        self.service._validate_checkout_step(mock_resp)

    def test_shipping_address(self):
        _shipping_address = self.service._get_address({
              "pk": 50,
              "email": "akinon@akinon.com",
              "phone_number": "0555555555",
              "first_name": "akinon",
              "last_name": "akinon",
              "country": {
                  "pk": 1,
                  "name": "Türkiye",
                  "code": "tr"
              },
              "city": {
                  "pk": 47,
                  "name": "İstanbul",
                  "country": 1
              },
              "line": "YTÜ-Davutpaşa Kampüsü Teknopark Bölgesi B2 Blok D:Kat:2, No: 417",
              "title": "ofis",
              "township": {
                  "pk": 209,
                  "name": "ESENLER",
                  "city": 47
              },
              "district": {
                  "pk": 2194,
                  "name": "ÇİFTEHAVUZLAR/ESENLER",
                  "city": 47,
                  "township": 209
              },
              "postcode": "34220",
              "notes": None,
              "company_name": "",
              "tax_office": "",
              "tax_no": "",
              "e_bill_taxpayer": False,
              "is_corporate": False,
              "primary": False,
              "identity_number": None,
              "extra_field": None
        })
        self.assertEqual(_shipping_address, {
                "city": "İstanbul",
                "country": "TR",
                "zip_code": "34220",
            }
        )
