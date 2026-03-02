from django.contrib import admin
from django.urls import path
from shoes import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.main_page, name='main_page'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # CRUD операции с товарами
    path('product/add/', views.product_add, name='product_add'),
    path('product/<str:article>/edit/', views.product_edit, name='product_edit'),
    path('product/<str:article>/delete/', views.product_delete, name='product_delete'),
]