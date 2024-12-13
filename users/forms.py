# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser

from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
import phonenumbers

class SignupForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Имя"
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Фамилия"
    )
    phone = PhoneNumberField(
        required=True,
        label="Номер телефона",
        widget=forms.TextInput(attrs={'class': 'w-3/4'}),
        error_messages={
           'invalid': "Введите номер телефона в международном формате, например, +12345678900"
        }
    )
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'w-full border rounded py-2 px-3'}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'w-full border rounded py-2 px-3'}),
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = str(self.cleaned_data['phone'])  # Записываем номер в поле username
        if commit:
            user.save()
        return user
   
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone_str = str(phone)
        try:
            # Проверка валидности номера
            parsed_number = phonenumbers.parse(phone_str, None)
            if not phonenumbers.is_valid_number(parsed_number):
                self.add_error('phone', "Введите действительный номер телефона.")
        except phonenumbers.NumberParseException:
            self.add_error('phone', "Введите номер телефона в международном формате, например, +12345678900.")
        return phone
    
class LoginForm(AuthenticationForm):
    username = PhoneNumberField(
        label="Номер телефона",
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border-2 border-gray-300 rounded',
            'placeholder': 'Введите номер телефона'
        }),
        error_messages={
            'invalid': "Введите действительный номер телефона."
        }
    )

    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'w-full border rounded py-2 px-3'}),
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password']
    
    def clean_username(self):
        phone = self.cleaned_data.get('username')
        try:
            # Преобразуем в строку, чтобы избежать ошибок
            phone_str = str(phone)
            # Проверяем валидность номера телефона
            parsed_number = phonenumbers.parse(phone_str, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError("Введите действительный номер телефона.")
        except phonenumbers.NumberParseException:
            raise ValidationError("Введите номер телефона в международном формате, например, +12345678900.")
       
        return phone
    
    def clean_password(self):
        # Переопределим метод для пароля, чтобы корректно передать ошибку, если пароль неверный
        password = self.cleaned_data.get('password')
        phone = self.cleaned_data.get('username')
        
        if phone and password:
            user = CustomUser.objects.filter(username=phone).first()
            if user is not None:
                if not user.check_password(password):
                    raise ValidationError("Неверный пароль.")
            else:
                raise ValidationError("Пользователь с таким номером не найден.")
        
        return password
    
class TransferForm(forms.Form):
    phone = PhoneNumberField(
        required=True,
        label="Номер телефона получателя",
        widget=forms.TextInput(attrs={'class': 'w-3/4'}),
        error_messages={
            'invalid': "Введите номер телефона в международном формате, например, +12345678900"
        }
    )
    amount = forms.DecimalField(
        required=True,
        label="Сумма перевода",
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'w-3/4'}),
    )

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError("Сумма перевода должна быть положительной.")
        return amount

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Проверка на существование пользователя с таким номером
        try:
            recipient = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            raise ValidationError("Пользователь с таким номером телефона не найден.")
        return phone