from django.contrib import admin
from django.urls import path
from shoes import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.main_page, name='main_page'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]