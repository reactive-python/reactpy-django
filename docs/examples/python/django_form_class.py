from django import forms


class MyForm(forms.Form):
    username = forms.CharField(label="Username")
