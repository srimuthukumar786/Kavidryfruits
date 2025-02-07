from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from shortuuid.django_fields import ShortUUIDField
from django.utils.text import slugify
from django.utils import timezone
import datetime
import os
import shortuuid

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self,email,password,**extra_fields):
        if not email:
            raise ValueError('Email is not given')
        email = self.normalize_email(email)
        user = self.model(email = email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff = True')
        
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser = True')
        
        return self.create_user(email,password,**extra_fields)
        

class CustomUser(AbstractBaseUser):
    email = models.EmailField(max_length=254,unique=True)
    password = models.CharField(max_length=254,null=False)
    first_name = models.CharField(max_length=255,null=False,blank=False)
    last_name = models.CharField(max_length=255,null=False,blank=False)
    mobile = models.CharField(max_length=15,null=True,blank=False,unique=True)
    is_email_verified = models.BooleanField(default=False)
    otp = models.IntegerField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name
    
    def has_module_perms(self,app_label):
        return True
    
    def has_perm(self,perm,obj=None):
        return True
    
    def get_all_permissions(self, obj=None):
        # Implement logic to get all permissions for this user
        return []
    

STATUS =(
    ("Published", "Published"),
    ("Draft", "Draft"),
    ("Disabled", "Disabled")
)

PAYMENT_STATUS =(
    ("Paid", "Paid"),
    ("Processing", "Processing"),
    ("Failed", "Failed")
)

PAYMENT_METHOD =(
    ("Cash On Delivery", "Cash On Delivery"),
    ("Razorpay", "Razorpay"),
)

ORDER_STATUS =(
    ("Processing","Processing"),
    ("Placed", "Placed"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
    ("Cancelled", "Cancelled"),
)

RATING = (
    (1, "⭐"),       # 1 star
    (2, "⭐⭐"),      # 2 stars
    (3, "⭐⭐⭐"),     # 3 stars
    (4, "⭐⭐⭐⭐"),    # 4 stars
    (5, "⭐⭐⭐⭐⭐"),   # 5 stars
)

def getFilename(request, filename):
    now_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # Fix the time formatting (remove colon)
    new_file = '%s%s' % (now_time, filename)
    return os.path.join('Media/', new_file)

class Category(models.Model):
    name = models.CharField(max_length=150, null=True, blank=True)
    image = models.ImageField(upload_to=getFilename,null=True, blank=True)
    slug = models.SlugField(unique=True)
    

    def __str__(self):
        return self.name

    @property
    def Imageurl(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    def compress_image(self):
        """Compress the image to reduce file size."""
        img = Image.open(self.image)

         # Convert the image to RGB mode if it's in a different mode like P (indexed color)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize image (optional, to a maximum size, e.g., 1024x1024)
        img.thumbnail((1024, 1024))

        # Create a BytesIO object to save the compressed image
        temp_image = BytesIO()
        img.save(temp_image, format='JPEG', quality=75, optimize=True)
        temp_image.seek(0)

        # Save the compressed image to the file storage
        self.image.save(self.image.name, ContentFile(temp_image.read()), save=False)
    
    def save(self, *args, **kwargs):
        """Override the save method to compress image before saving."""
        if self.image:
            self.compress_image()
        super().save(*args, **kwargs)


    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

def get_current_time():
    return timezone.now()

class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to=getFilename,null=True, blank=True)
    image2 = models.ImageField(upload_to=getFilename,null=True, blank=True)
    description = models.CharField(max_length=1000)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True,blank=True,related_name='products')
    price1 = models.DecimalField(max_digits=12, decimal_places=2,default=0.00,null=True, blank=True,verbose_name="Sale Price 100g")
    price2 = models.DecimalField(max_digits=12, decimal_places=2,default=0.00,null=True, blank=True,verbose_name="Sale Price 250g")
    price3 = models.DecimalField(max_digits=12, decimal_places=2,default=0.00,null=True, blank=True,verbose_name="Sale Price 500g")
    price4 = models.DecimalField(max_digits=12, decimal_places=2,default=0.00,null=True, blank=True,verbose_name="Sale Price 1kg")
    discount = models.DecimalField(max_digits=12,decimal_places=2,default=0.00,null=True,blank=True)
    stock = models.BooleanField(default=False,help_text="0-show,1-Hidden")
    status = models.CharField(max_length=20, choices=STATUS, default="Published")
    featured = models.BooleanField(default=False, verbose_name="Special product")
    best = models.BooleanField(default=False, verbose_name="Best Seller")
    trending = models.BooleanField(default=False, verbose_name="Trending")
    sku = ShortUUIDField(unique=True, max_length=50,length=5,prefix="SKU",alphabet="1234567890" )
    slug = models.SlugField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Products"
        ordering = ["-id"]


    def __str__(self):
        return self.name

    def average_rating(self):
        return Review.objects.filter(product=self).aggregate(avg_rating=models.Avg('rating')) ['avg_rating']

    def reviews(self):
        return Review.objects.filter(product=self)

    def gallery(self):
        return Gallery.objects.filter(product=self)
    
    @property
    def getPrice1(self):
        try:
            price = round(self.price1-(self.price1/100*self.discount))
        except:
            price = self.price1
        return price
    
    @property
    def getPrice2(self):
        try:
            price = round(self.price2-(self.price2/100*self.discount))
        except:
            price = self.price2
        return price
    @property
    def getPrice3(self):
        try:
            price = round(self.price3-(self.price3/100*self.discount))
        except:
            price = self.price3
        return price
    @property
    def getPrice4(self):
        try:
            price = round(self.price4-(self.price4/100*self.discount))
        except:
            price = self.price4
        return price
    
    @property
    def Imageurl(self):
        try:
            url=self.image.url
        except:
            url=''
        return url
    
    def compress_image(self,):
        """Compress the image to reduce file size."""
        img = Image.open(self.image)

         # Convert the image to RGB mode if it's in a different mode like P (indexed color)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize image (optional, to a maximum size, e.g., 1024x1024)
        img.thumbnail((1024, 1024))

        # Create a BytesIO object to save the compressed image
        temp_image = BytesIO()
        img.save(temp_image, format='JPEG', quality=75, optimize=True)
        temp_image.seek(0)

        # Save the compressed image to the file storage
        self.image.save(self.image.name, ContentFile(temp_image.read()), save=False)
    
    def save(self, *args, **kwargs):
        """Override the save method to compress image before saving."""
        if self.image:
            self.compress_image()

        if not self.slug:
            self.slug = slugify(self.name)+ "-" +str(shortuuid.uuid().lower()[:2])

        super(Product, self).save(*args, **kwargs)


class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name="product_images",null=True, blank=True)
    image = models.ImageField(upload_to=getFilename)
    gallery_id = ShortUUIDField(max_length=10,length=6,alphabet="1234567890" )
  

    def _str_(self):
        return f"{self.product.name} - image"

    class Meta:
        verbose_name_plural = "Gallery"


