from django.contrib import admin
from .models import *

# Register your models here.
class GalleryInline(admin.TabularInline):
    model = Gallery



class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','image']
    list_editable = ['image']
    prepopulated_fields = {'slug':('name',)}

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','category','price1','price2','price3','price4','discount','status','featured','date']
    search_fields = ['name','category__name']
    list_filter = ['status','featured','category']
    inlines = [GalleryInline]
    prepopulated_fields = {'slug':('name',)}


class GalleryAdmin(admin.ModelAdmin):
    list_display = ['product','gallery_id']
    search_fields = ['product__name','gallery_id']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user','product','rating','active','date']
    search_fields = ['user_username','product_name']
    list_filter = ['active','rating']

class OrderList(admin.ModelAdmin):
    list_display=('id','complete','total','transaction_id','payment_method')

class OrderItemList(admin.ModelAdmin):
    list_display=('product','order','size','quantity','price','order_status')

class FavoriteItemList(admin.ModelAdmin):
    list_display = ('product','created_at')

class ShippingAdrList(admin.ModelAdmin):
    list_display = ('customer','doorno','street','city','pincode')

class SubscriberList(admin.ModelAdmin):
    list_display = ('subscriber_email','subscribed')

admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Gallery,GalleryAdmin)
admin.site.register(Review,ReviewAdmin)
admin.site.register(CustomUser)
admin.site.register(Favorite,FavoriteItemList)
admin.site.register(Order,OrderList)
admin.site.register(OrderItem,OrderItemList)
admin.site.register(Coupon)
admin.site.register(ShippingAddress,ShippingAdrList)
admin.site.register(subscribers,SubscriberList)