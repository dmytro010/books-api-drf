import json
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer
from django.contrib.auth.models import User
from rest_framework.exceptions import ErrorDetail
from django.db.models import Count, Case, When, Avg
from django.test.utils import CaptureQueriesContext
from django.db import connection



class BooksApiTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.book_1 = Book.objects.create(name="Test book 1", price=10,
        author_name="Author 1", owner=self.user)
        self.book_2 = Book.objects.create(name="Test book 2", price=23.32,
        author_name="Author 2")
        self.book_3 = Book.objects.create(name="Test book 3 by Author 1", price=23.32,
        author_name="Author 2")
        UserBookRelation.objects.create(user=self.user, book=self.book_1, like=True, rate=5)
        

    def test_get(self):
        
        url = reverse('book-list')
        # print("url: ",url)
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            # print(response.data)
            self.assertEqual(2, len(queries))
            # print("queries: ", len(queries))
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))).order_by("id")
            
        serializer_data = BooksSerializer(books, many=True).data
        # print("++++++++++++SERIALIZER DATA+++++++++++++++++++++",serializer_data)
        # print("++++++++++++RESPONSE DATA+++++++++++++++++++++", response.data)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        # self.assertEqual(serializer_data[0]['likes_count'], 1)
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)
        print("response: ", response.data)
    
    def test_get_filter(self):
        
        url = reverse('book-list')
        # print("url: ",url)
        response = self.client.get(url, data={'price': 23.32})
        books = Book.objects.filter(id__in=[self.book_2.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))).order_by("id")
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # print("response: ", response.data)

    def test_get_search(self):
        
        url = reverse('book-list')
        print("url: ",url)
        response = self.client.get(url, data={'search':'Author 1'})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(
                userbookrelation__like=True, then=1)))).order_by("id")
        
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        print("response: ", response.data)
    
    def test_get_ordering(self):
        
        url = reverse('book-list')
        # print("url: ",url)
        response = self.client.get(url, data={'ordering':'-price'})
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))).order_by("-price")
        
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # print("response: ", response.data)

    def test_create(self):
        
        url = reverse('book-list')
        # print("url: ",url)
        books_count_before_creation = Book.objects.all().count()

        self.client.force_login(self.user)
        data = {"name": "Fluent Python: Clear, Concise, and Effective Programming 1st Edition",
                "price": 43.99,
                "author_name": "Luciano Ramalho", 'annotated_likes': 0    
                }

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type="application/json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        # print("response: ", response.data)
        self.assertEqual(books_count_before_creation+1, Book.objects.all().count())
        # print(Book.objects.last().owner)
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        
        url = reverse('book-detail', args=(self.book_1.id,))
       
        self.client.force_login(self.user)
        data = {"name": self.book_1.name,
                "price": 109,
                "author_name": self.book_1.author_name  
                }

        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type="application/json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # print("response: ", response.data)
        # self.book_1 = Book.objects.get(id=self.book_1.id)
        self.book_1.refresh_from_db()
        self.assertEqual(109, self.book_1.price)
    
    def test_delete(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        deleted_book_id = self.book_1.id
    
        self.client.force_login(self.user)
       
        response = self.client.delete(url)
        
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        # print("response: ", response.data)
        self.assertFalse(Book.objects.filter(id=deleted_book_id).exists())
      
        
    def test_get_detail(self):
        
        url = reverse('book-detail', args=(self.book_2.id,))
        response = self.client.get(url)
        books = Book.objects.filter(id=self.book_2.id).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))).order_by("id")[0]
        
        serializer_data = BooksSerializer(books).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # print("response: ", response.data)
        # print("serializer: ", serializer_data)


    """Negative tests"""   
    def test_update_not_owner(self):
        
        url = reverse('book-detail', args=(self.book_1.id,))
        self.user2 = User.objects.create(username='test_user2')
        self.client.force_login(self.user2)
        data = {"name": self.book_1.name,
                "price": 109,
                "author_name": self.book_1.author_name 
                }

        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type="application/json")
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        print("response: ", response.data)
        # self.book_1 = Book.objects.get(id=self.book_1.id)
        self.book_1.refresh_from_db()
        self.assertEqual(10, self.book_1.price)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')}, response.data)

    def test_update_not_owner_but_staff(self):
        
        url = reverse('book-detail', args=(self.book_1.id,))
        self.user2 = User.objects.create(username='test_user2', is_staff=True)
        self.client.force_login(self.user2)
        data = {"name": self.book_1.name,
                "price": 109,
                "author_name": self.book_1.author_name 
                }

        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type="application/json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # print("response: ", response.data)
        # self.book_1 = Book.objects.get(id=self.book_1.id)
        self.book_1.refresh_from_db()
        self.assertEqual(109, self.book_1.price)


"""BOOK_RELATION TESTS"""
class BooksRelationApiTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.user2 = User.objects.create(username='test_user2')
        self.book_1 = Book.objects.create(name="Test book 1", price=10,
        author_name="Author 1", owner=self.user)
        self.book_2 = Book.objects.create(name="Test book 2", price=23.32,
        author_name="Author 2")
        self.book_3 = Book.objects.create(name="Test book 3 by Author 1", price=23.32,
        author_name="Author 2")
        

    def test_like(self):
        
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        # print("url: ",url)
        data = {"like": True}
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type="application/json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.like)

        #TEST BOOKMARKS
        data = {"in_bookmarks": True}
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type="application/json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        # print("url: ",url)
        data = {"rate": 5}
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type="application/json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(5, relation.rate)
    
    """Negative tests"""
    def test_rate_negative(self):
        
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        # print("url: ",url)
        data = {"rate": 6}
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type="application/json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
       

        
     
