# products/serializers.py
from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """
    Basic serializer for Category.
    Used for listing and detail views.
    """

    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "slug", "product_count", "created_at"]
        read_only_fields = ["slug", "created_at"]

    def get_product_count(self, obj):
        """
        Custom method field - counts products in this category
        Method name must be: get_<field_name>
        """
        return obj.products.filter(is_active=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """
    Minimal info for product lists.
    Used in: GET /api/products/
    """

    category_name = serializers.CharField(source="category.name", read_only=True)
    seller_name = serializers.CharField(source="seller.username", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "stock",
            "image",
            "category_name",
            "seller_name",
            "is_in_stock",
            "created_at",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Full product info with nested relationships.
    Used in: GET /api/products/<id>/
    """

    category = CategorySerializer(read_only=True)  # Nested serializer
    seller = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "stock",
            "image",
            "category",
            "seller",
            "is_active",
            "is_in_stock",
            "created_at",
            "updated_at",
        ]

    def get_seller(self, obj):
        """Return seller info without sensitive data"""
        return {
            "id": obj.seller.id,
            "username": obj.seller.username,
            "email": obj.seller.email,
        }


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Used for creating/updating products.
    Includes validation logic.
    Used in: POST /api/products/, PUT/PATCH /api/products/<id>/
    """

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "stock",
            "category",
            "image",
            "is_active",
        ]

    def validate_price(self, value):
        """
        Field-level validation for price.
        Method name must be: validate_<field_name>
        """
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_stock(self, value):
        """Field-level validation for stock"""
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value

    def validate(self, data):
        """
        Object-level validation (across multiple fields).
        This runs AFTER all field-level validations.
        """
        # Example: Check if category exists and is valid
        if "category" in data and not data["category"].name:
            raise serializers.ValidationError("Invalid category")

        return data
