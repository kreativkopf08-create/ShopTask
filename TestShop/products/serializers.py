from rest_framework import serializers
from .models import Product, Category, Tag

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'created_at', 'category_name', 'tags']

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

class ProductExportSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category')
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'created', 'category', 'tags']

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]