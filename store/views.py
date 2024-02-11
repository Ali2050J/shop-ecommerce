from django.shortcuts import render
from django.http import JsonResponse

import json
import datetime

from .models import *
from .utils import cartData, guestOrder

def store(request):
    data = cartData(request)
    cart_items = data['cart_items']

    products = Product.objects.all()
    context = {'products': products, 'cart_items': cart_items}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)

    items = data['items']
    order = data['order']
    cart_items = data['cart_items']

    context = {'items': items, 'order': order, 'cart_items': cart_items}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)

    items = data['items']
    order = data['order']
    cart_items = data['cart_items']

    context = {'items': items, 'order': order, 'cart_items': cart_items}
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    print('action: ', action)
    print('product id: ', product_id)

    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        order_item.quantity += 1
    elif action == 'remove':
        order_item.quantity -= 1

    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()

    return JsonResponse('Item was added', safe=False)


def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
    else:
        customer, order = guestOrder(request, data)


    total = float(data['user_form']['total'])
    order.transaction_id = transaction_id

    if float(order.get_cart_total) == total:
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping_form']['address'],
            city=data['shipping_form']['city'],
            state=data['shipping_form']['state'],
            zip_code=data['shipping_form']['zip_code'],
        )
    

    return JsonResponse('Payment Complete ...', safe=False)
