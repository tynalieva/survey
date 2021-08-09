from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Category(models.Model):
    slug = models.SlugField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='categories', blank=True, null=True)
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        if self.parent:
            return self.name
        return self.name

    @property
    def get_children(self):
        if self.children:
            return self.children.all()
        return False


class Post(models.Model):
    CHOICES = [
        ('Chui', 'Чуйская область'),
        ('Issykkul', 'Иссык-Кульская область'),
        ('Naryn', 'Нарынская область'),
        ('Talas', 'Таласская область'),
        ('Jalalabat', 'Джалал-Адабская область'),
        ('Osh', 'Ошская область'),
        ('Batken', 'Баткенская область'),
    ]
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    region = models.CharField(choices=CHOICES, max_length=50)
    address = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    @property
    def get_image(self):
        return self.images.first()


class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return self.image.url


class Comment(models.Model):
    owner = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.owner}-->{self.post}'


class Rating(models.Model):
    VALUE = (
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rating')
    rating_field = models.CharField(choices=VALUE, max_length=1, default=0)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="rating")

    def __str__(self):
        return f"{self.rating_field} - {self.post}"

    class Meta:
        unique_together = ['owner', 'post']
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'


class Like(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    likes = models.BooleanField(default=False)

    class Meta:
        unique_together = ['owner', 'post']

    def str(self):
        return f'{self.owner} liked this ad: {self.likes}'


class Favorites(models.Model):
    owner = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favorites')
    favorites = models.BooleanField()

    class Meta:
        unique_together = ['owner', 'post']
