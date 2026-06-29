from rest_framework.pagination import PageNumberPagination


class BasePagination(PageNumberPagination):
    """Default pagination shared across the API endpoints.

    Clients can override the page size with the ``page_size`` query
    parameter, up to ``max_page_size`` to protect the database from
    unbounded result sets on very large tables.
    """

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
