from api.serializers import BookSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Book
from api.cache import BookCache

book_cache = BookCache(size=3, default_ttl=60)


class BookViewSet(APIView):
    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        if pk is None:
            return Response({"response": "PK is required"}, status=status.HTTP_400_BAD_REQUEST)

        book = book_cache.get_book(pk)
        if book is None:
            book = self.get_object(pk)
            book_cache.add_book(pk, book)

        serializer = BookSerializer(book)
        return Response(serializer.data)

    def delete(self, request, pk):
        book = book_cache.get_book(pk)
        if book is None:
            book = self.get_object(pk)

        book_cache.remove_book(pk)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        return Book.objects.get(pk=pk)
