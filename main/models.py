from django import template
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()


class Category(models.Model):
    slug = models.SlugField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='categories', blank=True, null=True)
    description = models.TextField()
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

    def total_posts(self):
        return self.posts.count()


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
    like = models.ManyToManyField(User, related_name='post')

    class Meta:
        ordering = ('created_at', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    def total_likes(self):
        return self.like.count()

    @property
    def get_image(self):
        return self.images.first()

    def total_comments(self):
        return self.comments.count()

    def total_post(self):
        return self.owner.count()


class Image(models.Model):
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")

    def __str__(self):
        if self.image:
            return self.image.url
        return ' '


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


class Favorites(models.Model):
    owner = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favorites')
    favorites = models.BooleanField()

    class Meta:
        unique_together = ['owner', 'post']
