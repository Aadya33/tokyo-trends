from django.contrib import admin
from .models import (
    Product,
    ProductImage,
    ProductSize,
    Client,
    Review,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 9


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "sale_price",
        "discount_percentage",
        "created_at",
    )

    list_filter = (
        "category",
    )

    search_fields = (
        "name",
        "description",
    )

    inlines = [
        ProductImageInline,
        ProductSizeInline,
    ]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "client",
        "rating",
        "verified_purchase",
        "created_at",
    )

    list_filter = (
        "rating",
        "verified_purchase",
    )

    search_fields = (
        "product__name",
        "comment",
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "mobile",
        "email",
        "created_at",
    )

    search_fields = (
        "mobile",
        "email",
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "position",
    )


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "size",
        "stock",
    )

    list_filter = (
        "size",
    )