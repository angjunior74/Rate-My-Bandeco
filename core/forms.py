from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class CadastroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'curso', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@usp.br'):
            raise forms.ValidationError("Você deve usar um email @usp.br para se cadastrar.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está cadastrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_admin = False
        user.email_confirmado = False
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
