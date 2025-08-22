from django.db import models
from restaurant.models import Restaurant
from django.utils.text import slugify

# Create your models here.


class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='categories')
    Category_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    image = models.ImageField(upload_to='media/category_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.Category_name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.Category_name
