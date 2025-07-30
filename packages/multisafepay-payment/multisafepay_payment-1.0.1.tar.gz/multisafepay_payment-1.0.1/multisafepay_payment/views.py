import logging

from django.http import Http404, JsonResponse
from django.views.generic import View
from django.template.response import TemplateResponse

from multisafepay_payment.commerce.checkout import CheckoutService
from multisafepay_payment.forms import MultisafePayForm
from multisafepay_payment.extensions import MultisafePayPayment


logger = logging.getLogger(__name__)


class MultisafePayPaymentView(View):
    checkout_service = CheckoutService()
    _multisafe_payment = MultisafePayPayment()
    http_method_names = ["get"]

    def get(self, request):
        session_id = request.GET.get("sessionId")
        if not session_id:
            logging.exception("Missing sessionId")
            raise Http404

        data = self.checkout_service.get_form_data(request)
        multisafe_form = MultisafePayForm(
            initial={"data": data}
        )

        return TemplateResponse(
            request=request,
            template="multisafepay_payment.html",
            context={
                "action_url": f"{self._multisafe_payment.url}/form-page?sessionId={session_id}",
                "action_method": "POST",
                "multisafe_form": multisafe_form,
            },
        )
