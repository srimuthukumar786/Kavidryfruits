from django.shortcuts import render,redirect
from .models import *
import sweetify
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login,authenticate,logout
from django.core.mail import send_mail
from django.conf import settings
from datetime import date,timedelta
from .utils import *
from .forms import *
from django.http import JsonResponse
import json
from django.db.models import Q,Avg,Sum
from decimal import Decimal

# Create your views here.
def index(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartcount = data['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()
    best = Product.objects.filter(best=True)
    featured = Product.objects.filter(featured=True)
    trending = Product.objects.filter(trending=True)
    fifteen_days_ago = date.today() - timedelta(days=10)
    new_products = Product.objects.filter(date__gte=fifteen_days_ago)
    reviews = Review.objects.all()
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = subscribers.objects.filter(subscriber_email=request.user.email, subscribed=True).exists()
    return render(request,'index.html',{'cartitems':cartcount,'items':items,'order':order,'favcount':favcartitems,'best': best,'featured': featured,'trending': trending,'new_products': new_products,'categories': categories,'reviews':reviews,'subscribers':is_subscribed})


def register(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartitems = data['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('mobile')
        password = request.POST.get('password')
        if CustomUser.objects.filter(email = email).exists():
            sweetify.sweetalert(request,'Error',text='Email already Exists!',icon='error', button='OK!')
            return redirect('register')
         # Hash the password before saving
        hashed_password = make_password(password)  # Hash the password using Django's built-in function

        user = CustomUser(email = email,password = hashed_password, first_name = fname, last_name = lname, mobile = phone)
        user.save()
        sweetify.sweetalert(request,'Success',text='Your account has been successfully created!',icon='success', button='OK!')
        return redirect('loginpage')
    return render(request,'register.html',{'categories': categories,'favcount':favcartitems,'cartitems':cartitems,'items':items,'order':order})

def loginpage(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartitems = data['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            email=request.POST.get('email')
            password=request.POST.get('password')
            user=authenticate(request,email=email,password=password)
            if user is not None:
                login(request,user)
                sweetify.sweetalert(request, 'Success', text=f'Welcome {request.user.first_name}!', icon='success', button='OK!')
                return redirect('/')
            else:
                sweetify.sweetalert(request,'Error',text='Invalid Username and Password',icon='error', button='OK!')
                return redirect('loginpage')
    return render(request,'login.html',{'categories': categories,'favcount':favcartitems,'cartitems':cartitems,'items':items,'order':order})

def logout_page(request):
   if request.user.is_authenticated:
      logout(request)
      sweetify.sweetalert(request, 'Success', text='Logout Successfully', icon='success', button='OK!')
   return redirect('/')

def OTPlogin(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartitems = data['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            # Try to fetch the user by email
            user = CustomUser.objects.get(email=email)
            if not user:
                sweetify.error(request, 'User Not Found!')
                return redirect('register')
            
            # Generate and save OTP
            email_otp = generate_otp()
            print(email_otp)
            user.otp = email_otp
            user.save()  # Ensure the OTP is saved to the database
            
            # Send email OTP
            send_mail(
                'Email Verification OTP',
                f'Your OTP for email verification is: {email_otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            # Optionally redirect to verify OTP page
            return redirect('verifyotp', user_id=user.id)

        except CustomUser.DoesNotExist:
            sweetify.error(request, 'User Not Found!')
            return redirect('register')
    return render(request,'otplogin.html',{'categories': categories,'favcount':favcartitems,'cartitems':cartitems,'items':items,'order':order})

def verify_otp(request, user_id):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartitems = data['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()

    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        email_otp = request.POST.get('otp')
        print(type(email_otp))
        print(type(user.otp))

        if email_otp == str(user.otp):
            user.is_email_verified = True
            user.otp = None  # Clear OTP after successful verification
            user.save()

            # Log the user in and redirect to the homepage
            login(request, user)
            sweetify.sweetalert(request, 'Success', text=f'Welcome {request.user.first_name}!', icon='success', button='OK!')
            return redirect('/')

        else:
            # If OTP is invalid, show an error
            sweetify.error(request, 'Invalid OTP!')
            return render(request, 'verifyotp.html')

    return render(request, 'verifyOTP.html',{'categories': categories,'favcount':favcartitems,'cartitems':cartitems,'items':items,'order':order})

def forgotpassword(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartitems = data['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            # Try to fetch the user by email
            user = CustomUser.objects.get(email=email)
            if not user:
                sweetify.error(request, 'User Not Found!')
                return redirect('register')
            
            # Generate and save OTP
            email_otp = generate_otp()
            print(email_otp)
            user.otp = email_otp
            user.save()  # Ensure the OTP is saved to the database
            
            # Send email OTP
            send_mail(
                'Forgot Password OTP',
                f'Your OTP is: {email_otp} for reset your password',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            # Optionally redirect to verify OTP page
            return redirect('forgotpasswordverifyotp', user_id=user.id)

        except CustomUser.DoesNotExist:
            sweetify.error(request, 'User Not Found!')
            return redirect('register')
    return render(request,'forgotpassword.html',{'categories': categories,'favcount':favcartitems,'cartitems':cartitems,'items':items,'order':order})

def termsconditions(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartitems = data['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()
    return render(request,'termsconditions.html',{'categories': categories,'favcount':favcartitems,'cartitems':cartitems,'items':items,'order':order})

def forgotpasswordverifyotp(request,user_id):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartitems = data['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()
    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        email_otp = request.POST.get('otp')
        print(type(email_otp))
        print(type(user.otp))

        if email_otp == str(user.otp):
            user.otp = None  # Clear OTP after successful verification
            user.save()

            sweetify.sweetalert(request, 'Success', text='OTP Verified!', icon='success', button='OK!')
            return redirect('resetpassword',user_id = user.id)

        else:
            # If OTP is invalid, show an error
            sweetify.error(request, 'Invalid OTP!')
            return render(request,'forgotpasswordverifyotp.html')
    return render(request,'forgotpasswordverifyotp.html',{'categories': categories,'favcount':favcartitems,'cartitems':cartitems,'items':items,'order':order})

def resetpassword(request,user_id):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartitems = data['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()

    user = CustomUser.objects.get(id=user_id)
    if request.method == 'POST':
        npassword = request.POST.get('npassword')

        user.password = make_password(npassword)
        user.save()
        sweetify.sweetalert(request, 'Success', text='Password Changed Successfully!', icon='success', button='OK!')
        return redirect('loginpage')

    return render(request,'resetpassword.html',{'categories': categories,'favcount':favcartitems,'cartitems':cartitems,'items':items,'order':order})


def category(request,slug):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartitems = data['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()
    if(Category.objects.filter(slug=slug)):
        products = Product.objects.filter(category__slug=slug)
        category = Category.objects.filter(slug=slug).first()
        context = {'categories': categories,'products':products,'category':category,'cartitems':cartitems,'favcount':favcartitems,'items':items,'order':order}
        return render(request,'category.html',context)
    else:
        sweetify.error(request,'No such category found')
        return redirect('/')
    
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    size = data['size']
    price = data['price']
    quantity = data['quantity']
    
    print('Action:', action)
    print('productId:', productId)
    print('size:', size)
    print('price:', price)
    print('quantity:',quantity)

    customer = request.user
    product = Product.objects.get(id=productId)
    
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem = OrderItem.objects.filter(order=order, product=product).first()

    if orderItem:
        if orderItem.size == size and orderItem.price == float(price):
            if action == 'add':
                orderItem.quantity += 1
            elif action == 'remove':
                orderItem.quantity -= 1
            elif action == 'delete':
                orderItem.delete()
        else:
            if action == 'add':
                #orderItem.delete()
                orderItem = OrderItem.objects.create(order=order, product=product, size=size, price=float(price), quantity=quantity)
                sweetify.success(request, 'Item updated successfully!')

    else:
        if action == 'add':
            orderItem = OrderItem.objects.create(order=order, product=product, size=size, price=price, quantity=quantity)
            sweetify.success(request, 'Item Added successfully!')
    
    if action != 'delete':
        orderItem.save()

    if orderItem and orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse({'message': 'Item was updated'}, safe=False)

def fav_page(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('ProductId:', productId)
    
    customer = request.user
    try:
        product = Product.objects.get(id=productId)
    except:
        pass

    # Check if the product is already in the favorites for this user
    existing_fav = Favorite.objects.filter(user=customer, product=product).first()

    if existing_fav:
        if action == 'add':
            sweetify.error(request,'Product Already in wishlist!')
        elif action == 'delete':
            existing_fav.delete()
            sweetify.success(request,'Product Deleted Successfully from wishlist!')
    
    # If the product is not in favorites, create it
    if action == 'add':
        favitem, created = Favorite.objects.get_or_create(user=customer, product=product)
        if created:
            sweetify.success(request,'Product Added Successfully in wishlist!')

    return JsonResponse({'status': 'Invalid action'}, status=400)

def wishlist(request):
    categories = Category.objects.all()
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartitems = data['cartitems']
    favdata = favcartData(request)
    favitems = favdata['favitems']
    favcartitems = favdata['favcartitems']
    return render(request,'wishlist.html',{'fav':favitems,'favcount':favcartitems,'cartitems':cartitems,'items':items,'order':order,'categories':categories})

    
def product(request,pname):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartitems = data['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()
    if(Product.objects.filter(name=pname,status='Published')):
        product = Product.objects.filter(name=pname,status='Published').first()
        related_products = Product.objects.filter(category=product.category,status="Published").exclude(id=product.id)
        review_form = ReviewForm()
        context = {'categories': categories,'product':product,'related_products':related_products,'review_form':review_form,'cartitems':cartitems,'favcount':favcartitems,'items':items,'order':order}
    else:
        sweetify.error(request,'No such product found')
        return redirect('/')
    return render(request,'product.html',context)

def add_review(request, pid):
   product = Product.objects.get(id=pid)
   user = request.user
   

   review = Review.objects.create(
       product=product,
       user=user,
       review=request.POST['review'],
       rating=request.POST['rating']
   )
   context={
        'user':user.email,
       'review':request.POST['review'],
       'rating':request.POST['rating'],
   }
   average_reviews = Review.objects.filter(product=product).aggregate(rating=Avg('rating'))
   #review.save()

   return JsonResponse({'bool':True, 'context':context,'average_reviews':average_reviews})

def cartpage(request):
     data = cartData(request)
     items = data['items']
     order = data['order']
     cartitems = data['cartitems']
     favdata = favcartData(request)
     favcartitems = favdata['favcartitems']
     categories = Category.objects.all()
     return render(request,'cart.html',{'categories': categories,'items':items,'order':order,'cartitems':cartitems,'favcount':favcartitems})

def checkout(request):
    coupon_code = Coupon.objects.all().first()
    try:
        coupon = Coupon.objects.get(code=coupon_code)
        discount = coupon.discount_percentage
        coupon_used_count = coupon.used_count
        coupon_max_usage = coupon.max_usage
    except Coupon.DoesNotExist:
        coupon=''
        discount=0
        coupon_used_count = 0
        coupon_max_usage = 0
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartitems = data['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()
    return render(request,'checkout.html',{'categories': categories,'items':items,'order':order,'cartitems':cartitems,'favcount':favcartitems,'coupon':coupon_code,'discount':discount,'coupon_used_count': coupon_used_count,'coupon_max_usage': coupon_max_usage})

def apply_coupon(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code')
        total = Decimal(data.get('total'))  # Ensure 'total' is a Decimal
        shipping = Decimal(data.get('shippingamt'))
        
        try:
            # Validate the coupon by checking max_usage and used_count
            coupon = Coupon.objects.get(code=coupon_code)
            
            # Check if the coupon has available usage left
            if coupon.used_count >= coupon.max_usage:
                return JsonResponse({
                    'success': False,
                    'message': 'Coupon usage limit reached.'
                })

            # Convert discount_percentage to Decimal (if it is a float, convert it)
            discount_percentage = Decimal(coupon.discount_percentage)

            # Calculate the discount amount (convert both to Decimal for precision)
            discount_amount = (discount_percentage / Decimal(100)) * total
            new_total = total - discount_amount + shipping

            # Update the used_count for the coupon
            coupon.used_count += 1
            coupon.save()
            
            return JsonResponse({
                'success': True,
                'new_total': new_total,
            })
        except Coupon.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Invalid coupon code.'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request'})

def save_shipping_address(request): 
    if request.method == 'POST':
        # Get the data from the request body
        data = json.loads(request.body)
        razorpay_payment_id = data.get('razorpay_payment_id')
        total = data.get('total')
        print(data)
        
        # Check if the user is logged in
        if request.user.is_authenticated:
            # If logged in, associate the address with the current user
            user = request.user
            order, created = Order.objects.get_or_create(customer=user, complete=False)
        
        else:
            user,order = guestOrder(request,data)

        
        order_items = OrderItem.objects.filter(order=order)
        for order_item in order_items:
            order_item.order_status = 'Placed'
            order_item.save()
        order.transaction_id = razorpay_payment_id
        order.payment_method = 'Razorpay'
        order.complete = True
        order.total = total
        order.save()
        
        # Save the shipping address details (assuming you have a ShippingAddress model)
        shipping_address = ShippingAddress(
            customer=user,
            order = order,
            doorno=data['doorno'],
            street=data['street'],
            apart=data['apart'],
            city=data['city'],
            state=data['state'],
            pincode=data['pincode']
        )
        shipping_address.save()

        # Assuming cart is stored in the user's session, clear it
        # request.session['cart'] = {}  # Clear the cart session variable

        return JsonResponse({"success": True})
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def myorders(request):
    datas = cartData(request)
    items = datas['items']
    order = datas['order']
    cartitems = datas['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()
    # Fetch all completed orders for the logged-in user
    orders = Order.objects.filter(customer=request.user, complete=True)

    # If orders exist, get all order items related to those orders
    if orders.exists():
        myorder = OrderItem.objects.filter(order__in=orders)  # Fetch all OrderItems related to the orders
    else:
        myorder = None  # or you can pass an empty list if you prefer

    return render(request, 'orders.html', {'categories': categories,'data': myorder,'items':items,'order':order, 'cartitems': cartitems,'favcount':favcartitems})

def save_cod_shipping_address(request): 
    if request.method == 'POST':
        # Get the data from the request body
        data = json.loads(request.body)
        total = data.get('total')
        print(data)
        
        # Check if the user is logged in
        if request.user.is_authenticated:
            # If logged in, associate the address with the current user
            user = request.user
            order, created = Order.objects.get_or_create(customer=user, complete=False)

        else:
            user,order = guestOrder(request,data)

        order_items = OrderItem.objects.filter(order=order)
        for order_item in order_items:
            order_item.order_status = 'Placed'
            order_item.save()
        order.payment_method = 'Cash On Delivery'
        order.complete = True
        order.total = total
        order.save()
        
        # Save the shipping address details (assuming you have a ShippingAddress model)
        shipping_address = ShippingAddress(
            customer=user,
            order = order,
            doorno=data['doorno'],
            street=data['street'],
            apart=data['apart'],
            city=data['city'],
            state=data['state'],
            pincode=data['pincode']
        )
        shipping_address.save()

        # Assuming cart is stored in the user's session, clear it
        # request.session['cart'] = {}  # Clear the cart session variable

        return JsonResponse({"success": True})
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def tracking(request,id):
    datas = cartData(request)
    items = datas['items']
    order = datas['order']
    cartitems = datas['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()

    orderItem = OrderItem.objects.filter(id = id).first()
    #print(orderItem)
    return render(request,'tracking.html',{'categories': categories,'item':orderItem,'items':items,'order':order, 'cartitems': cartitems,'favcount':favcartitems})


def bestseller(request):
    datas = cartData(request)
    items = datas['items']
    order = datas['order']
    cartitems = datas['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()

    products =  Product.objects.filter(best=True)
    return render(request,'bestseller.html',{'categories': categories,'products':products,'items':items,'order':order, 'cartitems': cartitems,'favcount':favcartitems})

def newproducts(request):
    datas = cartData(request)
    items = datas['items']
    order = datas['order']
    cartitems = datas['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()

    fifteen_days_ago = date.today() - timedelta(days=10)
    products = Product.objects.filter(date__gte=fifteen_days_ago)
    return render(request,'newproducts.html',{'categories': categories,'products':products,'items':items,'order':order, 'cartitems': cartitems,'favcount':favcartitems})

def featuredproducts(request):
    datas = cartData(request)
    items = datas['items']
    order = datas['order']
    cartitems = datas['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()

    products =  Product.objects.filter(featured=True)
    return render(request,'featuredproducts.html',{'categories': categories,'products':products,'items':items,'order':order, 'cartitems': cartitems,'favcount':favcartitems})

def Search(request):
    datas = cartData(request)
    items = datas['items']
    order = datas['order']
    cartitems = datas['cartitems']
    favdata = favcartData(request)
    favcartitems = favdata['favcartitems']
    categories = Category.objects.all()
    if request.method == 'POST':
        keyword = request.POST.get('keyword')

        if keyword:
            category = Category.objects.filter(name__icontains=keyword)
        # sort_option = request.POST.get('sort', '')
            
            if category.exists():
                print('if Executed')
                searchproducts = Product.objects.filter(category__in=category)
            else:
                print('Else Executed')
                searchproducts = Product.objects.filter(name__icontains=keyword)
        
        #  # Apply sorting based on the sort option
        # if sort_option == 'low_to_high':
        #     products = products.order_by('selling_price')  # Sort low to high
        # elif sort_option == 'high_to_low':
        #     products = products.order_by('-selling_price')  # Sort high to low
        return render(request,'search.html',{'keyword':keyword,'searchproducts':searchproducts,'categories': categories,'items':items,'order':order, 'cartitems': cartitems,'favcount':favcartitems})
    
def add_subscriber(request):
    if request.method == 'POST':
        sub_mail = request.POST.get('mail')
        print(sub_mail)

        subscriber = subscribers.objects.filter(subscriber_email=sub_mail).first()  # Get the first matching subscriber
        
        if subscriber:
            subscriber.subscribed = True
            subscriber.save()  # Save the updated instance
        else:
            new_subscriber = subscribers.objects.create(subscriber_email=sub_mail, subscribed=True)
            new_subscriber.save()
        return redirect('/')

def remove_subscriber(request):
    if request.method == 'POST':
        sub_mail = request.POST.get('mail')
        print(sub_mail)

        subscriber = subscribers.objects.filter(subscriber_email=sub_mail).first()  # Get the first matching subscriber
        
        if subscriber:
            subscriber.subscribed = False
            subscriber.save()  # Save the updated instance
        return redirect('/')

def orderreview(request,pid):
    review_form = ReviewForm()
    product = Product.objects.get(id=pid)
    user = request.user

    if request.method == 'POST':
        reviewcontent = request.POST['review']
        ratings = request.POST['rating']
        review = Review.objects.create(
            product=product,
            user=user,
            review=reviewcontent,
            rating=ratings
        )
        return redirect('orders')
    return render(request,'orderreview.html',{'review_form':review_form,'id':pid})

