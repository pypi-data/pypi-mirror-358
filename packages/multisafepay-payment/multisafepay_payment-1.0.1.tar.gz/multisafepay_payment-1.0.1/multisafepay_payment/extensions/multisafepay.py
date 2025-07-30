from urllib.parse import urljoin
import logging

import requests
from django.http import Http404
from django.conf import settings


class MultisafePayPayment:
    def __init__(self):
        url = getattr(settings, "MULTISAFEPAY_EXTENSION_URL", None)
        if not url:
            logging.exception("Missing MULTISAFEPAY_EXTENSION_URL")
            raise Http404
        self.base_url = url

    def _send_request(self, url, method, **kwargs):
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as ex:
            response_text = ex.response.text if ex.response is not None else None
            status_code = ex.response.status_code if ex.response is not None else None

            logging.exception("MultisafePay Payment Request Error",
                              extra={"url": url,
                                     "method": method,
                                     "status_code": status_code,
                                     "response_text": response_text,
                                     "exception": ex
                                     })
            return None

    @property
    def url(self):
        return self.base_url
