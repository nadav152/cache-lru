from api.serializers import BookSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponseNotFound
from api.models import Book
from api.cache import Cache
from typing import Union
from api.constants import LOGGER, BOOK_DELETED, CREATED_BOOK
import logging

book_cache = Cache(size=3, default_ttl=60)
logger = logging.getLogger(LOGGER)


class BookViewSet(APIView):
    """
    APIView is a DRF build-in view class which help us handle CRUD actions.
    This class can integrate and make use of DRF packages.
    """

    def post(self, request):
        try:
            serializer = BookSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info(CREATED_BOOK)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as err:
            self.log_general_exception(err)
            return Response(err)

    def get(self, request, pk=None):
        try:
            book = self.get_book(pk)
            # add book to cache will renew its TTL if already in cache
            book_cache.set_object(pk, book)
            serializer = BookSerializer(book)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Book.DoesNotExist as err:
            self.log_failed_get_book(pk, err)
            return HttpResponseNotFound(err)

        except Exception as err:
            self.log_general_exception(err)
            return Response(err)

    def delete(self, request, pk):
        try:
            book = self.get_book(pk)
            book_cache.remove_object(pk)
            book.delete()
            return Response(BOOK_DELETED, status=status.HTTP_204_NO_CONTENT)

        except Book.DoesNotExist as err:
            self.log_failed_get_book(pk, err)
            return HttpResponseNotFound(err)

        except Exception as err:
            self.log_general_exception(err)
            return Response(err)

    def get_book_from_db(self, pk):
        return Book.objects.get(pk=pk)

    def get_book(self, pk: int) -> Union[Book, None]:
        """
        This function is retrieving a book by its ID.
        If successful it will be returned from the cache, else from DB.
        """
        book = book_cache.get_object(pk)

        if book is None:
            book = self.get_book_from_db(pk)

        return book

    def log_general_exception(self, err):
        return logger.error(f"[CREATE BOOK EXCEPTION] Error: {err}")

    def log_failed_get_book(self, pk, err):
        return logger.error(f"[FAILED GET BOOK] Book ID: {pk} | Error: {err}")
