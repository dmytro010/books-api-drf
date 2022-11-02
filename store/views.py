
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .permissions import IsOwnerOrStaffOrReadOnly
from rest_framework import filters
from store.serializers import BooksSerializer, UserBookRelationsSerializer
from django.shortcuts import render
from .models import Book, UserBookRelation
from rest_framework.mixins import UpdateModelMixin
from django.db.models import Count, Case, When


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(
        annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))).select_related("owner")\
        .prefetch_related('readers')\
        .only('name', 'price', 'author_name', 'owner__username', 'readers__username', 'rating', \
             'readers__first_name', 'readers__last_name').order_by("id")
    serializer_class = BooksSerializer
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['price']
    search_fields = ['name', 'author_name']
    ordering_fields = ['price', 'author_name']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()

class UserBookRelationViewSet(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationsSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, created = UserBookRelation.objects.get_or_create(user=self.request.user,
                                                            book_id=self.kwargs['book'])
        #print("created", created)
      
        return obj

    




def auth(request):
    return render(request, "oauth.html")