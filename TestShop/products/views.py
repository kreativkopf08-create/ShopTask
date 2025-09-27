from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Product
from .serializers import ProductExportSerializer, ProductSerializer
import openpyxl
from io import BytesIO
from django.http import HttpResponse

class ProductListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.select_related('category').prefetch_related('tags')
    serializer_class = ProductSerializer
    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ProductExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = 'product_export_data'
        cached_data = cache.get(cache_key)
        if cached_data is None:
            products = Product.objects.select_related('category').prefetch_related('tags')
            serializer = ProductExportSerializer(products, many=True)
            cached_data = serializer.data
            cache.set(cache_key, cached_data, timeout=60 * 15)
        else:
            products = Product.objects.select_related('category').prefetch_related('tags')

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Products"
        headers = ['ID', 'Name', 'Description', 'Price', 'Created', 'Category Name', 'Tags']
        ws.append(headers)

        for product in cached_data:
            ws.append([
                product['id'],
                product['name'],
                product['description'],
                float(product['price']),
                product['created'],
                product['category_name'],
                ', '.join(product['tags'])
            ])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="products_export.xlsx"'
        return response