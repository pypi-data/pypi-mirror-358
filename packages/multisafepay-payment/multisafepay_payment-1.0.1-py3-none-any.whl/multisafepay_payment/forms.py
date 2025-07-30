from django import forms


class MultisafePayForm(forms.Form):
    data = forms.CharField()
