Simple Rest api with Django Rest Framework and PostgreSQL.
Functionality: 
Rating, Likes, Bookmarks
Filter by price Search by Author and Title
Custom permission IsOwnerOrStaffOrReadOnly 
OAuth with Github.
Cashe rating.
Api unit tests.

PATHS:
__debug__/
admin/
api-auth/
login/<str:backend>/ [name='begin']
complete/<str:backend>/ [name='complete']
disconnect/<str:backend>/ [name='disconnect']
disconnect/<str:backend>/<int:association_id>/ [name='disconnect_individual']
auth/ [name='auth']
^book/$ [name='book-list']
^book/(?P<pk>[^/.]+)/$ [name='book-detail']
^book_relation/(?P<book>[^/.]+)/$ [name='userbookrelation-detail']

Deployed on server with Nginx and Gunicorn.
http://185.235.218.164/

