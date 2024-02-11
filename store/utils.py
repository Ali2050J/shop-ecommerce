import json
from .models import *


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cart_items = order['get_cart_items']
    
    for item in cart:
        try:
            cart_items += cart[item]['quantity']

            product = Product.objects.get(id=item)
            total = (product.price * cart[item]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[item]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                },
                'quantity': cart[item]['quantity'],
                'get_total': total
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass

    return {'items': items, 'order': order, 'cart_items': cart_items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitems.all()
        cart_items = order.get_cart_items
    else:
        cookie_data = cookieCart(request)
        cart_items = cookie_data['cart_items']
        order = cookie_data['order']
        items = cookie_data['items']

    return {'items': items, 'order': order, 'cart_items': cart_items}


def guestOrder(request, data):
    name = data['user_form']['name']
    email = data['user_form']['email']

    cookie_data = cookieCart(request)
    items = cookie_data['items']

    customer , created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    order = Order.objects.create(customer=customer, complete=False)

    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        order_item = OrderItem.objects.create(order=order, product=product, quantity=item['quantity'])

    return customer, order
