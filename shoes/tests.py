from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from .models import Product, Category, Manufacturer, Supplier, Role, User


class ProductTests(TestCase):
    """Тесты для товаров"""

    def setUp(self):
        """Подготовка данных"""
        self.category = Category.objects.create(name="Тест")
        self.manufacturer = Manufacturer.objects.create(name="Тест")
        self.supplier = Supplier.objects.create(name="Тест")

        # Товары для тестов
        self.product1 = Product.objects.create(
            article="ART001", name="Телевизор", unit="шт", price=1000,
            supplier=self.supplier, manufacturer=self.manufacturer,
            category=self.category, discount=20, stock=10,
            description="LED телевизор", photo="tv.jpg"
        )

        self.product2 = Product.objects.create(
            article="ART002", name="Смартфон", unit="шт", price=500,
            supplier=self.supplier, manufacturer=self.manufacturer,
            category=self.category, discount=0, stock=5,
            description="Смартфон", photo="phone.jpg"
        )

    def test_discount_calculation(self):
        """Тест расчета скидки"""
        # Товар со скидкой
        if self.product1.discount > 0:
            self.product1.final_price = self.product1.price - (
                    self.product1.price * Decimal(self.product1.discount) / 100
            )
        else:
            self.product1.final_price = self.product1.price

        # Товар без скидки
        if self.product2.discount > 0:
            self.product2.final_price = self.product2.price - (
                    self.product2.price * Decimal(self.product2.discount) / 100
            )
        else:
            self.product2.final_price = self.product2.price

        # Проверка
        self.assertEqual(self.product1.final_price, 800)  # 1000 - 20% = 800
        self.assertEqual(self.product2.final_price, 500)  # без скидки

    def test_search(self):
        """Тест поиска"""
        # Поиск по названию
        result = Product.objects.filter(name__icontains="телевизор")
        self.assertEqual(result.count(), 1)

        # Поиск по описанию
        result = Product.objects.filter(description__icontains="LED")
        self.assertEqual(result.count(), 1)

        # Поиск по артикулу
        result = Product.objects.filter(article__icontains="ART002")
        self.assertEqual(result.count(), 1)

    def test_sorting(self):
        """Тест сортировки"""
        # По возрастанию
        products = Product.objects.all().order_by('stock')
        self.assertEqual(products[0].stock, 5)  # Смартфон
        self.assertEqual(products[1].stock, 10)  # Телевизор

        # По убыванию
        products = Product.objects.all().order_by('-stock')
        self.assertEqual(products[0].stock, 10)  # Телевизор
        self.assertEqual(products[1].stock, 5)  # Смартфон

    def test_filters(self):
        """Тест фильтров"""
        # Товары со скидкой
        with_discount = Product.objects.filter(discount__gt=0)
        self.assertEqual(with_discount.count(), 1)

        # Товары без скидки
        without_discount = Product.objects.filter(discount=0)
        self.assertEqual(without_discount.count(), 1)

        # Товары в наличии
        in_stock = Product.objects.filter(stock__gt=0)
        self.assertEqual(in_stock.count(), 2)

    def test_failing_test(self):
        """Этот тест специально провалится - неправильный расчет скидки"""
        # НАМЕРЕННАЯ ОШИБКА: неправильно рассчитываем скидку
        if self.product1.discount > 0:
            # Ошибка: умножаем на discount без деления на 100
            wrong_price = self.product1.price - (self.product1.price * Decimal(self.product1.discount))
        else:
            wrong_price = self.product1.price

        # Проверяем, что получилось (должно быть 800, а будет -19000)
        self.assertEqual(wrong_price, 800, "Этот тест специально провалится - неправильный расчет скидки!")