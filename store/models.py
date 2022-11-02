
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation', related_name='books')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)
    
    def __str__(self):
        return f'Id {self.id}: {self.name}'

class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1, 'Waste of time'),
        (2, 'Hard to read'),
        (3, 'Good'),
        (4, 'Must read'),
        (5, 'Best')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)
    
    def __str__(self):
        return f'{self.user.username}: {self.book.name}, RATE: {self.rate}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_rating = self.rate

    def save(self, *args, **kwargs):
        from store.calculate import set_rating

        creating = not self.pk
        
        
        super().save(*args, **kwargs)
        new_rating = self.rate

        if self.old_rating != new_rating or creating:
            set_rating(self.book)