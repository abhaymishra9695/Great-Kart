from django.db import models
from category.models import Category
from django.urls import reverse
# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length = 150,unique=True)
    slug = models.SlugField(max_length = 150,unique=True)
    description = models.TextField(max_length=500,blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photo/product')
    stock = models.IntegerField()
    is_available=models.BooleanField(default=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)

    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])

    def __str__(self):
        return self.product_name
    
class VariationManager(models.Manager):
    def colors(self):
        return self.filter(variation_category='color', is_activate=True)
        # return super(Variation,self).filter(variation_value='size',is_activate=True)

    
    def sizes(self):
        return self.filter(variation_category='size', is_activate=True)



class Variation(models.Model):
    variation_category_choice=(
        ('color','color'),
        ('size','size'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length = 150,choices=variation_category_choice)
    variation_value = models.CharField(max_length = 150)
    is_activate = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now=True)

    objects=VariationManager()

    def __unicode__(self): # same as __str__(self) __unicode us for integer
        return self.product

    
    
    

    
    