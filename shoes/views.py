from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Max
from django.contrib import messages
from .models import User, Product, Category, Manufacturer, Supplier, Order
from decimal import Decimal
import os
from django.conf import settings
from PIL import Image
import uuid


def main_page(request):
    if 'edit_mode' in request.session:
        del request.session['edit_mode']
    if 'edit_article' in request.session:
        del request.session['edit_article']

    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')

    products = Product.objects.all()



    if user_role in ['Администратор', 'Менеджер']:
        query = request.GET.get('q')
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query) |
                Q(article__icontains=query) | Q(category__name__icontains=query)
            )
        sort = request.GET.get('sort')
        if sort == 'asc':
            products = products.order_by('stock')
        elif sort == 'desc':
            products = products.order_by('-stock')

    for product in products:
        if product.discount > 0:
            product.final_price = product.price - (product.price * Decimal(product.discount) / 100)
        else:
            product.final_price = product.price

    user_name = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            user_name = user.fio
        except User.DoesNotExist:
            request.session.flush()
            user_role = None

    return render(request, 'main.html', {
        'products': products,
        'user_role': user_role,
        'user_name': user_name,
    })


def login_view(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        try:
            user = User.objects.get(login=login, password=password)
            request.session['user_id'] = user.id
            request.session['user_role'] = user.role.name
            request.session['user_name'] = user.fio
            return redirect('main_page')
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Неверный логин или пароль'})
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('main_page')


def product_add(request):
    if request.session.get('user_role') != 'Администратор':
        messages.error(request, 'Нет прав для добавления товаров')
        return redirect('main_page')

        # Принудительно очищаем старые флаги
    if 'edit_mode' in request.session:
        del request.session['edit_mode']
    if 'edit_article' in request.session:
        del request.session['edit_article']

    request.session['edit_article'] = 'add'

    if request.session.get('edit_mode'):
        messages.warning(request, 'Сначала закройте текущее окно редактирования')
        return redirect('main_page')

    request.session['edit_mode'] = True

    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    suppliers = Supplier.objects.all()

    max_article = Product.objects.aggregate(Max('article'))['article__max']
    if max_article:
        import re
        numbers = re.findall(r'\d+', max_article)
        next_article = f"ART{int(numbers[0]) + 1:03d}" if numbers else "ART001"
    else:
        next_article = "ART001"

    if request.method == 'POST':
        errors = []
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        manufacturer_id = request.POST.get('manufacturer')
        supplier_id = request.POST.get('supplier')
        unit = request.POST.get('unit')
        article = request.POST.get('article', next_article)

        try:
            price = Decimal(request.POST.get('price'))
            if price <= 0:
                errors.append("Цена должна быть положительной")
        except:
            errors.append("Некорректная цена")

        try:
            stock = int(request.POST.get('stock'))
            if stock < 0:
                errors.append("Количество не может быть отрицательным")
        except:
            errors.append("Некорректное количество")

        try:
            discount = int(request.POST.get('discount', 0))
            if discount < 0 or discount > 100:
                errors.append("Скидка от 0 до 100")
        except:
            discount = 0

        photo_filename = ''
        if request.FILES.get('photo'):
            photo = request.FILES['photo']
            try:
                img = Image.open(photo)
                img.thumbnail((300, 200))
                ext = os.path.splitext(photo.name)[1]
                photo_filename = f"{uuid.uuid4().hex}{ext}"
                save_path = os.path.join(settings.BASE_DIR, 'static', 'products', photo_filename)
                img.save(save_path)
            except:
                errors.append("Ошибка при сохранении фото")

        if errors:
            return render(request, 'product_form.html', {
                'errors': errors,
                'categories': categories,
                'manufacturers': manufacturers,
                'suppliers': suppliers,
                'next_article': next_article,
                'is_add': True
            })

        Product.objects.create(
            article=article, name=name, unit=unit, price=price,
            supplier_id=supplier_id, manufacturer_id=manufacturer_id,
            category_id=category_id, discount=discount, stock=stock,
            description=description, photo=photo_filename
        )

        messages.success(request, f'Товар "{name}" добавлен')
        del request.session['edit_mode']
        return redirect('main_page')

    return render(request, 'product_form.html', {
        'categories': categories,
        'manufacturers': manufacturers,
        'suppliers': suppliers,
        'next_article': next_article,
        'is_add': True
    })


def product_edit(request, article):
    if request.session.get('user_role') != 'Администратор':
        messages.error(request, 'Нет прав для редактирования')
        return redirect('main_page')

        # Проверяем, есть ли активное редактирование
    if request.session.get('edit_mode') and request.session.get('edit_article') != article:
        # Если есть, но это другой товар - проверяем, не истекла ли сессия
        messages.warning(request, 'Сначала завершите редактирование текущего товара')
        return redirect('main_page')

    product = get_object_or_404(Product, article=article)

    request.session['edit_mode'] = True
    request.session['edit_article'] = article

    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == 'POST':
        errors = []
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        manufacturer_id = request.POST.get('manufacturer')
        supplier_id = request.POST.get('supplier')
        unit = request.POST.get('unit')

        try:
            price = Decimal(request.POST.get('price'))
            if price <= 0:
                errors.append("Цена должна быть положительной")
        except:
            errors.append("Некорректная цена")

        try:
            stock = int(request.POST.get('stock'))
            if stock < 0:
                errors.append("Количество не может быть отрицательным")
        except:
            errors.append("Некорректное количество")

        try:
            discount = int(request.POST.get('discount', 0))
            if discount < 0 or discount > 100:
                errors.append("Скидка от 0 до 100")
        except:
            discount = 0

        photo_filename = product.photo
        if request.FILES.get('photo'):
            photo = request.FILES['photo']
            try:
                img = Image.open(photo)
                img.thumbnail((300, 200))
                ext = os.path.splitext(photo.name)[1]
                photo_filename = f"{uuid.uuid4().hex}{ext}"
                save_path = os.path.join(settings.BASE_DIR, 'static', 'products', photo_filename)
                img.save(save_path)

                if product.photo and product.photo != 'picture.png':
                    old_path = os.path.join(settings.BASE_DIR, 'static', 'products', product.photo)
                    if os.path.exists(old_path):
                        os.remove(old_path)
            except:
                errors.append("Ошибка при сохранении фото")

        if errors:
            return render(request, 'product_form.html', {
                'errors': errors,
                'product': product,
                'categories': categories,
                'manufacturers': manufacturers,
                'suppliers': suppliers,
                'is_add': False
            })

        product.name = name
        product.category_id = category_id
        product.description = description
        product.manufacturer_id = manufacturer_id
        product.supplier_id = supplier_id
        product.unit = unit
        product.price = price
        product.stock = stock
        product.discount = discount
        product.photo = photo_filename
        product.save()

        messages.success(request, f'Товар "{name}" обновлен')
        del request.session['edit_mode']
        del request.session['edit_article']
        return redirect('main_page')

    return render(request, 'product_form.html', {
        'product': product,
        'categories': categories,
        'manufacturers': manufacturers,
        'suppliers': suppliers,
        'is_add': False
    })


def product_delete(request, article):
    if request.session.get('user_role') != 'Администратор':
        messages.error(request, 'Нет прав для удаления')
        return redirect('main_page')

    if request.method == 'POST':
        product = get_object_or_404(Product, article=article)

        if Order.objects.filter(product=product).exists():
            messages.error(request, f'Товар "{product.name}" есть в заказах, удалить нельзя')
            return redirect('main_page')

        if product.photo and product.photo != 'picture.png':
            photo_path = os.path.join(settings.BASE_DIR, 'static', 'products', product.photo)
            if os.path.exists(photo_path):
                os.remove(photo_path)

        product.delete()
        messages.success(request, f'Товар удален')

    return redirect('main_page')