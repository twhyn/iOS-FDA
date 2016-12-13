import json

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import AccessToken

from iOSfoodDeliveryApp.models import Restaurant, Meal, Order, OrderDetails, Driver
from iOSfoodDeliveryApp.serializers import RestaurantSerializer, MealSerializer, OrderSerializer

# ################## #
#      customers     #
# ################## #

def customer_get_restaurants(request):
  restaurants = RestaurantSerializer(
    Restaurant.objects.all().order_by("-id"),
    many = True,
    context = {"request": request}
  ).data

  return JsonResponse({"restaurants": restaurants})

def customer_get_meals(request, restaurant_id):
  meals = MealSerializer(
    Meal.objects.filter(restaurant_id = restaurant_id).order_by("-id"),
    many = True,
    context = {"request": request}
  ).data
  return JsonResponse({"meals": meals})

# SECURITY WARNING: comment out csrf_exempt in production!
@csrf_exempt
def customer_add_order(request):
  """
    params:
      access_token
      restaurant_id
      address
      order_details (json format)
      stripe_token

    return:
      {"status": "success"}
  """
  if request.method == "POST":
    # token
    access_token = AccessToken.objects.get(token = request.POST.get("access_token"), expires__gt = timezone.now() )

    # profile from token
    customer = access_token.user.customer

    # check order that has yet been delivered for the customer
    if Order.objects.filter(customer = customer).exclude(status = Order.DELIVERED):
      return JsonResponse({"status": "failed", "error": "Your last order must be completed."})

    # check address
    if not request.POST["address"]:
      return JsonResponse({"status": "failed", "error": "Please input your address."})

    # get order details
    order_details = json.loads(request.POST["order_details"])

    # calculate order
    order_total = 0
    for meal in order_details:
      order_total += Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]

    if len(order_details) > 0:
      # create order
      order = Order.objects.create(
        customer = customer,
        restaurant_id = request.POST["restaurant_id"],
        total = order_total,
        status = Order.COOKING,
        address = request.POST["address"]
      )

      # create order details
      for meal in order_details:
        OrderDetails.objects.create(
          order = order,
          meal_id = meal["meal_id"],
          quantity = meal["quantity"],
          sub_total = Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]
        )

      return JsonResponse({"status": "success"})

def customer_get_latest_order(request):
  access_token = AccessToken.objects.get(token = request.GET.get("access_token"), expires__gt = timezone.now())

  customer = access_token.user.customer
  order = OrderSerializer(Order.objects.filter(customer = customer).last()).data

  return JsonResponse({"order": order})

def restaurant_order_notification(request, last_request_time):
  notification = Order.objects.filter(restaurant = request.user.restaurant, created_at__gt = last_request_time).count()

  return JsonResponse({"notification": notification})
