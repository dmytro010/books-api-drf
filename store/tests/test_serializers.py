
from django.test import TestCase
from store.serializers import BooksSerializer
from store.models import Book, UserBookRelation
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username="user1", first_name="user1", last_name="user_1")
        user2 = User.objects.create(username="user2", first_name="user2", last_name="user_2")
        user3 = User.objects.create(username="user3", first_name="user3", last_name="user_3")

        book_1 = Book.objects.create(name="Test book 1", price=23.32, author_name='Author 1', owner=user1)
        book_2 = Book.objects.create(name="Test book 2", price=10, author_name='Author 2')
        
        UserBookRelation.objects.create(user=user1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True, rate=5)
        user_book_3 = UserBookRelation.objects.create(user=user3, book=book_1, like=True)
        user_book_3.rate = 4
        user_book_3.save()

        UserBookRelation.objects.create(user=user1, book=book_2, like=False, rate=5)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))).order_by("id")
        data = BooksSerializer(books, many=True).data

        expected_data = [
            {
            'id': book_1.id,
            'name': 'Test book 1',
            'price': '23.32',
            'author_name': 'Author 1',
            'annotated_likes': 3,
            'rating': '4.67',
            'owner_name': 'user1',
            'readers': [
                {
                    'first_name': 'user1',
                    'last_name': 'user_1'
                },
                {
                    'first_name': 'user2',
                    'last_name': 'user_2'
                },
                {
                    'first_name': 'user3',
                    'last_name': 'user_3'
                }
            ]
        },
         {
            'id': book_2.id,
            'name': 'Test book 2',
            'price': '10.00',
            'author_name': 'Author 2',
            'annotated_likes': 1,
            'rating': '4.00',
            'owner_name': '',
            'readers': [
                {
                    'first_name': 'user1',
                    'last_name': 'user_1'
                },
                {
                    'first_name': 'user2',
                    'last_name': 'user_2'
                },
                {
                    'first_name': 'user3',
                    'last_name': 'user_3'
                }
            ]
            
        },
        ]
        print("DATA", data)
        print("EXPECTED", expected_data)
        self.assertEqual(expected_data, data)
 

