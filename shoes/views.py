from django.shortcuts import render, redirect
from django.db.models import Q
from .models import User, Product, Role
from decimal import Decimal


def main_page(request):
    # Получаем информацию о пользователе из сессии
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')

    # Получаем все товары
    products = Product.objects.all()

    # Поиск
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(article__icontains=query) |
            Q(unit__icontains=query) |
            Q(category__name__icontains=query) |
            Q(manufacturer__name__icontains=query) |
            Q(supplier__name__icontains=query)
        )

    # Сортировка по складу
    sort = request.GET.get('sort')
    if sort == 'asc':
        products = products.order_by('stock')
    elif sort == 'desc':
        products = products.order_by('-stock')

    # Расчет цены со скидкой
    for product in products:
        if product.discount > 0:
            product.final_price = product.price - (
                    product.price * Decimal(product.discount) / 100
            )
        else:
            product.final_price = product.price

    # Получаем имя пользователя, если есть
    user_name = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            user_name = user.fio
        except User.DoesNotExist:
            # Очищаем сессию, если пользователь не найден
            request.session.flush()
            user_role = None

    context = {
        'products': products,
        'user_role': user_role,
        'user_name': user_name,
    }

    return render(request, 'main.html', context)


def login_view(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')

        try:
            user = User.objects.get(login=login, password=password)
            role_name = user.role.name

            # Сохраняем информацию о пользователе в сессии
            request.session['user_id'] = user.id
            request.session['user_role'] = role_name
            request.session['user_name'] = user.fio

            return redirect('main_page')

        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Неверный логин или пароль'})

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('main_page')