from django.contrib import admin
from .models import Product,Variation,ReviewRating,ProductGallery
# Register your models here.
import admin_thumbnails 
@admin_thumbnails.thumbnail('image')
class ProductGelleryInline(admin.TabularInline):
    model=ProductGallery
    extra = 1



class ProductAdmin(admin.ModelAdmin):
    list_display=('product_name','price','stock','category','modified_date','is_available')
    prepopulated_fields={'slug':('product_name',)}
    inlines=[ProductGelleryInline]
admin.site.register(Product,ProductAdmin)
class VariationAdmin(admin.ModelAdmin):
    list_display=('product','variation_category','variation_value','is_activate','create_date')
    list_editable = ('is_activate',)
    list_filter=('product','variation_category','variation_value')
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)