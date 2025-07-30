# MultisafePay Payment Redirect View

This app provides order related data to the Multisafe Payment extension when plugged-in to project zero.

## Installation

Add the package to requirements.txt file and install it via pip:

    pip install multisafepay-payment

## Configuration

### 1. Adding App
Include the following lines in your `omnife_base.settings` file:

```python
INSTALLED_APPS.append('multisafepay_payment')

PZ_SERVICE_CLASS = "omnife.core.service.Service"
HASH_SECRET_KEY = "your-hash-secret-key"
MULTISAFEPAY_EXTENSION_URL = "extension url"
MULTISAFEPAY_PAYMENT_METHODS = {
    "msext_paypal": "PAYPAL",
    "msext_bancontact": "MISTERCASH",
    "msext_mastercard": "MASTERCARD",
    "msext_visa": "VISA"
} 
```

### Explanation of Settings

| Setting Name                   | Description                                                                                                                                                                                                                                                                          |
|--------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `MULTISAFEPAY_PAYMENT_METHODS` | A setting that maps payment option slugs to Multisafe payment methods. <br/> {"payment_option_slug": "Gateway ID"}<br/>For the full list of available Gateway IDs, visit: [https://docs.multisafepay.com/reference/gateway-ids](https://docs.multisafepay.com/reference/gateway-ids) |
| `MULTISAFEPAY_EXTENSION_URL`   | The URL where the Multisafe Payment extension is hosted.                                                                                                                                                                                                                             |
| `HASH_SECRET_KEY`              | A secret key used for security.                                                                                                                                                                                                                                                      |



### 2. Add URL Pattern
Add url pattern to `omnife_base.urls` like below:
```python
urlpatterns = [
    # ...
    path('payment-gateway/multisafepay/', include('multisafepay_payment.urls')),
]
```

## Running Tests

    python -m unittest discover

## Python Version Compatibility

This package is compatible with the following Python versions:
  - Python 3.9
