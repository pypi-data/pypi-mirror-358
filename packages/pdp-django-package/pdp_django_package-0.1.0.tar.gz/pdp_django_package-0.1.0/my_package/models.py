from django.db.models import Model, CharField, IntegerField, ForeignKey, CASCADE


class Category(Model):
    name = CharField(max_length=100)


class Product(Model):
    title = CharField(max_length=255)
    price = IntegerField(default=10_000)
    category = ForeignKey(Category, CASCADE, related_name='products')
