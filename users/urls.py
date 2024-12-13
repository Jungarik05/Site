from django.urls import path
from . import views
from .views import SignupView

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('finance/', views.FinanceView.as_view(), name='finance'),
    path('transfer/', views.TransferView.as_view(), name='transfer'),
    path('archive/', views.ArchiveView.as_view(), name='archive'),

]
