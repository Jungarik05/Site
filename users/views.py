# users/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import CustomUser, Transaction
from django.utils import timezone

from .forms import SignupForm
from .forms import LoginForm
from .forms import TransferForm

def home(request):
    return render(request, 'home.html')  # Главная страница


class SignupView(View):
    template_name = "users/signup.html"

    def get(self, request):
        form = SignupForm()
        return render(request, 'users/signup.html', {'form': form})  # Возвращаем форму в шаблон

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Пользователь {user.username} успешно зарегистрирован!')
            return redirect('profile')  # Перенаправление на главную страницу
        else:
            messages.error(request, 'Ошибка при регистрации. Проверьте введённые данные.')
        return render(request, 'users/signup.html', {'form': form})  # Повторно отображаем форму

class LoginView(View):
    template_name = "users/login.html"

    def get(self, request):
        form = LoginForm()  # Форма аутентификации
        return render(request, 'users/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(data=request.POST)  # Обработка данных из формы
        if form.is_valid():
            phone = form.cleaned_data.get('username')  # Получаем номер телефона
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=phone, password=password)
            if user:
                login(request, user)  # Вход в систему
                messages.success(request, f'Добро пожаловать, {user.first_name} {user.last_name}!')
                return redirect('profile')  # Перенаправление на страницу профиля
            else:
                messages.error(request, 'Неверный номер телефона или пароль.')
        else:
            messages.error(request, 'Ошибка при входе. Проверьте логин и пароль.')
        return render(request, self.template_name, {'form': form})
    
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            "email": getattr(user, "email", "Не указан"),
            "phone": user.phone,
            "finance_url": "/finance/",
            "support_url": "/support/",
        })
        return context
    
class FinanceView(LoginRequiredMixin, TemplateView):
    template_name = "users/finance.html"

    def get(self, request, *args, **kwargs):
            context = self.get_context_data(**kwargs)
            user = request.user

            # Получаем все транзакции, в которых участвует пользователь
            transactions = Transaction.objects.filter(sender=user) | Transaction.objects.filter(recipient=user)
            
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date') 
            #Преобразуем строки в объекты даты
            if start_date and end_date:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d') + timezone.timedelta(days=1)  # Добавляем один день для включения конечной даты
            # Фильтруем транзакции
                transactions = transactions.filter(date__gte=start_date, date__lt=end_date)
            else:
                transactions = transactions.all()  # Если даты не указаны, получаем все транзакции
            
            transactions = transactions.order_by('date') # Отсортируем транзакции по времени
            context ['transactions'] = transactions # Добавляем тразакции в контекст

            return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            "balance": user.balance,
            "transfer_url": "/transfer/",  # URL для страницы перевода
        })
        return context   
     
class TransferView(View):
    template_name = 'users/transfer.html'

    def get(self, request):
        form = TransferForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = TransferForm(request.POST)
        if form.is_valid():
            sender = request.user
            phone = form.cleaned_data['phone']
            amount = form.cleaned_data['amount']

             # Получаем получателя
            try:
                recipient = CustomUser .objects.get(phone=phone)
            except CustomUser .DoesNotExist:
                form.add_error('phone', "Получатель с таким номером не найден.")
                return render(request, self.template_name, {'form': form})

            # Проверка на попытку отправки денег самому себе
            if sender == recipient:
                form.add_error('phone', "Вы не можете отправить деньги самому себе.")
                return render(request, self.template_name, {'form': form})

            # Проверка наличия средств на аккаунте
            if sender.balance < amount:
                form.add_error('amount', "Недостаточно средств на счете.")
                return render(request, self.template_name, {'form': form})

            # Обновляем баланс отправителя и получателя
            sender.balance -= amount
            recipient.balance += amount
            sender.save()
            recipient.save()

            # Сохраняем информацию о переводе в истории
            Transaction.objects.create(
                sender=sender,
                recipient=recipient,
                amount=amount
            )

            messages.success(request, f"Вы успешно перевели {amount} на номер {phone}.")
            return redirect('profile')  # Перенаправление на профиль
        else:
            messages.error(request, "Ошибка при отправке перевода. Проверьте введенные данные.")
        return render(request, self.template_name, {'form': form}) 
      
class ArchiveView(View):
    def get(self, request):
        user = request.user

        # Получаем все транзакции, в которых участвует пользователь
        transactions = Transaction.objects.filter(sender=user) | Transaction.objects.filter(recipient=user)

        # Отсортируем транзакции по времени
        transactions = transactions.order_by('date')

        # Передаем в контекст все транзакции
        context = {
            'transactions': transactions,
        }

        return render(request, 'users/archive.html', context)