class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,null=True,blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,null=True,blank=True,related_name='reviews')
    review = models.TextField(null=True,blank=True)
    reply = models.TextField(null=True,blank=True)
    rating = models.IntegerField(choices=RATING,default=4)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True) 

    def _str_(self):
        return f"{self.user.email} review on {self.product.name}"
    
class Favorite(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    customer=models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True,blank=True)
    date_ordered=models.DateTimeField(auto_now_add=True)
    complete=models.BooleanField(null=True,blank=False,default=False)
    transaction_id=models.CharField(max_length=50,null=True)
    total=models.DecimalField(max_digits=12, decimal_places=2,default=0.00,null=True, blank=True)
    payment_method=models.CharField(choices=PAYMENT_METHOD,max_length=200,null=True)
    def __str__(self):
        return str(self.id)


    @property
    def get_cart_total(self):
        orderitems=self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_items(self):
        orderitems=self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    
    @property
    def get_cart_weight(self):
        orderitems=self.orderitem_set.all()
        total = sum([item.get_weight for item in orderitems])
        return total

    @property
    def get_cart(self):
        total = self.orderitem_set.count()
        return total
 
class OrderItem(models.Model):
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=True)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,null=True,blank=True)
    size=models.CharField(max_length=10,null=True,blank=True)
    quantity=models.IntegerField(default=0,null=True,blank=True)
    price = models.FloatField(null=True,blank=True)
    date_added=models.DateTimeField(auto_now_add=True)
    order_status=models.CharField(choices=ORDER_STATUS,max_length=200,default='Processing',null=True)


    @property
    def get_total(self):
        if self.product:
            total = self.price * self.quantity
            return total
        return 0
    
    @property
    def get_weight(self):
        if self.product:
            total = int(self.size) * self.quantity
            return total
        return 0

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)  # Coupon code
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # Discount percentage
    max_usage = models.PositiveIntegerField()  # Max number of uses
    used_count = models.PositiveIntegerField(default=0)  # How many times the coupon has been used
    expiration_date = models.DateTimeField(null=True, blank=True)  # Optional expiration date
    
    def __str__(self):
        return self.code
    
class ShippingAddress(models.Model):
    customer=models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True,blank=True)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
    doorno=models.CharField(max_length=25,null=False)
    street = models.CharField(max_length=100,null=False)
    apart = models.CharField(max_length=100,null=True)
    city=models.CharField(max_length=100,null=True)
    state=models.CharField(max_length=100,null=True)
    pincode=models.CharField(max_length=50,null=True)
    date_added=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

class subscribers(models.Model):
    subscriber_email = models.CharField(max_length=100,null=False,blank=False,unique=True)
    subscribed = models.BooleanField(default=False)

    def __str__(self):
        return self.subscriber_email