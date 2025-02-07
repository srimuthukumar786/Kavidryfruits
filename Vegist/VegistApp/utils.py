import pyotp
import json
from .models import *
from django.contrib.auth.hashers import make_password

def generate_otp():
    totp = pyotp.TOTP(pyotp.random_base32(), interval=300)  # 5 minutes validity
    return totp.now()


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    #print('cart:',cart)
    items=[]
    order = {'get_cart_items':0,'get_cart_total':0,'get_cart_weight':0}
    cartitems = len(cart)

    for i in cart:
        #print(i)
        try:
            product = Product.objects.get(id = cart[i]['productId'])
            size  = cart[i]['size']
            price = cart[i]['price']
            total = float(price) * cart[i]['quantity']
            weight = int(cart[i]['size']) * cart[i]['quantity']
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']
            order['get_cart_weight'] += weight

            item = {
                    'product':{
                        'id':product.id,
                        'name': product.name,
                        'Imageurl': product.Imageurl
                    },
                    'size':size,
                    'price': price,
                    'quantity':cart[i]['quantity'],
                    'get_total':total
            }
            items.append(item)
            print(f"Item created for product ID {i}: {item}")
        except Exception as e:
            print(f"Error processing item {i}: {e}")
            pass
    return {'items':items,'order':order,'cartitems':cartitems}

def cartData(request):
     if request.user.is_authenticated:
          customer = request.user
          order,created = Order.objects.get_or_create(customer=customer,complete=False)
          items = order.orderitem_set.all()
          cartitems = order.get_cart
     else:
          cookieData = cookieCart(request)
          cartitems = cookieData['cartitems']
          order = cookieData['order']
          items = cookieData['items']
     return{'items':items,'order':order,'cartitems':cartitems}


def favcookieCart(request):
    try:
        favcart = json.loads(request.COOKIES['favcart'])
    except:
        favcart = {}
    print('favcart:',favcart)
    favitems=[]
    favcartitems=0

    for i in favcart:
        try:
            favcartitems += favcart[i]['quantity']

            product = Product.objects.get(id = i)

            favitem = {
                    'product':{
                        'id':product.id,
                        'name': product.name,
                        'slug':product.slug,
                        'Imageurl': product.Imageurl
                    }
            }
            favitems.append(favitem)
        except:
            pass
    return {'favitems':favitems,'favcartitems':favcartitems}

def favcartData(request):
     if request.user.is_authenticated:
          customer = request.user
          favitems = Favorite.objects.filter(user=customer)
          favcartitems = favitems.count()
     else:
          favcookieData = favcookieCart(request)
          favcartitems = favcookieData['favcartitems']
          favitems = favcookieData['favitems']
     return{'favitems':favitems,'favcartitems':favcartitems}

def guestOrder(request,data):
     print('User not logged in...')
     print('COOKIES:',request.COOKIES)
     fname = data['fname']
     lname = data['lname']
     email = data['email']
     phone = data['phone']
     password = make_password(data['password'])
     cookieData = cookieCart(request)
     items = cookieData['items']

     customer,created = CustomUser.objects.get_or_create(
        email = email,
     )
     customer.first_name = fname
     customer.last_name = lname
     customer.mobile = phone
     customer.password = password
     customer.save()

     order = Order.objects.create(
        customer = customer,
        complete =  False,
      )

     for item in items:
        product = Product.objects.get(id = item['product']['id'])

        orderItem =  OrderItem.objects.create(
            product = product,
            order = order,
            size = item['size'],
            price = item['price'],
            quantity = item['quantity'],
        )
     return customer,order