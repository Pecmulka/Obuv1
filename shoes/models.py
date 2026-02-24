from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class User(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    fio = models.CharField(max_length=255)
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.fio


class PickupPoint(models.Model):
    index = models.CharField(max_length=20)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    house = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.city}, {self.street}, {self.house}"


class OrderStatus(models.Model):
    state = models.CharField(max_length=100)

    def __str__(self):
        return self.state


class Supplier(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    article = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    discount = models.IntegerField(default=0)
    stock = models.IntegerField()
    description = models.TextField()
    photo = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Order(models.Model):
    nomer_zakaza = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    kolichestvo = models.IntegerField()
    order_date = models.DateField()
    delivery_date = models.DateField()
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    receive_code = models.CharField(max_length=50)
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order #{self.id}"
