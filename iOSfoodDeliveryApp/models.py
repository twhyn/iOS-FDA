from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# RELATIONSHIP DESCRIPTION
# User       1-1 Restaurant, Customer, Driver
# Restaurant 1-N Meal
# Order      N-1 Restaurant, Customer, Driver


class Restaurant(models.Model):
  user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant')
  name    = models.CharField(max_length=500)
  phone   = models.CharField(max_length=500)
  address = models.CharField(max_length=500)
  logo    = models.ImageField(upload_to='restaurant_logo/', blank=False)

  # in default displays id, therefore set it to name to display name in admin dashboard
  def __str__(self):
    return self.name

class Customer(models.Model):
  user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
  avatar  = models.CharField(max_length=500)
  phone   = models.CharField(max_length=500, blank=True)
  address = models.CharField(max_length=500, blank=True)

  def __str__(self):
    # get_full_name from user model of django
    return self.user.get_full_name()

class Driver(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver')

  avatar  = models.CharField(max_length=500)
  phone   = models.CharField(max_length=500, blank=True)
  address = models.CharField(max_length=500, blank=True)

  def __str__(self):
    # get_full_name from user model of django
    return self.user.get_full_name()

class Meal(models.Model):
  restaurant        = models.ForeignKey(Restaurant)
  name              = models.CharField(max_length=500)
  short_description = models.CharField(max_length=500)
  image             = models.ImageField(upload_to='meal_images/', blank=False)
  price             = models.IntegerField(default = 0)

  def __str__(self):
    return self.name

class Order(models.Model):
  COOKING   = 1
  READY     = 2
  ONTHEWAY  = 3
  DELIVERED = 4

  STATUS_CHOICES = (
    (COOKING, "Cooking"),
    (READY, "Ready"),
    (ONTHEWAY, "On the way"),
    (DELIVERED, "Delivered")
  )

  customer    = models.ForeignKey(Customer)
  restaurant  = models.ForeignKey(Restaurant)
  driver      = models.ForeignKey(Driver, blank = True, null = True)
  address     = models.CharField(max_length=500)
  total       = models.IntegerField()
  status      = models.IntegerField(choices = STATUS_CHOICES)
  created_at  = models.DateTimeField(default = timezone.now)
  picked_at   = models.DateTimeField(blank = True, null = True)

class OrderDetails(models.Model):
    order = models.ForeignKey(Order, related_name='order_details')
    meal = models.ForeignKey(Meal)
    quantity = models.IntegerField()
    sub_total = models.IntegerField()

    def __str__(self):
        return str(self.id)