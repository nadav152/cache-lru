from api import views
from django.urls import include, path


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # url for the main API view page
    path('books/', views.BookViewSet.as_view(), name='books-creation'),
    path('books/<int:pk>/', views.BookViewSet.as_view(), name='book-detail'),
]
