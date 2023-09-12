from django.db import models
from category.models import Category
from django.urls import reverse
from account.models import *
from django.db.models import Avg,Count

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

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def countreview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    
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

    
    
    
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    subject = models.CharField(max_length = 100,blank=True)
    review=models.TextField(max_length=100)
    rating = models.FloatField()
    ip = models.CharField(max_length = 150)
    status=models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

class ProductGallery(models.Model):
    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'  # Corrected attribute name


    def __str__(self):
        return self.product.product_name
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)


    
    
    