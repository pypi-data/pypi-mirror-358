from django.conf.urls import url

from multisafepay_payment.views import MultisafePayPaymentView


urlpatterns = [
    url(r"^$", MultisafePayPaymentView.as_view(), name="multisafe-payment"),
]
